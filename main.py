import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import time
import logging
import logging.handlers
import statistics
import asyncio
import random
import requests

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

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Commande inconnue. Voici la liste des commandes disponibles:\n`{", ".join([command.name for command in bot.commands])}`')
    else:
        await ctx.send(f"Une erreur s'est produite lors de l'exécution de la commande. Veuillez vérifier la console pour plus de détails. Erreur: {error}")
        raise error

@bot.command(name='ping')
async def ping(ctx):
    """: Mesure la latence du bot"""
    start_time = time.perf_counter()
    message = await ctx.send('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await message.edit(content=f'Pong! Latence: `{latency:.2f}ms`\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='hello')
async def hello(ctx):
    """: Bonjours !"""
    await ctx.send(f'Bonjour {ctx.author.mention}!')

@bot.command(name='ip')
async def ip(ctx):
    """: Affiche l'IP du serveur"""
    await ctx.send(f'IP du serveur: `play.sunrisenetwork.eu`\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='web')
async def web(ctx):
    """: Affiche l'URL du site web"""
    await ctx.send(f'Site web du serveur: https://sunrisenetwork.eu\nDemandé par {ctx.author.mention}')
    await ctx.message.delete()

@bot.command(name='echo')
async def echo(ctx, *, message: str):
    """: Répète le message de l'utilisateur"""
    await ctx.send(message)
    await ctx.message.delete()

@bot.command(name='random')
async def random(ctx, min: int = None, max: int = None):
    """: Génère un nombre aléatoire"""
    if min is None or max is None:
        await ctx.send('Usage: `!random <min> <max>`')
        return
    
    await ctx.send("Nombre aléatoire: " + str(random.randint(min, max)))
    await ctx.message.delete()

@bot.command(name='benchmark')
async def benchmark(ctx, duration: int = None):
    """: Mesure de la latence du bot sur une durée donnée (en secondes)."""
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

def search_google(query):
    google_api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = '20f02a5ebf8234b5f'
    url = f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}'
    response = requests.get(url)
    search_results = response.json()
    return search_results

# Commande pour effectuer une recherche sur Google
@bot.command(name='google')
async def google(ctx, *, query: str):
    """: Effectuer une recherche sur Google"""
    try:
        search_results = search_google(query)
        if 'items' in search_results:
            for result in search_results['items'][:5]:
                await ctx.send(f"{result['title']}: {result['link']}")
        else:
            await ctx.send('Aucun résultat trouvé.')
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")

def search_wiki(query):
    google_api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = '567f0ad4fa4ff419d'
    url = f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}'
    response = requests.get(url)
    search_results = response.json()
    return search_results

# Commande pour effectuer une recherche sur le wiki
@bot.command(name='wiki')
async def google(ctx, *, query: str):
    """: Effectuer une recherche sur le Wiki"""
    try:
        search_results = search_wiki(query)
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await ctx.send(f"{result['title']}: {result['link']}")
        else:
            await ctx.send('Aucun résultat trouvé.')
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")

def search_wikipedia(query):
    url = f'https://fr.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': query,
        'srlimit': 1,
    }
    response = requests.get(url, params=params)
    search_results = response.json()
    return search_results

# Commande pour effectuer une recherche sur Wikipédia
@bot.command(name='ckoi')
async def wikipedia_search(ctx, *, query: str):
    """: Effectuer une recherche sur Wikipedia"""
    try:
        search_results = search_wikipedia(query)
        if 'query' in search_results and 'search' in search_results['query'] and search_results['query']['search']:
            article_title = search_results['query']['search'][0]['title']
            article_url = f'https://fr.wikipedia.org/wiki/{article_title.replace(" ", "_")}'
            await ctx.send(f'Voici un lien vers l\'article Wikipedia correspondant: {article_url}')
        else:
            await ctx.send('Aucun résultat trouvé sur Wikipédia.')
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")

# Démarrage du bot
bot.run(BOT_TOKEN)
