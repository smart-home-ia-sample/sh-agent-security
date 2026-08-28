import httpx

from smart_home_common.registration_client import ServiceInfo, register_with_retry

SKILLS = [
    ("secure_home", "Secure home", "Locks the front door, arms the alarm, and reports critical devices",
     ["vou sair de casa", "estou saindo, tranca tudo", "protege a casa"]),
    ("check_security", "Check security", "Reports the current security state",
     ["a casa está trancada?", "status da segurança"]),
    ("lock", "Lock", "Locks a door", ["tranca a porta da frente"]),
    ("unlock", "Unlock", "Unlocks a door", ["destranca a porta da frente"]),
    ("arm", "Arm alarm", "Arms the home alarm", ["arma o alarme"]),
    ("disarm", "Disarm alarm", "Disarms the home alarm", ["desarma o alarme"]),
]

CAPABILITIES = [skill_id for skill_id, *_ in SKILLS]
CATALOG = [
    {"id": sid, "name": name, "description": desc, "tags": ["security"], "examples": examples}
    for sid, name, desc, examples in SKILLS
]


def register_with_bfa(bfa_url: str, port: int, version: str = "0.1.0", max_attempts: int = 10) -> dict:
    service = ServiceInfo(
        name="security", port=port, capabilities=CAPABILITIES, protocol="http", version=version, catalog=CATALOG
    )
    with httpx.Client(timeout=5.0) as client:
        return register_with_retry(client, bfa_url, service, kind="agents", max_attempts=max_attempts)
