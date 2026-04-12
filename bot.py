import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import os
from dotenv import load_dotenv
load_dotenv()
from stay_alive import Stay_alive
from william_ta_gueule import handle_spam

# ─────────────────────────────────────────────
#  Configuration yt-dlp
# ─────────────────────────────────────────────
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
    }],
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


# ─────────────────────────────────────────────
#  Source audio
# ─────────────────────────────────────────────
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Titre inconnu")
        self.url = data.get("webpage_url", "")
        self.duration = data.get("duration", 0)
        self.thumbnail = data.get("thumbnail", "")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            # Playlist : retourne la liste de toutes les entrées
            return [
                cls(
                    discord.FFmpegPCMAudio(entry["url"], **FFMPEG_OPTIONS),
                    data=entry,
                )
                for entry in data["entries"]
                if entry
            ]
        return cls(
            discord.FFmpegPCMAudio(data["url"], **FFMPEG_OPTIONS),
            data=data,
        )


# ─────────────────────────────────────────────
#  État par serveur
# ─────────────────────────────────────────────
class GuildState:
    def __init__(self):
        self.queue: deque = deque()
        self.current = None
        self.loop_current = False
        self.loop_queue = False
        self.volume = 0.5


guild_states: dict[int, GuildState] = {}


def get_state(guild_id: int) -> GuildState:
    if guild_id not in guild_states:
        guild_states[guild_id] = GuildState()
    return guild_states[guild_id]


# ─────────────────────────────────────────────
#  Bot
# ─────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def format_duration(seconds: int) -> str:
    if not seconds:
        return "?:??"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


async def play_next(ctx):
    state = get_state(ctx.guild.id)
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return

    if state.loop_current and state.current:
        # Rejouer la piste actuelle
        source = await YTDLSource.from_url(state.current.url, loop=bot.loop)
        if isinstance(source, list):
            source = source[0]
        state.current = source
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        return

    if not state.queue:
        state.current = None
        embed = discord.Embed(
            title="✅ File d'attente terminée",
            description="Plus aucune piste en attente.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)
        return

    source = state.queue.popleft()
    source.volume = state.volume
    state.current = source

    if state.loop_queue:
        state.queue.append(source)

    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

    embed = discord.Embed(
        title="▶️ Lecture en cours",
        description=f"**[{source.title}]({source.url})**",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Durée", value=format_duration(source.duration))
    if source.thumbnail:
        embed.set_thumbnail(url=source.thumbnail)
    await ctx.send(embed=embed)


# ─────────────────────────────────────────────
#  Événements
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="!help pour les commandes"
    ))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant. Tape `!help {ctx.command}` pour plus d'infos.")
    else:
        await ctx.send(f"❌ Erreur : `{error}`")

@bot.event      
async def on_message(message):
    # Ignorer les messages du bot lui-même
    if message.author.bot:
        return
 
    # Passer le message au module spam — si l'utilisateur ciblé a écrit,
    # on répond et on s'arrête là (pas de traitement de commande)
    if await handle_spam(message):
        return
 
    # Laisser le bot traiter les commandes normalement
    await bot.process_commands(message)   


# ─────────────────────────────────────────────
#  Commandes vocales
# ─────────────────────────────────────────────
@bot.command(name="join", aliases=["j"], help="Rejoindre ton salon vocal")
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Tu dois être dans un salon vocal.")
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
        return await ctx.send(f"🔀 Déplacé vers **{channel.name}**.")
    await channel.connect()
    await ctx.send(f"🔊 Connecté à **{channel.name}**.")


@bot.command(name="leave", aliases=["dc", "quitter"], help="Quitter le salon vocal")
async def leave(ctx):
    if not ctx.voice_client:
        return await ctx.send("❌ Je ne suis dans aucun salon vocal.")
    state = get_state(ctx.guild.id)
    state.queue.clear()
    state.current = None
    await ctx.voice_client.disconnect()
    await ctx.send("👋 Déconnecté du salon vocal.")


# ─────────────────────────────────────────────
#  Commandes de lecture
# ─────────────────────────────────────────────
@bot.command(name="play", aliases=["p"], help="Jouer une vidéo YouTube (URL ou recherche)")
async def play(ctx, *, url: str):
    # Rejoindre automatiquement si nécessaire
    if not ctx.voice_client:
        if not ctx.author.voice:
            return await ctx.send("❌ Tu dois être dans un salon vocal.")
        await ctx.author.voice.channel.connect()

    state = get_state(ctx.guild.id)
    msg = await ctx.send("🔍 Recherche en cours...")

    try:
        source = await YTDLSource.from_url(url, loop=bot.loop)
    except Exception as e:
        return await msg.edit(content=f"❌ Impossible de charger la piste : `{e}`")

    if isinstance(source, list):
        for s in source:
            state.queue.append(s)
        embed = discord.Embed(
            title="📋 Playlist ajoutée",
            description=f"**{len(source)}** pistes ajoutées à la file.",
            color=discord.Color.orange(),
        )
        await msg.edit(content=None, embed=embed)
    else:
        state.queue.append(source)
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            embed = discord.Embed(
                title="➕ Ajouté à la file",
                description=f"**[{source.title}]({source.url})**",
                color=discord.Color.orange(),
            )
            embed.add_field(name="Position", value=f"#{len(state.queue)}")
            embed.add_field(name="Durée", value=format_duration(source.duration))
            if source.thumbnail:
                embed.set_thumbnail(url=source.thumbnail)
            await msg.edit(content=None, embed=embed)
        else:
            await msg.delete()

    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        await play_next(ctx)


@bot.command(name="skip", aliases=["s"], help="Passer à la piste suivante")
async def skip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("❌ Aucune piste en cours de lecture.")
    ctx.voice_client.stop()
    await ctx.send("⏭️ Piste ignorée.")


@bot.command(name="pause", help="Mettre en pause")
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Lecture mise en pause.")
    else:
        await ctx.send("❌ Aucune piste en cours de lecture.")


@bot.command(name="resume", aliases=["r"], help="Reprendre la lecture")
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Lecture reprise.")
    else:
        await ctx.send("❌ La lecture n'est pas en pause.")


@bot.command(name="stop", help="Arrêter la lecture et vider la file")
async def stop(ctx):
    state = get_state(ctx.guild.id)
    state.queue.clear()
    state.current = None
    if ctx.voice_client:
        ctx.voice_client.stop()
    await ctx.send("⏹️ Lecture arrêtée et file vidée.")


@bot.command(name="volume", aliases=["vol"], help="Régler le volume (0-100)")
async def volume(ctx, vol: int):
    if not 0 <= vol <= 100:
        return await ctx.send("❌ Le volume doit être entre 0 et 100.")
    state = get_state(ctx.guild.id)
    state.volume = vol / 100
    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = state.volume
    await ctx.send(f"🔊 Volume réglé à **{vol}%**.")


# ─────────────────────────────────────────────
#  File d'attente
# ─────────────────────────────────────────────
@bot.command(name="queue", aliases=["q", "file"], help="Afficher la file d'attente")
async def queue(ctx):
    state = get_state(ctx.guild.id)
    if not state.current and not state.queue:
        return await ctx.send("📭 La file d'attente est vide.")

    embed = discord.Embed(title="📋 File d'attente", color=discord.Color.blurple())

    if state.current:
        embed.add_field(
            name="▶️ En cours",
            value=f"[{state.current.title}]({state.current.url}) `{format_duration(state.current.duration)}`",
            inline=False,
        )

    if state.queue:
        lines = []
        for i, track in enumerate(list(state.queue)[:10], 1):
            lines.append(f"`{i}.` [{track.title}]({track.url}) `{format_duration(track.duration)}`")
        if len(state.queue) > 10:
            lines.append(f"*...et {len(state.queue) - 10} autres pistes*")
        embed.add_field(name="⏳ Suivantes", value="\n".join(lines), inline=False)

    flags = []
    if state.loop_current:
        flags.append("🔂 Répétition (piste)")
    if state.loop_queue:
        flags.append("🔁 Répétition (file)")
    if flags:
        embed.set_footer(text=" | ".join(flags))

    await ctx.send(embed=embed)


@bot.command(name="clear", help="Vider la file d'attente")
async def clear(ctx):
    state = get_state(ctx.guild.id)
    state.queue.clear()
    await ctx.send("🗑️ File d'attente vidée.")


@bot.command(name="remove", help="Supprimer une piste de la file (par numéro)")
async def remove(ctx, index: int):
    state = get_state(ctx.guild.id)
    if index < 1 or index > len(state.queue):
        return await ctx.send(f"❌ Index invalide. La file contient **{len(state.queue)}** piste(s).")
    removed = list(state.queue)[index - 1]
    new_queue = list(state.queue)
    new_queue.pop(index - 1)
    state.queue = deque(new_queue)
    await ctx.send(f"🗑️ Supprimé : **{removed.title}**")


@bot.command(name="loop", help="Répéter la piste actuelle (on/off)")
async def loop(ctx):
    state = get_state(ctx.guild.id)
    state.loop_current = not state.loop_current
    status = "activée 🔂" if state.loop_current else "désactivée"
    await ctx.send(f"Répétition de la piste {status}.")


@bot.command(name="loopqueue", aliases=["lq"], help="Répéter toute la file (on/off)")
async def loopqueue(ctx):
    state = get_state(ctx.guild.id)
    state.loop_queue = not state.loop_queue
    status = "activée 🔁" if state.loop_queue else "désactivée"
    await ctx.send(f"Répétition de la file {status}.")


# ─────────────────────────────────────────────
#  Infos sur la piste en cours
# ─────────────────────────────────────────────
@bot.command(name="now", aliases=["np", "playing"], help="Afficher la piste en cours")
async def now_playing(ctx):
    state = get_state(ctx.guild.id)
    if not state.current:
        return await ctx.send("❌ Aucune piste en cours de lecture.")
    embed = discord.Embed(
        title="🎵 En cours de lecture",
        description=f"**[{state.current.title}]({state.current.url})**",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Durée", value=format_duration(state.current.duration))
    embed.add_field(name="Volume", value=f"{int(state.volume * 100)}%")
    if state.current.thumbnail:
        embed.set_thumbnail(url=state.current.thumbnail)
    await ctx.send(embed=embed)


# ─────────────────────────────────────────────
#  Aide personnalisée
# ─────────────────────────────────────────────
@bot.command(name="help", help="Afficher cette aide")
async def help_command(ctx):
    embed = discord.Embed(
        title="🎵 Commandes du bot musical",
        color=discord.Color.blurple(),
    )
    categories = {
        "🔊 Vocal": [
            ("`!join` / `!j`", "Rejoindre ton salon vocal"),
            ("`!leave` / `!dc`", "Quitter le salon vocal"),
        ],
        "▶️ Lecture": [
            ("`!play <url/recherche>` / `!p`", "Jouer une vidéo YouTube ou une playlist"),
            ("`!skip` / `!s`", "Passer à la piste suivante"),
            ("`!pause`", "Mettre en pause"),
            ("`!resume` / `!r`", "Reprendre la lecture"),
            ("`!stop`", "Arrêter et vider la file"),
            ("`!volume <0-100>`", "Régler le volume"),
            ("`!now` / `!np`", "Voir la piste en cours"),
        ],
        "📋 File d'attente": [
            ("`!queue` / `!q`", "Afficher la file d'attente"),
            ("`!clear`", "Vider la file d'attente"),
            ("`!remove <n>`", "Supprimer la piste n° N"),
            ("`!loop`", "Répéter la piste actuelle"),
            ("`!loopqueue` / `!lq`", "Répéter toute la file"),
        ],
    }
    for cat, cmds in categories.items():
        value = "\n".join(f"{name} — {desc}" for name, desc in cmds)
        embed.add_field(name=cat, value=value, inline=False)
    embed.set_footer(text="Supporte les URLs YouTube, les recherches texte et les playlists.")
    await ctx.send(embed=embed)


# ─────────────────────────────────────────────
#  Lancement
# ─────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Variable d'environnement DISCORD_TOKEN manquante.")

Stay_alive()
bot.run(TOKEN)
