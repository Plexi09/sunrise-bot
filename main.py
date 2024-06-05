import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import time
import logging
import logging.handlers
import statistics
import asyncio

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

# Configuration des intents et du bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}!')

@bot.command(name='ping')
async def ping(ctx):
    start_time = time.perf_counter()
    message = await ctx.send('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await message.edit(content=f'Pong! Latence: `{latency:.2f}ms`\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Bonjour {ctx.author.mention}!')

@bot.command(name='helpme')
async def help_command(ctx):
    commands_list = '`!ping`, `!hello`, `!ip`, `!web`, `!echo`, `!benchmark <durée>`'
    await ctx.send(f'Commandes: {commands_list}\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='ip')
async def ip(ctx):
    await ctx.send(f'IP du serveur: `play.sunrisenetwork.eu`\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='web')
async def web(ctx):
    await ctx.send(f'Site web du serveur: https://sunrisenetwork.eu\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='echo')
async def echo(ctx, *, message: str):
    await ctx.send(message)
    await ctx.message.delete()

@bot.command(name='benchmark')
async def benchmark(ctx, duration: int = None):
    """Mesure de la latence du bot sur une durée donnée (en secondes)."""
    if duration is None:
        await ctx.send('Usage: `!benchmark <durée en secondes>`')
        return

    latencies = []

    start_time = time.time()
    while time.time() - start_time < duration:
        ping_start = time.perf_counter()
        message = await ctx.send('Benchmarking...')
        ping_end = time.perf_counter()
        latency = (ping_end - ping_start) * 1000  # Convertir en millisecondes
        latencies.append(latency)
        await message.delete()
        await asyncio.sleep(1)  # Attendre une seconde avant le prochain ping

    if latencies:
        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = statistics.mean(latencies)
        await ctx.send(f'Résultats du benchmark sur {duration} secondes:\n'
                       f'Latence Min: `{min_latency:.2f}ms`\n'
                       f'Latence Max: `{max_latency:.2f}ms`\n'
                       f'Latence Moyenne: `{avg_latency:.2f}ms`\n'
                       f'Demandé par {ctx.author.mention}')
    else:
        await ctx.send('Aucune donnée de latence collectée. Veuillez réessayer.')

# Démarrage du bot
bot.run(BOT_TOKEN)
