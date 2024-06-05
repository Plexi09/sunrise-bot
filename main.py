
import discord
from discord import app_commands
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

# Définition des événements du bot
@client.event
async def on_ready():
    print(f"Logged on as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!ping'):
        await handle_ping(message)
    elif message.content.startswith('hello'):
        await handle_hello(message)
    elif message.content.startswith('!help'):
        await handle_help(message)
    elif message.content.startswith('!ip'):
        await handle_ip(message)
    elif message.content.startswith('!web'):
        await handle_web(message)

# Handlers pour les commandes spécifiques
async def handle_ping(message):
    start_time = time.perf_counter()
    message_ping = await message.channel.send('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await message_ping.edit(content=f'Pong! Latency: `{latency:.2f}ms`\nDemandé par {message.author.mention}')
    await message.delete()

async def handle_hello(message):
    await message.channel.send(f'Bonjour {message.author.mention} !')

async def handle_help(message):
    await message.channel.send(f'Commandes :`!ping`, `!hello`, `!ip`, `!web` \nDemandé par {message.author.mention}')
    await message.delete()

async def handle_ip(message):
    await message.channel.send(f'IP du serveur: `play.sunrisenetwork.eu` \nDemandé par {message.author.mention}')
    await message.delete()

async def handle_web(message):
    await message.channel.send(f'Site web du serveur: https://sunrisenetwork.eu \nDemandé par {message.author.mention}')
    await message.delete()

# Démarrage du bot
client.run(BOT_TOKEN)