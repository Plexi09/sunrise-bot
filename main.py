import logging
import os
import time
import asyncio
import random
import aiohttp
import uuid
import json
from dotenv import load_dotenv
from datetime import datetime
import discord
from discord import Intents, app_commands
from discord.ext import commands

# Configuration du logger
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture detailed logs
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=(f'logs/discord_{timestamp}.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configuration du bot et des intents
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Définir l'encodage de sortie sur UTF-8
import sys
sys.stdout.reconfigure(encoding='utf-8')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    logger.info(f'Connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} commands')
        logger.info(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
        logger.error(f'Error syncing commands: {e}')

# Commande pour afficher l'IP du serveur
@bot.tree.command(name="ip", description="Affiche l'IP du serveur.", guild=discord.Object(id=GUILD_ID))
async def ip_function(interaction: discord.Interaction):
    await interaction.response.send_message('IP du serveur: `play.sunrisenetwork.eu`')
    logger.info(f"Commande exécutée par {interaction.user.name}: ip.")

# Commande pour afficher l'URL du site web
@bot.tree.command(name="web", description="Affiche l'URL du site web", guild=discord.Object(id=GUILD_ID))
async def web_function(interaction: discord.Interaction):
    await interaction.response.send_message('Site web du serveur: https://sunrisenetwork.eu')
    logger.info(f"Commande exécutée par {interaction.user.name}: web.")

# Commande pour répéter le message de l'utilisateur
@bot.tree.command(name="echo", description="Répète le message de l'utilisateur", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(text="Texte à répéter")
async def echo_function(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"{text}")
    logger.info(f"Commande exécutée par {interaction.user}: echo. Message: {text}")

# Commande pour afficher "Pong!" avec la latence
@bot.tree.command(name="ping", description="Pong", guild=discord.Object(id=GUILD_ID))
async def ping_function(interaction: discord.Interaction):
    start_time = time.perf_counter()
    message = await interaction.response.send_message('Pong!')
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # Convertir en millisecondes
    await interaction.edit_original_response(content=f'Pong! Latence: `{latency:.2f}ms`')
    logger.info(f"Commande exécutée par {interaction.user}: ping. Latence: `{latency:.2f}ms`")

# Commande pour effectuer un benchmark de latence
@bot.tree.command(name="benchmark", description="Mesure de la latence du bot", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(duration="Durée du benchmark en secondes")
async def benchmark_function(interaction: discord.Interaction, duration: int):
    enabled = False
    if enabled:
        logger.info(f"Démarrage du benchmark par {interaction.user}")
        latencies = []

        start_time = time.time()
        while time.time() - start_time < duration:
            ping_start = time.perf_counter()
            message = await interaction.channel.send("Benchmarking...")
            await message.delete()
            ping_end = time.perf_counter()
            latency = (ping_end - ping_start) * 1000
            latencies.append(latency)
            await asyncio.sleep(1)

        if latencies:
            min_latency = min(latencies)
            max_latency = max(latencies)
            avg_latency = sum(latencies) / len(latencies)
            await interaction.response.send_message(f"Résultats du benchmark sur {duration} secondes:\n"
                                                    f"Latence Min: `{min_latency:.2f}ms`\n"
                                                    f"Latence Max: `{max_latency:.2f}ms`\n"
                                                    f"Latence Moyenne: `{avg_latency:.2f}ms`")
            logger.info(f"Fin du benchmark sur {duration} secondes. Latency min: `{min_latency:.2f}ms. Latency max: `{max_latency:.2f}ms. Latency avg: `{avg_latency:.2f}ms")
        else:
            await interaction.response.send_message("Aucune donnée de latence collectée.")
            logger.warning(f"Aucune donnée de latence collectée lors du benchmark par {interaction.user}")
    else:
        await interaction.response.send_message("Le benchmark désactivé.")

# Commande pour générer un nombre aléatoire entre min et max
@bot.tree.command(name="random", description="Génère un nombre aléatoire", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(min="Nombre minimum", max="Nombre maximum")
async def random_function(interaction: discord.Interaction, min: int, max: int):
    randomnumber = random.randint(min, max)
    await interaction.response.send_message(f"Nombre aléatoire: {randomnumber}")
    logger.info(f"Commande exécutée par {interaction.user}: random. Nombre aléatoire: {randomnumber}")

# Commande pour rechercher sur Google
@bot.tree.command(name="google", description="Recherche sur Google", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(recherche="Recherche à effectuer")
async def google_function(interaction: discord.Interaction, recherche: str):
    search_engine_id = '20f02a5ebf8234b5f'
    url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={search_engine_id}&q={recherche}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            search_results = await response.json()

    try:
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await interaction.response.send_message(f"{result['title']}: {result['link']}")
                logger.info(f"Commande exécutée par {interaction.user}: Google. Recherche: {recherche}")
        else:
            await interaction.response.send_message(f'Aucun résultat trouvé pour {recherche}.')
            logger.info(f"Aucun résultat trouvé pour la recherche '{recherche}' par {interaction.user}")
    except Exception as e:
        await interaction.response.send_message(f"Une erreur s'est produite lors de la recherche: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche: {e}")

# Commande pour rechercher sur le Wiki (Différente de /wikipedia)
@bot.tree.command(name="wiki", description="Recherche sur le Wiki", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(recherche="Recherche à effectuer")
async def google_function(interaction: discord.Interaction, recherche: str):
    search_engine_id = '567f0ad4fa4ff419d'
    url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={search_engine_id}&q={recherche}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            search_results = await response.json()

    try:
        if 'items' in search_results:
            for result in search_results['items'][:1]:
                await interaction.response.send_message(f"{result['title']}: {result['link']}")
                logger.info(f"Commande exécutée par {interaction.user}: Wiki. Recherche: {recherche}")
        else:
            await interaction.response.send_message(f'Aucun résultat trouvé pour {recherche}.')
            logger.info(f"Aucun résultat trouvé pour la recherche '{recherche}' par {interaction.user}")
    except Exception as e:
        await interaction.response.send_message(f"Une erreur s'est produite lors de la recherche: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche: {e}")

# Commande pour rechercher sur Wikipedia
@bot.tree.command(name="wikipedia", description="Recherche sur Wikipedia", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(recherche="Recherche à effectuer")
async def wikipedia_function(interaction: discord.Interaction, recherche: str):
    url = f'https://fr.wikipedia.org/w/api.php'
    params = {'action': 'query', 'format': 'json', 'list': 'search', 'srsearch': recherche, 'srlimit': 1}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            search_results = await response.json()

    try:
        if 'query' in search_results and 'search' in search_results['query'] and search_results['query']['search']:
            article_title = search_results['query']['search'][0]['title']
            article_url = f'https://fr.wikipedia.org/wiki/{article_title.replace(" ", "_")}'
            await interaction.response.send_message(f'Voici un lien vers l\'article Wikipedia correspondant: {article_url}')
            logger.info(f"Commande exécutée par {interaction.user}: Wikipedia. Recherche: {recherche}. Article: {article_title}")
        else:
            await interaction.response.send_message(f'Aucun résultat trouvé pour {recherche}.')
            logger.info(f"Aucun résultat trouvé sur Wikipedia pour la recherche '{recherche}' par {interaction.user}")
    except Exception as e:
        await interaction.response.send_message(f"Une erreur s'est produite lors de la recherche sur Wikipedia: {e}")
        logger.error(f"Une erreur s'est produite lors de la recherche sur Wikipedia: {e}")

# Context Menu pour signaler un message
@bot.tree.context_menu(name="Signaler", guild=discord.Object(id=GUILD_ID))
async def report(interaction: discord.Interaction, message: discord.Message):
    if interaction.guild is None:
        await interaction.response.send_message("Cette commande ne peut pas être utilisée dans les messages privés.", ephemeral=True)
        return

    member = message.author
    target_channel_id = 1248358610455629824
    target_channel = interaction.guild.get_channel(target_channel_id)
    message_link = f"https://discord.com/channels/{interaction.guild.id}/{message.channel.id}/{message.id}"
    staff_role = 1131596251650068521

    # Générer un UUID pour le signalement
    report_uuid = uuid.uuid4()

    # Créer un fichier JSON pour les signalements
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_data = {
        "uuid": str(report_uuid),
        "reporter_id": interaction.user.id,
        "reported_message_id": message.id,
        "reported_message_content": message.content,
        "reported_message_author_id": member.id,
        "guild_id": interaction.guild.id,
        "channel_id": message.channel.id,
        "message_link": message_link,
        "date": timestamp
    }

    # Charger les signalements existants
    try:
        with open("reports.json", "r", encoding="utf-8") as file:
            try:
                reports = json.load(file)
            except json.JSONDecodeError:
                reports = []  # Fichier vide ou corrompu
    except FileNotFoundError:
        reports = []  # Fichier non trouvé

    # Ajouter le nouveau signalement
    reports.append(report_data)

    # Enregistrer les signalements mis à jour
    with open("reports.json", "w", encoding="utf-8") as file:
        json.dump(reports, file, indent=4, ensure_ascii=False)

    # Envoyer un message dans salon de signalements et en MP
    if target_channel:
        report_message = (
            f"🚨 Nouveau signalement par {interaction.user.mention} 🚨\n\n"
            f"UUID du signalement: {report_uuid}\n\n"
            f"Message signalé:\n"
            f"`{message.content}`\n\n"
            f"Auteur du message: {member.mention}\n"
            f"Lien du message: {message_link}\n"
            f"<@&{staff_role}>"
        )
        dm_message = (
            f"Merci pour votre signalement. Notre équipe de modération va examiner le message.\n"
            f"UUID du signalement: {report_uuid}\n\n"
            f"Message signalé:\n"
            f"`{message.content}`\n\n"
            f"Auteur du message: {member.mention}\n"
            f"Lien du message: {message_link}\n"
        )

        await target_channel.send(report_message)
        await interaction.response.send_message("Merci pour votre signalement. Notre équipe de modération va examiner le message.", ephemeral=True)

        # Envoyer un message privé à l'utilisateur qui a fait le signalement
        try:
            await interaction.user.send(dm_message)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message privé: {e}")
    else:
        await interaction.response.send_message("Le salon cible n'a pas été trouvé.")

# Démarrage du bot
bot.run(BOT_TOKEN)
