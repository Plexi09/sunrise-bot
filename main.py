import discord
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv
import os
import time
import logging
import logging.handlers

# Configuration des logs
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='logs/discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5  # Rotation de 5 fichiers
)

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

# Configuration des intents et du client Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
slash = SlashCommand(client, sync_commands=True)  # Initializer les commandes slash

# Définition des événements du bot
@client.event
async def on_ready():
    print(f"Logged on as {client.user}!")

# Handlers pour les commandes spécifiques
async def handle_ping(ctx: SlashContext):
    start_time = time.perf_counter()
    await ctx.send(content='Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await ctx.edit(content=f'Pong! Latency: `{latency:.2f}ms`\nDemandé par {ctx.author.mention}')

async def handle_hello(ctx: SlashContext):
    await ctx.send(content=f'Bonjour {ctx.author.mention} !')

async def handle_help(ctx: SlashContext):
    await ctx.send(content=f'Commandes :`/ping`, `/hello`, `/ip`, `/web` \nDemandé par {ctx.author.mention}')

async def handle_ip(ctx: SlashContext):
    await ctx.send(content=f'IP du serveur: `play.sunrisenetwork.eu` \nDemandé par {ctx.author.mention}')

async def handle_web(ctx: SlashContext):
    await ctx.send(content=f'Site web du serveur: https://sunrisenetwork.eu \nDemandé par {ctx.author.mention}')

# Slash command definitions
@slash.slash(name="ping", description="Check the bot's latency")
async def ping(ctx: SlashContext):
    await handle_ping(ctx)

@slash.slash(name="hello", description="Say hello")
async def hello(ctx: SlashContext):
    await handle_hello(ctx)

@slash.slash(name="help", description="Get a list of available commands")
async def help(ctx: SlashContext):
    await handle_help(ctx)

@slash.slash(name="ip", description="Get the server IP")
async def ip(ctx: SlashContext):
    await handle_ip(ctx)

@slash.slash(name="web", description="Get the server website")
async def web(ctx: SlashContext):
    await handle_web(ctx)

# Démarrage du bot
client.run(BOT_TOKEN)
