import random
 
# ─────────────────────────────────────────────
#  ID de l'utilisateur ciblé
#  Remplace par l'ID Discord réel (clic droit
#  sur l'utilisateur > Copier l'identifiant)
# ─────────────────────────────────────────────
TARGET_USER_ID = os.getenv("USER_BULLY_ID")
 
# ─────────────────────────────────────────────
#  Liste des réponses aléatoires
# ─────────────────────────────────────────────
RESPONSES = [
    "Ferme ta gueule William",
    "Tu parles trop",
    "Vraiment la ferme",
    "Houss il te baise",
    "Arrête tu pues de la gueule, je le sens alors que je suis un bot",
]
 
async def handle_spam(message) -> bool:
    """
    Vérifie si le message vient de l'utilisateur ciblé.
    Si oui, répond avec une string aléatoire et retourne True.
    Retourne False sinon.
    """
    if message.author.id != TARGET_USER_ID:
        return False
 
    response = random.choice(RESPONSES)
    await message.reply(response)
    return True
