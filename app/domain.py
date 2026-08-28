from typing import Protocol

from smart_home_common import AgentUnavailableError

ALARM_DEVICE_ID = "alarm"
FRONT_DOOR_DEVICE_ID = "front_door"


class McpClientLike(Protocol):
    async def call_tool(self, name: str, arguments: dict | None = None): ...
    async def read_resource(self, uri: str): ...


class AgentClientLike(Protocol):
    async def call(self, capability: str, intent: str, input: dict, correlation_id: str | None = None): ...


async def secure_home(mcp: McpClientLike, agent_client: AgentClientLike) -> dict:
    await mcp.call_tool("lock", {"device_id": FRONT_DOOR_DEVICE_ID})
    await mcp.call_tool("arm", {"device_id": ALARM_DEVICE_ID})

    security_state = await mcp.read_resource("home://security")

    try:
        critical = await agent_client.call("identify_critical_devices", "identify_critical_devices", {})
    except AgentUnavailableError as exc:
        security_state["critical_devices_error"] = str(exc)
    else:
        if critical["status"] == "ok":
            security_state["critical_devices"] = critical["result"].get("critical_devices", [])
        else:
            security_state["critical_devices_error"] = str(critical["result"])

    return security_state


async def device_command(mcp: McpClientLike, verb: str, device_id: str, value: float | int | None = None) -> dict:
    """Forward a generic security verb ({lock, unlock, arm, disarm}) to the Home
    MCP. The MCP / BFF validate it against the device's announced capabilities."""
    args: dict = {"device_id": device_id}
    if value is not None:
        args["value"] = value
    return await mcp.call_tool(verb, args)


async def check_security(mcp: McpClientLike) -> dict:
    return await mcp.read_resource("home://security")
