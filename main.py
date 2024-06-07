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
import interactions
from interactions import (
    slash_command,
    SlashContext,
    OptionType,
    slash_option,
    ContextMenuContext,
    Message, 
    message_context_menu,
    user_context_menu,
    Member
)

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
@slash_option(name="text", description="Texte à répéter", opt_type=OptionType.STRING, required=True)
async def echo_function(ctx: SlashContext, text: str):
    await ctx.send(f"{text}")
    logger.info(f"Commande exécutée par {ctx.author}: echo. Message: {text}")

@user_context_menu(name="mention")
async def ping(ctx: ContextMenuContext):
    member: Member = ctx.target
    await ctx.send(member.mention)

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
@slash_option(name="duration", description="Durée du benchmark en secondes" ,opt_type=OptionType.INTEGER, required=True,)
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
@slash_option(name="min", description="Nombre minimum", opt_type=OptionType.INTEGER, required=True)
@slash_option(name="max", description="Nombre maximum", opt_type=OptionType.INTEGER, required=True)
async def random_function(ctx: SlashContext, min: int, max: int):
    randomnumber = random.randint(min, max)
    await ctx.send(f"Nombre aléatoire: {randomnumber}")
    logger.info(f"Commande exécutée par {ctx.author}: random. Nombre aléatoire: {randomnumber}")

# Commande pour rechercher sur Google
@slash_command(name="google",description="Recherche sur Google")
@slash_option(name="recherche", description="Recherche à effectuer", opt_type=OptionType.STRING, required=True)
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
@slash_option(name="recherche", description="Recherche à effectuer", opt_type=OptionType.STRING, required=True)
async def wikipedia_function(ctx: SlashContext, recherche: str):
    url = f'https://fr.wikipedia.org/w/api.php'
    params = {'action': 'query', 'format': 'json', 'list': 'search', 'srsearch': recherche, 'srlimit': 1}

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
@slash_option(name="recherche", description="Recherche à effectuer", opt_type=OptionType.STRING, required=True)
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

@message_context_menu(name="Signaler")
async def repeat(ctx: ContextMenuContext):
    if ctx.guild is None:
        await ctx.send("Cette commande ne peut pas être utilisée dans les messages privés.", ephemeral=True)
        return

    message: Message = ctx.target
    member: Member = message.author  # Obtention de l'auteur du message
    target_channel_id = 1248358610455629824  # Remplacez par l'ID de votre salon spécifique
    target_channel = ctx.guild.get_channel(target_channel_id)
    message_link = f"https://discord.com/channels/{ctx.guild.id}/{message.channel.id}/{message.id}"
    staff_role = 1131596251650068521

    # Générer un UUID pour le signalement
    report_uuid = uuid.uuid4()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_data = {
        "uuid": str(report_uuid),
        "reporter_id": ctx.author.id,
        "reported_message_id": message.id,
        "reported_message_content": message.content,
        "reported_message_author_id": member.id,
        "guild_id": ctx.guild.id,
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

    if target_channel:
        report_message = (
            f"🚨 Nouveau signalement par {ctx.author.mention} 🚨\n\n"
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
        await ctx.send("Merci pour votre signalement. Notre équipe de modération va examiner le message.", ephemeral=True)
        
        # Envoyer un message privé à l'utilisateur qui a fait le signalement
        try:
            await ctx.author.send(dm_message)
        except Exception as e:
            print(f"Erreur lors de l'envoi du message privé: {e}")
    else:
        await ctx.send("Le salon cible n'a pas été trouvé.")

# Démarrage du bot
bot.start()