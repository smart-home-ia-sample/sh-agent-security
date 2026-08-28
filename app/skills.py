# One entry per A2A skill, served on the agent card. `tags` / `examples` let the
# BFA rank the skill in /resolve straight from the card — no self-registration.
# Tuples: (id, name, description, tags, examples).
SKILLS = [
    ("secure_home", "Secure home", "Locks the front door, arms the alarm, and reports critical devices",
     ["security", "leave"], ["vou sair de casa", "estou saindo, tranca tudo", "protege a casa"]),
    ("check_security", "Check security", "Reports the current security state",
     ["security", "status"], ["a casa está trancada?", "status da segurança"]),
    ("lock", "Lock", "Locks a door", ["door", "security"], ["tranca a porta da frente"]),
    ("unlock", "Unlock", "Unlocks a door", ["door", "security"], ["destranca a porta da frente"]),
    ("arm", "Arm alarm", "Arms the home alarm", ["alarm", "security"], ["arma o alarme"]),
    ("disarm", "Disarm alarm", "Disarms the home alarm", ["alarm", "security"], ["desarma o alarme"]),
]
