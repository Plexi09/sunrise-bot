import discord
from dotenv import load_dotenv
import os
import logging
import logging.handlers

################################
############LOGGING#############
################################
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

################################
############LOGGING#############
################################

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged on as {client.user}!")

@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    if message.author == client.user:
        return
    
    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!help'):
        await message.channel.send('Commandes :`!ping`, `!hello`, `!ip`, `!web`')

    if message.content.startswith('!ip'):
        await message.channel.send('IP du serveur: play.sunrisenetwork.eu')

    if message.content.startswith('!web'):
        await message.channel.send('Site web du serveur: https://sunrisenetwork.eu')


intents = discord.Intents.default()
intents.message_content = True

client.run(BOT_TOKEN)