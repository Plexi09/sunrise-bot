from dotenv import load_dotenv
import os
import interactions
import time
import asyncio
import random
import requests
import sys

# Définir l'encodage de sortie sur UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# Configuration du bot et des intents
bot = interactions.Client(token=BOT_TOKEN)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.me.name}')


@bot.command(
    name="ip",
    description="Affiche l'IP du serveur",
    scope=GUILD_ID,
)
async def ip(ctx: interactions.CommandContext):
    await ctx.send('IP du serveur: `play.sunrisenetwork.eu`')
    print(f"Commande exécutée par {ctx.author.name}: ip.")


@bot.command(
    name="web",
    description="Affiche l'URL du site web",
    scope=GUILD_ID,
)
async def web(ctx: interactions.CommandContext):
    await ctx.send('Site web du serveur: https://sunrisenetwork.eu')
    print(f"Commande exécutée par {ctx.author.name}: web.")


@bot.command(
    name="echo",
    description="Répète le message de l'utilisateur",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="text",
            description="Texte à répéter",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def echo(ctx: interactions.CommandContext, text: str):
    await ctx.send(f"{text}")
    print(f"Commande exécutée par {ctx.author.name}: echo.")


@bot.command(
    name="ping",
    description="Pong",
    scope=GUILD_ID
)
async def ping(ctx: interactions.CommandContext):
    start_time = time.perf_counter()
    message = await ctx.send('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await message.edit(content=f'Pong! Latence: `{latency:.2f}ms`')
    print(f"Commande exécutée par {ctx.author.name}: ping. Latence: `{latency:.2f}ms`")


@bot.command(
    name="benchmark",
    description="Mesure de la latence du bot",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="duration",
            description="Durée du benchmark en secondes",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def benchmark(ctx: interactions.CommandContext, duration: int):
    print(f"Démarrage du benchmark par {ctx.author.name}")
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
        print(f"Fin du benchmark sur {duration}. Latency min: `{min_latency:.2f}ms. Latency max: `{max_latency:.2f}ms. Latency avg: `{avg_latency:.2f}ms")
    else:
        await ctx.send("Aucune donnée de latence collectée.")


@bot.command(
    name="random",
    description="Génère un nombre aléatoire",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="min",
            description="Nombre minimum",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="max",
            description="Nombre maximum",
            type=interactions.OptionType.INTEGER,
            required=True,
        )
    ]
)
async def random_command(ctx: interactions.CommandContext, min: int, max: int):
    randomnumber = random.randint(min, max)
    await ctx.send(f"Nombre aléatoire: {randomnumber}")
    print(f"Commande exécutée par {ctx.author.name}: random. Nombre aléatoire: {randomnumber}")


@bot.command(
    name="google",
    description="Recherche sur Google",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="recherche",
            description="Recherche à effectuer",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def google(ctx: interactions.CommandContext, recherche: str):
    google_api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = '20f02a5ebf8234b5f'
    url = f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={recherche}'
    response = requests.get(url)
    search_results = response.json()
    try:
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await ctx.send(f"{result['title']}: {result['link']}")
                print(f"Commande exécutée par {ctx.author.name}: Google. Recherche: {recherche}")
        else:
            await ctx.send('Aucun résultat trouvé.')
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        print(f"Une erreur s'est produite lors de la recherche: {e}")


@bot.command(
    name="wikipedia",
    description="Recherche sur Wikipedia",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="recherche",
            description="Recherche à effectuer",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def wikipedia(ctx: interactions.CommandContext, recherche: str):
    url = f'https://fr.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': recherche,
        'srlimit': 1,
    }
    response = requests.get(url, params=params)
    search_results = response.json()
    try:
        if 'query' in search_results and 'search' in search_results['query'] and search_results['query']['search']:
            article_title = search_results['query']['search'][0]['title']
            article_url = f'https://fr.wikipedia.org/wiki/{article_title.replace(" ", "_")}'
            await ctx.send(f'Voici un lien vers l\'article Wikipedia correspondant: {article_url}')
            print(f"Commande exécutée par {ctx.author.name}: Wikipedia. Recherche: {recherche}")
        else:
            await ctx.send('Aucun résultat trouvé sur Wikipédia.')
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        print(f"Une erreur s'est produite lors de la recherche: {e}")
    
@bot.command(
    name="wiki",
    description="Recherche sur le Wiki",
    scope=GUILD_ID,
    options=[
        interactions.Option(
            name="recherche",
            description="Recherche à effectuer",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def wiki(ctx: interactions.CommandContext, recherche: str):
    try:
        search_results = search_google(recherche)
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await ctx.send(f"{result['title']}: {result['link']}")
        else:
            await ctx.send('Aucun résultat trouvé.')
            print(f"Commande exécutée par {ctx.author.name}: Wiki. Recherche: {recherche}")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche: {e}")
        print(f"Une erreur s'est produite lors de la recherche: {e}")

def search_google(query: str):
    google_api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = '20f02a5ebf8234b5f'
    url = f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}'
    response = requests.get(url)
    return response.json()


bot.start()
