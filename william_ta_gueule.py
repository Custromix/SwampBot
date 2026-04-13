import random
import os
from dotenv import load_dotenv
load_dotenv()
 
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
    "On s'en bas les couilles ftg",
]
 
PreviousResponses = []
LastResponse = "none"

MaxSameMsg = 2

async def handle_spam(message, isReEnter = False) -> bool:
    """
    Vérifie si le message vient de l'utilisateur ciblé.
    Si oui, vérifie si un message à déjà été envoyé N fois d'affilé @var = MaxSameMsg
    Si oui recommence,
    Si non répond avec une string aléatoire et retourne True.
    Retourne False sinon.
    """

    if message.author.id != int(TARGET_USER_ID):
        return False
 
    response = random.choice(RESPONSES)
    if PreviousResponses.count(response) == MaxSameMsg:
        return handle_spam(message, True)

    if(isReEnter):
        PreviousResponses.clear()

    if(len(PreviousResponses) == MaxSameMsg):
        PreviousResponses.pop(0)
        PreviousResponses.sort()
        PreviousResponses.append(response)
    elif(len(PreviousResponses) < MaxSameMsg):
        PreviousResponses.append(response)

    await message.reply(response)
    return True
