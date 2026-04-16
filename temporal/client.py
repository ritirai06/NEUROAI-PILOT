"""
Temporal Client — triggers NeuroAI workflows and streams step results.
Used by FastAPI to start workflows and poll for updates.
"""
import os
from typing import AsyncGenerator

from temporalio.client import Client
from temporal.workflow import NeuroAIPlanWorkflow, TASK_QUEUE
from agent.executor import Executor
from mcp.tool_registry import ToolRegistry

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")

_client: Client | None = None
_stream_executor: Executor | None = None


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
    Yield step updates in real time for the UI.

    Temporal is still used for durable workflow execution elsewhere, but the
    current workflow integration cannot emit per-step updates until the whole
    workflow finishes. For the live WebSocket UI we prefer genuine streaming,
    so this path uses the direct executor.
    """
    global _stream_executor
    if _stream_executor is None:
        _stream_executor = Executor(registry=ToolRegistry())

    async for update in _stream_executor.execute_stream(plan):
        yield update
