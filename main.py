import logging
from dotenv import load_dotenv
import os
from interactions import slash_command, SlashContext, OptionType, slash_option, check, is_owner
import interactions
import time
import asyncio
import random
import aiohttp
from datetime import datetime

# Configurer le logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(filename=(f'logs/discord_{timestamp}.log'), level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configuration du bot et des intents
bot = interactions.Client(token=BOT_TOKEN)

# Définir l'encodage de sortie sur UTF-8
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Événement déclenché lorsque le bot est prêt
@bot.event
async def on_ready():
    logger.info(f'Connecté en tant que {bot.me.name}')

# Commande pour afficher l'IP du serveur
@slash_command(name="ip", description="Affiche l'IP du serveur.")
async def ip_function(ctx: SlashContext):
    await ctx.send('IP du serveur: `play.sunrisenetwork.eu`')
    logger.info(f"Commande exécutée par {ctx.author.name}: ip.")

# Commande pour afficher l'URL du site web
@slash_command(name="web",description="Affiche l'URL du site web")
async def web_function(ctx: SlashContext):
    await ctx.send('Site web du serveur: https://sunrisenetwork.eu')
    logger.info(f"Commande exécutée par {ctx.author.name}: web.")

# Commande pour répéter le message de l'utilisateur
@slash_command(name="echo",description="Répète le message de l'utilisateur")
@slash_option(
            name="text",
            description="Texte à répéter",
            opt_type=OptionType.STRING,
            required=True,
        )
async def echo_function(ctx: SlashContext, text: str):
    await ctx.send(f"{text}")
    logger.info(f"Commande exécutée par {ctx.author}: echo. Message: {text}")

# Commande pour afficher "Pong!" avec la latence
@slash_command(name="ping",description="Pong")
async def ping_function(ctx: SlashContext):
    start_time = time.perf_counter()
    message = await ctx.send('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await message.edit(content=f'Pong! Latence: `{latency:.2f}ms`')
    logger.info(f"Commande exécutée par {ctx.author}: ping. Latence: `{latency:.2f}ms`")

# Commande pour effectuer un benchmark de latence
@slash_command(name="benchmark",description="Mesure de la latence du bot")
@slash_option(
    name="duration",
    description="Durée du benchmark en secondes",
    opt_type=OptionType.INTEGER,
    required=True,
    )
async def benchmark_function(ctx: SlashContext, duration: int):
    logger.info(f"Démarrage du benchmark par {ctx.author}")
    latencies = []

    start_time = time.time()
    while time.time() - start_time < duration:
        ping_start = time.perf_counter()
        message = await ctx.send("Benchmarking...")
        await message.delete()
        ping_end = time.perf_counter()
        latency = (ping_end - ping_start) * 1000
        latencies.append(latency)
        await asyncio.sleep(1)

    if latencies:
        min_latency = min(latencies)
        max_latency = max(latencies)
        avg_latency = sum(latencies) / len(latencies)
        await ctx.send(f"Résultats du benchmark sur {duration} secondes:\n"
                       f"Latence Min: `{min_latency:.2f}ms`\n"
                       f"Latence Max: `{max_latency:.2f}ms`\n"
                       f"Latence Moyenne: `{avg_latency:.2f}ms`")
        logger.info(f"Fin du benchmark sur {duration} secondes. Latency min: `{min_latency:.2f}ms. Latency max: `{max_latency:.2f}ms. Latency avg: `{avg_latency:.2f}ms")
    else:
        await ctx.send("Aucune donnée de latence collectée.")
        logger.warning(f"Aucune donnée de latence collectée lors du benchmark par {ctx.author}")

# Commande pour générer un nombre aléatoire entre min et max
@slash_command(name="random",description="Génère un nombre aléatoire")
@slash_option(
    name="min",
    description="Nombre minimum",
    opt_type=OptionType.INTEGER,
    required=True,
)
@slash_option(
    name="max",
    description="Nombre maximum",
    opt_type=OptionType.INTEGER,
    required=True,
)
async def random_function(ctx: SlashContext, min: int, max: int):
    randomnumber = random.randint(min, max)
    await ctx.send(f"Nombre aléatoire: {randomnumber}")
    logger.info(f"Commande exécutée par {ctx.author}: random. Nombre aléatoire: {randomnumber}")

# Commande pour rechercher sur Google
@slash_command(name="google",description="Recherche sur Google")
@slash_option(
    name="recherche",
    description="Recherche à effectuer",
    opt_type=OptionType.STRING,
    required=True
)
async def google_function(ctx: SlashContext, recherche: str):
    search_engine_id = '20f02a5ebf8234b5f'
    url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={search_engine_id}&q={recherche}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            search_results = await response.json()

    try:
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await ctx.send(f"{result['title']}: {result['link']}")
                logger.info(f"Commande exécutée par {ctx.author}: Google. Recherche: {recherche}")
        else:
            await ctx.send('Aucun résultat trouvé.')
            logger.info(f"Aucun résultat trouvé pour la recherche '{recherche}' par {ctx.author}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche: {e}")

# Commande pour rechercher sur Wikipedia
@slash_command(name="wikipedia",description="Recherche sur Wikipedia")
@slash_option(
    name="recherche",
    description="Recherche à effectuer",
    opt_type=OptionType.STRING,
    required=True
)
async def wikipedia_function(ctx: SlashContext, recherche: str):
    url = f'https://fr.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': recherche,
        'srlimit': 1,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            search_results = await response.json()

    try:
        if 'query' in search_results and 'search' in search_results['query'] and search_results['query']['search']:
            article_title = search_results['query']['search'][0]['title']
            article_url = f'https://fr.wikipedia.org/wiki/{article_title.replace(" ", "_")}'
            await ctx.send(f'Voici un lien vers l\'article Wikipedia correspondant: {article_url}')
            logger.info(f"Commande exécutée par {ctx.author}: Wikipedia. Recherche: {recherche}")
        else:
            await ctx.send('Aucun résultat trouvé sur Wikipédia.')
            logger.info(f"Aucun résultat trouvé sur Wikipédedia pour la recherche '{recherche}' par {ctx.author}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche: {e}")

# Commande pour rechercher sur le Wiki
@slash_command(name="wiki", description="Recherche sur le Wiki")
@slash_option(
    name="recherche",
    description="Recherche à effectuer",
    opt_type=OptionType.STRING,
    required=True
)
async def wiki_function(ctx: SlashContext, recherche: str):
    search_engine_id = '567f0ad4fa4ff419d'
    url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={search_engine_id}&q={recherche}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            search_results = await response.json()

    try:
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await ctx.send(f"{result['title']}: {result['link']}")
                logger.info(f"Commande exécutée par {ctx.author}: Google. Recherche: {recherche}")
        else:
            await ctx.send('Aucun résultat trouvé.')
            logger.info(f"Aucun résultat trouvé pour la recherche '{recherche}' par {ctx.author}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche: {e}")

# Démarrage du bot
bot.start()