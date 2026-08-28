import asyncio

from app import domain
from smart_home_common import AgentUnavailableError


class FakeMcpClient:
    def __init__(self, responses: dict):
        self.responses = responses
        self.calls: list[tuple] = []

    async def call_tool(self, name, arguments=None):
        self.calls.append(("call_tool", name, arguments))
        return self.responses.get(name, {})

    async def read_resource(self, uri):
        self.calls.append(("read_resource", uri, None))
        return self.responses.get(uri, {})


class FakeAgentClient:
    def __init__(self, response: dict | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[tuple] = []

    async def call(self, capability, intent, input, correlation_id=None):
        self.calls.append((capability, intent, input))
        if self.error is not None:
            raise self.error
        return self.response


def test_secure_home_locks_door_and_arms_alarm():
    mcp = FakeMcpClient({"home://security": {"alarm_armed": True, "doors": {"front_door": {"locked": True}}}})
    agent_client = FakeAgentClient(response={"status": "ok", "result": {"critical_devices": []}})

    result = asyncio.run(domain.secure_home(mcp, agent_client))

    tool_calls = [(c[1], c[2]) for c in mcp.calls if c[0] == "call_tool"]
    assert ("lock", {"device_id": "front_door"}) in tool_calls
    assert ("arm", {"device_id": "alarm"}) in tool_calls
    assert result["alarm_armed"] is True


def test_secure_home_calls_energy_and_includes_critical_devices():
    mcp = FakeMcpClient({"home://security": {"alarm_armed": True}})
    agent_client = FakeAgentClient(
        response={
            "status": "ok",
            "result": {"critical_devices": [{"id": "kitchen_refrigerator", "type": "refrigerator"}]},
        }
    )

    result = asyncio.run(domain.secure_home(mcp, agent_client))

    assert agent_client.calls == [("identify_critical_devices", "identify_critical_devices", {})]
    assert result["critical_devices"] == [{"id": "kitchen_refrigerator", "type": "refrigerator"}]


def test_secure_home_still_succeeds_when_energy_is_unavailable():
    mcp = FakeMcpClient({"home://security": {"alarm_armed": True, "doors": {"front_door": {"locked": True}}}})
    agent_client = FakeAgentClient(error=AgentUnavailableError("agent 'energy' unreachable"))

    result = asyncio.run(domain.secure_home(mcp, agent_client))

    assert result["alarm_armed"] is True
    assert result["doors"]["front_door"]["locked"] is True
    assert "critical_devices_error" in result
    assert "critical_devices" not in result


def test_device_command_lock_and_unlock():
    fake = FakeMcpClient({"lock": {"id": "front_door", "locked": True},
                          "unlock": {"id": "front_door", "locked": False}})

    locked = asyncio.run(domain.device_command(fake, "lock", "front_door"))
    unlocked = asyncio.run(domain.device_command(fake, "unlock", "front_door"))

    assert ("call_tool", "lock", {"device_id": "front_door"}) in fake.calls
    assert locked["locked"] is True
    assert unlocked["locked"] is False


def test_device_command_arm_and_disarm():
    fake = FakeMcpClient({"arm": {"armed": True}, "disarm": {"armed": False}})

    armed = asyncio.run(domain.device_command(fake, "arm", "alarm"))
    disarmed = asyncio.run(domain.device_command(fake, "disarm", "alarm"))

    assert ("call_tool", "arm", {"device_id": "alarm"}) in fake.calls
    assert armed["armed"] is True
    assert disarmed["armed"] is False


def test_check_security_reads_resource():
    fake = FakeMcpClient({"home://security": {"alarm_armed": False}})

    result = asyncio.run(domain.check_security(fake))

    assert fake.calls == [("read_resource", "home://security", None)]
    assert result["alarm_armed"] is False
