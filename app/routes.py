import os

from fastapi import APIRouter, FastAPI

from app import domain
from app.skills import SKILLS
from smart_home_common import AgentClient, HomeMcpClient, IntentAgentExecutor, build_agent_card, mount_a2a

router = APIRouter()
mcp_client = HomeMcpClient(os.environ["BFA_URL"])
agent_client = AgentClient(os.environ["BFA_URL"], sender="security")

HANDLERS = {
    "secure_home": lambda input: domain.secure_home(mcp_client, agent_client),
    "check_security": lambda input: domain.check_security(mcp_client),
    "lock": lambda input: domain.device_command(mcp_client, "lock", input["device_id"]),
    "unlock": lambda input: domain.device_command(mcp_client, "unlock", input["device_id"]),
    "arm": lambda input: domain.device_command(mcp_client, "arm", input["device_id"]),
    "disarm": lambda input: domain.device_command(mcp_client, "disarm", input["device_id"]),
}


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.get("/ready")
def ready():
    return {"status": "ready"}


def mount(app: FastAPI) -> None:
    app.include_router(router)
    executor = IntentAgentExecutor(HANDLERS)
    card = build_agent_card("security", skills=SKILLS)
    mount_a2a(app, card, executor)
