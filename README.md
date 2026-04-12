# SwampBot
Bot du swamp en open source baby

---

## 📦 Prérequis

- Python 3.10+
- FFmpeg installé et accessible dans le PATH
- Un token de bot Discord

---

## ⚙️ Installation

### 1. Installer FFmpeg

**Windows**
Télécharge FFmpeg sur https://ffmpeg.org/download.html, extrais l'archive et ajoute
le dossier `bin/` à ta variable d'environnement PATH.

Si t'as Winget tu fais :
```bash
winget install ffmpeg
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**macOS**
```bash
brew install ffmpeg
```

---

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

---

### 3. Créer le bot sur Discord

1. Rends-toi sur https://discord.com/developers/applications
2. Clique sur **New Application**, donne un nom.
3. Va dans **Bot** > **Add Bot**.
4. Active les **Privileged Gateway Intents** :
   - `MESSAGE CONTENT INTENT` (obligatoire)
5. Copie le **Token** du bot (tu en auras besoin juste après).
6. Va dans **OAuth2 > URL Generator** :
   - Scopes : `bot`
   - Bot Permissions : `Connect`, `Speak`, `Send Messages`, `Read Message History`, `Embed Links`
7. Copie l'URL générée et invite le bot sur ton serveur.

---

### 4. Configurer le token

Install **python-dotenv**
```bash
pip install pytho-dotenv
```

**Fichier `.env`**
```
DISCORD_TOKEN=ton_token_ici
```

### 5. Lancer le bot

```bash
python bot.py
```

---

## 🎮 Commandes disponibles

| Commande | Alias | Description |
|---|---|---|
| `!join` | `!j` | Rejoindre ton salon vocal |
| `!leave` | `!dc` | Quitter le salon vocal |
| `!play <url/recherche>` | `!p` | Jouer une vidéo, une recherche ou une playlist |
| `!skip` | `!s` | Passer à la piste suivante |
| `!pause` | — | Mettre en pause |
| `!resume` | `!r` | Reprendre la lecture |
| `!stop` | — | Arrêter et vider la file |
| `!volume <0-100>` | `!vol` | Régler le volume |
| `!now` | `!np` | Voir la piste en cours |
| `!queue` | `!q` | Afficher la file d'attente |
| `!clear` | — | Vider la file d'attente |
| `!remove <n>` | — | Supprimer la piste n° N de la file |
| `!loop` | — | Répéter la piste actuelle |
| `!loopqueue` | `!lq` | Répéter toute la file |
| `!help` | — | Afficher l'aide |

---

## 🛠️ Dépannage

- **"DISCORD_TOKEN manquante"** : vérifie que la variable d'environnement est bien définie.
- **Pas de son** : vérifie que FFmpeg est installé et dans le PATH (`ffmpeg -version`).
- **"Opus library not found"** : installe `libopus` (`apt install libopus-dev` sur Linux) ou PyNaCl (`pip install PyNaCl`).
- **Erreur yt-dlp** : mets à jour yt-dlp (`pip install -U yt-dlp`).
