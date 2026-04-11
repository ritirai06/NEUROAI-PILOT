from fastapi import APIRouter
from pydantic import BaseModel
from mcp.tool_registry import ToolRegistry
import asyncio

router = APIRouter(prefix="/mcp", tags=["MCP"])
registry = ToolRegistry()


class ToolCall(BaseModel):
    tool: str
    params: dict = {}


@router.get("/tools")
def list_tools():
    return {"tools": registry.list_tools()}


@router.post("/invoke")
async def invoke_tool(call: ToolCall):
    fn = registry.get(call.tool)
    if not fn:
        return {"status": "error", "output": f"Tool not found: {call.tool}"}
    try:
        if asyncio.iscoroutinefunction(fn):
            result = await fn(**call.params)
        else:
            result = await asyncio.to_thread(fn, **call.params)
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "output": str(e)}
