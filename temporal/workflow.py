"""
Temporal Workflow — executes a JSON plan step by step.
Each step is a Temporal activity with retry + timeout.
"""
from datetime import timedelta
from typing import Any
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from temporal.activities import ACTIVITY_MAP


TASK_QUEUE = "neuroai-tasks"

# Non-critical actions — failure won't stop the workflow
NON_CRITICAL = {"open_website", "open_app", "wait", "respond"}

# Per-action timeouts (seconds)
ACTION_TIMEOUTS = {
    "open_website":      60,
    "search_youtube":    60,
    "click_first_video": 30,
    "search_google":     60,
    "open_app":          20,
    "open_camera":       15,
    "click_photo":       10,
    "get_weather":       15,
    "get_news":          15,
    "run_command":       30,
    "take_screenshot":   15,
    "send_email":        30,
    "scrape":            45,
}


@workflow.defn(name="NeuroAIPlan")
class NeuroAIPlanWorkflow:

    @workflow.run
    async def run(self, plan: dict) -> dict:
        steps   = plan.get("steps", [])
        summary = plan.get("summary", "Done")
        results = []

        for i, step in enumerate(steps):
            action = step.get("action", "")
            params = step.get("params", {}) or {}

            activity_fn = ACTIVITY_MAP.get(action)
            if not activity_fn:
                results.append({
                    "index":  i,
                    "action": action,
                    "status": "error",
                    "output": f"Unknown action: {action}",
                })
                continue

            timeout   = ACTION_TIMEOUTS.get(action, 45)
            is_critical = action not in NON_CRITICAL

            retry = RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            )

            try:
                output = await workflow.execute_activity(
                    activity_fn,
                    args=list(params.values()) if params else [],
                    task_queue=TASK_QUEUE,
                    start_to_close_timeout=timedelta(seconds=timeout),
                    retry_policy=retry,
                )
                results.append({
                    "index":  i,
                    "action": action,
                    "status": "success",
                    "output": str(output),
                })

            except ActivityError as e:
                err = str(e.cause) if e.cause else str(e)
                results.append({
                    "index":  i,
                    "action": action,
                    "status": "error",
                    "output": err,
                })
                # Stop workflow only for critical failures
                if is_critical and action not in NON_CRITICAL:
                    # Try fallback for browser navigation
                    if action == "search_youtube":
                        # Already self-sufficient, just continue
                        pass
                    else:
                        break

            except Exception as e:
                results.append({
                    "index":  i,
                    "action": action,
                    "status": "error",
                    "output": str(e),
                })

        return {"results": results, "summary": summary}
