import asyncio, json, os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

from agent.planner     import Planner
from agent.executor    import Executor
from agent.memory      import Memory
from agent.scheduler   import Scheduler
from voice.stt         import SpeechToText
from voice.tts         import TextToSpeech
from mcp.tool_registry import ToolRegistry
from tools.api_tools   import get_news_articles, get_breaking_news, get_daily_digest, NEWS_CATEGORIES

# ── Temporal flag ──────────────────────────────────────────────────────────────
_temporal_ok = False

# ── Active WebSocket clients (for push notifications) ─────────────────────────
_ws_clients: list = []

# ── Notification settings ──────────────────────────────────────────────────────
_notif_settings = {
    "enabled": True,
    "categories": ["technology", "health", "finance", "world", "india"],
    "interval_minutes": 30,
    "popup": True,
}
_last_notif_time = 0.0

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

async def _news_push_loop():
    """Background task: push breaking news to all WS clients periodically."""
    import time
    global _last_notif_time
    await asyncio.sleep(10)  # wait for server to fully start
    while True:
        interval = _notif_settings.get("interval_minutes", 30) * 60
        await asyncio.sleep(interval)
        if not _notif_settings.get("enabled") or not _ws_clients:
            continue
        try:
            cats = _notif_settings.get("categories", ["technology"])
            articles = await get_news_articles(cats[0] if cats else "technology", limit=3)
            if articles:
                payload = {"type": "news_notification", "articles": articles, "category": cats[0]}
                dead = []
                for ws in _ws_clients:
                    try:
                        await ws.send_json(payload)
                    except Exception:
                        dead.append(ws)
                for ws in dead:
                    _ws_clients.remove(ws)
        except Exception as e:
            print(f"[News Push] Error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _check_temporal()
    asyncio.create_task(_news_push_loop())
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


@app.get("/stats")
async def get_stats():
    import psutil, time
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    bat = psutil.sensors_battery()
    net = psutil.net_io_counters()
    return {
        "cpu": cpu,
        "ram": mem.percent,
        "ram_used_mb": mem.used // 1024 // 1024,
        "ram_total_mb": mem.total // 1024 // 1024,
        "battery": round(bat.percent) if bat else None,
        "charging": bat.power_plugged if bat else None,
        "net_sent_mb": round(net.bytes_sent / 1024 / 1024, 1),
        "net_recv_mb": round(net.bytes_recv / 1024 / 1024, 1),
    }


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
    _ws_clients.append(websocket)

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
    finally:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)


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


# ── News endpoints ─────────────────────────────────────────────────────────────

@app.get("/news/categories")
def news_categories():
    return {"categories": list(NEWS_CATEGORIES.keys())}


@app.get("/news/{category}")
async def news_by_category(category: str, limit: int = 8):
    articles = await get_news_articles(category, limit=limit)
    return {"category": category, "articles": articles}


@app.get("/news/digest/all")
async def news_digest():
    cats = _notif_settings.get("categories", ["technology", "health", "finance", "world", "india"])
    result = {}
    for cat in cats:
        result[cat] = await get_news_articles(cat, limit=4)
    return result


@app.get("/news/breaking/now")
async def breaking_news():
    from tools.api_tools import get_news_articles
    articles = await get_news_articles("world", limit=6)
    return {"articles": articles}


# ── Notification settings ──────────────────────────────────────────────────────

@app.get("/notifications/settings")
def get_notif_settings():
    return _notif_settings


@app.post("/notifications/settings")
async def update_notif_settings(settings: dict):
    _notif_settings.update(settings)
    return _notif_settings


@app.post("/notifications/push")
async def push_news_now():
    """Manually trigger a news push to all connected clients."""
    cats = _notif_settings.get("categories", ["technology"])
    pushed = 0
    for cat in cats[:3]:
        articles = await get_news_articles(cat, limit=2)
        if articles and _ws_clients:
            payload = {"type": "news_notification", "articles": articles, "category": cat}
            for ws in list(_ws_clients):
                try:
                    await ws.send_json(payload)
                    pushed += 1
                except Exception:
                    pass
    return {"pushed": pushed, "clients": len(_ws_clients)}

# Serve built React frontend
ui_dist = os.path.join(os.path.dirname(__file__), "ui", "dist")
if os.path.exists(ui_dist):
    app.mount("/", StaticFiles(directory=ui_dist, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
