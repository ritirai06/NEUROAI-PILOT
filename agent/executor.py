"""
Executor — runs each step from the plan, tracks context, handles errors.
"""
import asyncio
from typing import AsyncGenerator
from mcp.tool_registry import ToolRegistry


class Executor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        # Context state — persists across steps in a single plan
        self.context = {
            "current_app": None,
            "current_url": None,
            "last_action": None,
        }

    async def execute(self, plan: dict) -> dict:
        steps = plan.get("steps", [])
        results = []
        for step in steps:
            result = await self._run(step)
            results.append(result)
            if result["status"] == "error" and step.get("critical"):
                break
        return {"results": results, "summary": plan.get("summary", "Done")}

    async def execute_stream(self, plan: dict) -> AsyncGenerator[dict, None]:
        steps = plan.get("steps", [])
        for i, step in enumerate(steps):
            action = step.get("action", "unknown")
            params = step.get("params", {})
            yield {"index": i, "action": action, "params": params, "status": "running"}
            result = await self._run(step)
            yield {"index": i, "action": action, "params": params,
                   "status": result["status"], "output": result.get("output", "")}
            if result["status"] == "error" and step.get("critical"):
                yield {"index": i, "status": "aborted", "output": result.get("output")}
                return

    async def _run(self, step: dict) -> dict:
        action = step.get("action")
        params = step.get("params", {})

        if not action:
            return {"status": "error", "output": "No action specified"}

        fn = self.registry.get(action)
        if not fn:
            return {"status": "error", "output": f"Unknown action: '{action}'"}

        # Skip open_app if app already running (context check)
        if action == "open_app":
            app = params.get("app", "")
            if self.context.get("current_app") == app:
                return {"status": "skipped", "output": f"{app} already open"}

        # Browser actions get longer timeout, API calls get 12s, others 30s
        if action in ("open_website", "search_youtube", "click_first_video", "search_google", "click_button", "click"):
            timeout = 30.0
        elif action in ("open_app", "run_command", "take_screenshot", "open_camera", "click_photo"):
            timeout = 20.0
        else:
            timeout = 12.0

        try:
            if asyncio.iscoroutinefunction(fn):
                output = await asyncio.wait_for(fn(**params), timeout=timeout)
            else:
                output = await asyncio.wait_for(asyncio.to_thread(fn, **params), timeout=timeout)

            self._update_context(action, params, output)
            return {"status": "success", "output": output}

        except asyncio.TimeoutError:
            return {"status": "error", "output": f"{action} timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def _update_context(self, action: str, params: dict, output: str):
        self.context["last_action"] = action
        if action == "open_app":
            self.context["current_app"] = params.get("app")
        elif action in ("open_website", "play_youtube", "search_google"):
            self.context["current_url"] = params.get("url") or params.get("query")
