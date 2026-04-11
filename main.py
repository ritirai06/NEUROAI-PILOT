import asyncio, json, os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from agent.planner     import Planner
from agent.executor    import Executor
from agent.memory      import Memory
from agent.scheduler   import Scheduler
from voice.stt         import SpeechToText
from voice.tts         import TextToSpeech
from mcp.tool_registry import ToolRegistry

# ── Temporal flag ──────────────────────────────────────────────────────────────
_temporal_ok = False

async def _check_temporal():
    global _temporal_ok
    try:
        from temporal.client import get_client
        await asyncio.wait_for(get_client(), timeout=3.0)
        _temporal_ok = True
        print("[NeuroAI] Temporal connected")
    except Exception:
        _temporal_ok = False
        print("[NeuroAI] Temporal not available - using direct executor")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await _check_temporal()
    yield

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="NeuroAI", version="3.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

memory    = Memory()
registry  = ToolRegistry()
planner   = Planner(memory=memory)
executor  = Executor(registry=registry)
stt       = SpeechToText()
tts       = TextToSpeech()
scheduler = Scheduler()


class ChatRequest(BaseModel):
    message: str
    voice_response: Optional[bool] = False

class ScheduleRequest(BaseModel):
    command: str
    cron: str


@app.get("/status")
async def status():
    return {"temporal": _temporal_ok, "ollama": True, "version": "3.0.0"}


@app.post("/chat")
async def chat(req: ChatRequest):
    plan    = await planner.plan(req.message)
    results = await executor.execute(plan)
    memory.save(req.message, plan, results)
    outputs  = [r.get("output", "") for r in results.get("results", []) if r.get("output")]
    response = "\n".join(str(o) for o in outputs) if outputs else plan.get("summary", "Done")
    if req.voice_response:
        tts.speak(response)
    return {"plan": plan, "results": results, "response": response}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send(data: dict):
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        while True:
            data       = json.loads(await websocket.receive_text())
            user_input = data.get("message", "")

            await send({"type": "status", "message": "Planning..."})
            plan = await planner.plan(user_input)
            await send({"type": "plan", "data": plan})

            outputs = []

            if _temporal_ok:
                try:
                    from temporal.client import run_plan_stream
                    async for step_result in run_plan_stream(plan):
                        await send({"type": "step", "data": step_result})
                        if step_result.get("status") in ("success", "done") and step_result.get("output"):
                            outputs.append(str(step_result["output"]))
                except Exception as e:
                    await send({"type": "status", "message": f"Temporal error: {e} - falling back"})
                    async for step_result in executor.execute_stream(plan):
                        await send({"type": "step", "data": step_result})
                        if step_result.get("status") in ("success", "done") and step_result.get("output"):
                            outputs.append(str(step_result["output"]))
            else:
                async for step_result in executor.execute_stream(plan):
                    await send({"type": "step", "data": step_result})
                    if step_result.get("status") in ("success", "done") and step_result.get("output"):
                        outputs.append(str(step_result["output"]))

            memory.save(user_input, plan, {})
            response = "\n".join(outputs) if outputs else plan.get("summary", "Done")
            await send({"type": "done", "message": response, "_input": user_input})

    except WebSocketDisconnect:
        pass


@app.get("/history")
def get_history():
    return memory.get_history()

@app.delete("/history")
def clear_history():
    memory.clear()
    return {"status": "cleared"}

@app.get("/tools")
def list_tools():
    return registry.list_tools()

@app.get("/context")
def get_context():
    return executor.context

@app.post("/voice/listen")
async def listen():
    import asyncio
    try:
        # Run blocking STT in thread so event loop stays free
        text = await asyncio.wait_for(
            asyncio.to_thread(stt.listen, 5),
            timeout=12.0
        )
        return {"text": text or "", "error": None}
    except asyncio.TimeoutError:
        return {"text": "", "error": "Recording timed out"}
    except Exception as e:
        return {"text": "", "error": str(e)}


@app.post("/voice/speak")
async def speak(req: dict):
    import asyncio
    text = req.get("text", "")
    if text:
        await asyncio.to_thread(tts.speak, text, True)
    return {"status": "ok"}

@app.post("/schedule")
def schedule_task(req: ScheduleRequest):
    scheduler.add_task(req.command, req.cron)
    return {"status": "scheduled", "command": req.command, "cron": req.cron}

@app.get("/schedules")
def get_schedules():
    return scheduler.list_tasks()

# Serve built React frontend
ui_dist = os.path.join(os.path.dirname(__file__), "ui", "dist")
if os.path.exists(ui_dist):
    app.mount("/", StaticFiles(directory=ui_dist, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
