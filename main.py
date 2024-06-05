from dotenv import load_dotenv
import os
import interactions
import time
import asyncio
import random

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# Configuration du bot et des intents
bot = interactions.Client(token=BOT_TOKEN)

@bot.event
async def on_ready():
    print(f'Connecté en tant que ')


@bot.command(
    name="ip",
    description="Affiche l'IP du serveur",
    scope=GUILD_ID,
)
async def ip(ctx: interactions.CommandContext):
    await ctx.send('IP du serveur: `play.sunrisenetwork.eu`')
    print("Commande exécutée: ping")


@bot.command(
    name="web",
    description="Affiche l'URL du site web",
    scope=GUILD_ID,
)
async def ip(ctx: interactions.CommandContext):
    await ctx.send('Site web du serveur: https://sunrisenetwork.eu')
    print("Commande exécutée: web")


@bot.command(
    name="echo",
    description="Répète le message de l'utilisateur",
    scope=GUILD_ID,
    options = [
        interactions.Option(
            name="text",
            description="Texte a répéter",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def echo(ctx: interactions.CommandContext, text: str):
    await ctx.send(f"{text}")

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
        await ctx.send("Benchmarking...")
        await ctx.message.delete()
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
    await random_number(ctx, min, max)
async def random_number(ctx: interactions.CommandContext, min_value: int, max_value: int):
    await ctx.send(f"Nombre aléatoire: {random.randint(min_value, max_value)}")


# Démarrage du bot
bot.start()
