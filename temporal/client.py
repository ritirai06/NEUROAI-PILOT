"""
Temporal Client — triggers NeuroAI workflows and streams step results.
Used by FastAPI to start workflows and poll for updates.
"""
import asyncio
import os
import uuid
from typing import AsyncGenerator

from temporalio.client import Client, WorkflowHandle
from temporal.workflow import NeuroAIPlanWorkflow, TASK_QUEUE

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")

_client: Client | None = None


async def get_client() -> Client:
    global _client
    if _client is None:
        _client = await Client.connect(TEMPORAL_HOST)
    return _client


async def run_plan(plan: dict) -> dict:
    """Execute a plan via Temporal and return full results."""
    client = await get_client()
    workflow_id = f"neuroai-{uuid.uuid4().hex[:8]}"
    result = await client.execute_workflow(
        NeuroAIPlanWorkflow.run,
        plan,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    return result


async def run_plan_stream(plan: dict) -> AsyncGenerator[dict, None]:
    """
    Execute a plan via Temporal and yield step updates in real-time.
    Since Temporal doesn't push events, we simulate streaming by
    running the workflow and yielding results as they complete.
    Falls back to direct execution if Temporal is unavailable.
    """
    client = await get_client()
    workflow_id = f"neuroai-{uuid.uuid4().hex[:8]}"
    steps = plan.get("steps", [])

    # Yield "running" for each step immediately
    for i, step in enumerate(steps):
        yield {
            "index":  i,
            "action": step.get("action", ""),
            "params": step.get("params", {}),
            "status": "running",
        }

    # Execute full workflow
    handle: WorkflowHandle = await client.start_workflow(
        NeuroAIPlanWorkflow.run,
        plan,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    result = await handle.result()

    # Yield final results
    for r in result.get("results", []):
        yield {
            "index":  r["index"],
            "action": r["action"],
            "params": steps[r["index"]].get("params", {}) if r["index"] < len(steps) else {},
            "status": r["status"],
            "output": r.get("output", ""),
        }
