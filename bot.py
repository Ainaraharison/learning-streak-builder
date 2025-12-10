"""
Learning Streak Builder - Bot Discord
Un bot pour suivre et gamifier votre apprentissage quotidien
"""

import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta
import asyncio
import random
import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

# Import du module de base de données
from database import (
    init_db,
    get_user,
    create_user as db_create_user,
    update_user_streak,
    update_user_points,
    insert_learning_log,
    insert_badge,
    get_user_badges,
    count_user_logs,
    count_unique_subjects,
    get_daily_challenge,
    insert_daily_challenge,
    update_user_interests,
    execute_query,
    DatabaseConnection
)

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Initialise Groq
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Configuration
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour lire les commandes
# intents.members = True  # Désactivé - nécessite Privileged Intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Système de badges
BADGES = {
    'first_step': {'name': '🌱 Premier Pas', 'description': 'Première session loguée'},
    'week_warrior': {'name': '🔥 Guerrier Hebdomadaire', 'description': '7 jours consécutifs'},
    'month_master': {'name': '🏆 Maître du Mois', 'description': '30 jours consécutifs'},
    'century': {'name': '💯 Centurion', 'description': '100 sessions au total'},
    'explorer': {'name': '🗺️ Explorateur', 'description': 'Explorer 10 sujets différents'},
    'dedicated': {'name': '⚡ Dédié', 'description': 'Atteindre le niveau 5'},
    'marathon': {'name': '🎯 Marathon', 'description': '50 jours consécutifs'},
    'polymath': {'name': '🧠 Polymathe', 'description': 'Explorer 25 sujets différents'},
}

# Catégories de défis
CHALLENGE_CATEGORIES = {
    'science': [
        "Recherche comment fonctionne la physique quantique",
        "Découvre les dernières avancées en biologie cellulaire",
        "Explore le concept de l'espace-temps",
        "Apprends comment fonctionne l'ADN",
        "Étudie le principe de la relativité"
    ],
    'technologie': [
        "Découvre ce qu'est le machine learning",
        "Explore les bases de la blockchain",
        "Apprends un nouveau langage de programmation",
        "Comprends comment fonctionne l'Internet",
        "Étudie les algorithmes de tri"
    ],
    'histoire': [
        "Découvre un événement historique majeur du 20e siècle",
        "Explore l'histoire d'une civilisation ancienne",
        "Apprends sur la révolution industrielle",
        "Étudie les causes d'une guerre mondiale",
        "Recherche l'histoire de ton pays"
    ],
    'art': [
        "Découvre un mouvement artistique",
        "Explore l'œuvre d'un artiste célèbre",
        "Apprends sur l'histoire de la musique classique",
        "Étudie les techniques de peinture",
        "Découvre l'architecture gothique"
    ],
    'philosophie': [
        "Explore un courant philosophique",
        "Lis sur Socrate et ses idées",
        "Découvre l'existentialisme",
        "Apprends sur l'éthique et la morale",
        "Étudie le stoïcisme"
    ],
    'langues': [
        "Apprends 10 nouveaux mots dans une langue étrangère",
        "Découvre l'origine d'expressions courantes",
        "Explore la linguistique",
        "Pratique la prononciation d'une nouvelle langue",
        "Étudie la grammaire d'une langue"
    ]
}

def create_user(user_id: int, username: str):
    """Crée un nouvel utilisateur"""
    now = datetime.now().isoformat()
    db_create_user(user_id, username, now)

def update_streak(user_id: int):
    """Met à jour le streak de l'utilisateur"""
    user = get_user(user_id)
    if not user:
        return 0
    
    current_streak = user[2]
    longest_streak = user[3]
    last_log_date = user[6]
    
    today = datetime.now().date()
    
    if last_log_date:
        last_date = datetime.fromisoformat(last_log_date).date()
        days_diff = (today - last_date).days
        
        if days_diff == 0:
            # Déjà loggué aujourd'hui
            new_streak = current_streak
        elif days_diff == 1:
            # Continuation du streak
            new_streak = current_streak + 1
        else:
            # Streak cassé
            new_streak = 1
    else:
        new_streak = 1
    
    # Mise à jour du longest streak
    new_longest = max(longest_streak, new_streak)
    
    update_user_streak(user_id, new_streak, new_longest, today.isoformat())
    
    return new_streak

def calculate_points(duration: int, streak: int) -> int:
    """Calcule les points gagnés"""
    base_points = duration * 10  # 10 points par minute
    streak_bonus = streak * 5  # Bonus basé sur le streak
    return base_points + streak_bonus

def calculate_level(total_points: int) -> int:
    """Calcule le niveau basé sur les points"""
    # Niveau = racine carrée des points divisé par 100
    return max(1, int((total_points / 100) ** 0.5))

def check_and_award_badges(user_id: int, username: str):
    """Vérifie et attribue les badges"""
    user = get_user(user_id)
    if not user:
        return []
    
    current_streak = int(user[2])
    longest_streak = int(user[3])
    total_points = int(user[4])
    level = int(user[5])
    
    # Compte le nombre de logs et sujets uniques
    total_logs = count_user_logs(user_id)
    unique_subjects = count_unique_subjects(user_id)
    
    # Vérifie quels badges l'utilisateur a déjà
    earned_badge_names = get_user_badges(user_id)
    
    new_badges = []
    
    # Vérification des conditions
    if total_logs == 1 and 'first_step' not in earned_badge_names:
        new_badges.append('first_step')
    
    if current_streak >= 7 and 'week_warrior' not in earned_badge_names:
        new_badges.append('week_warrior')
    
    if current_streak >= 30 and 'month_master' not in earned_badge_names:
        new_badges.append('month_master')
    
    if current_streak >= 50 and 'marathon' not in earned_badge_names:
        new_badges.append('marathon')
    
    if total_logs >= 100 and 'century' not in earned_badge_names:
        new_badges.append('century')
    
    if unique_subjects >= 10 and 'explorer' not in earned_badge_names:
        new_badges.append('explorer')
    
    if unique_subjects >= 25 and 'polymath' not in earned_badge_names:
        new_badges.append('polymath')
    
    if level >= 5 and 'dedicated' not in earned_badge_names:
        new_badges.append('dedicated')
    
    # Attribuer les nouveaux badges
    now = datetime.now().isoformat()
    for badge_key in new_badges:
        badge = BADGES[badge_key]
        insert_badge(user_id, badge['name'], badge['description'], now)
    
    return new_badges

@bot.event
async def on_ready():
    """Événement au démarrage du bot"""
    init_db()
    print(f'{bot.user} est connecté et prêt!')
    print(f'Connecté à {len(bot.guilds)} serveur(s)')
    
    # Lance la tâche de rappel quotidien
    daily_reminder.start()
    
    # Génère le défi du jour
    generate_daily_challenge.start()

async def get_ai_response(user_message: str, user_id: int) -> str:
    """Obtient une réponse IA via Groq"""
    try:
        # Récupère les infos de l'utilisateur pour personnaliser la réponse
        user = get_user(user_id)
        user_context = ""
        if user:
            user_context = f"""
Informations de l'utilisateur :
- Streak actuel : {user[2]} jours
- Meilleur streak : {user[3]} jours
- Points : {user[4]}
- Niveau : {user[5]}
"""
        
        system_prompt = f"""Tu es Learning Streak Builder, un assistant d'apprentissage motivant et sympathique sur Discord. 

Ton rôle :
- Aider les utilisateurs à rester réguliers dans leur apprentissage
- Les motiver et encourager
- Répondre à leurs questions sur l'apprentissage
- Leur rappeler les commandes disponibles quand c'est pertinent

Commandes disponibles :
- !start - S'inscrire
- !log <sujet> <minutes> <description> - Logger une session
- !stats - Voir les statistiques
- !challenge - Défi du jour
- !badges - Voir les badges
- !suggest - Suggestion personnalisée
- !interests - Définir ses centres d'intérêt
- !leaderboard - Classement

{user_context}

Réponds de façon naturelle, amicale et motivante. Utilise des emojis appropriés. 
Si la question concerne les fonctionnalités du bot, mentionne les commandes pertinentes.
Garde tes réponses concises (2-3 phrases maximum) sauf si on te demande des détails."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Erreur Groq: {e}")
        # Réponse de secours si l'API échoue
        return "😊 Je suis là pour t'aider dans ton apprentissage ! Tape `!help` pour voir toutes mes commandes ou pose-moi une question ! 📚"

@bot.event
async def on_message(message):
    """Gère les messages et conversations"""
    if message.author == bot.user:
        return
    
    print(f"📩 Message reçu de {message.author}: {message.content}")
    
    # Si c'est une commande, la traiter
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    # Vérifie si le bot est mentionné
    bot_mentioned = bot.user in message.mentions
    
    # Si le bot n'est pas mentionné, ignorer
    if not bot_mentioned:
        return
    
    # Retire la mention du texte
    user_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
    
    # Si le message est vide après avoir retiré la mention
    if not user_message:
        await message.channel.send(f"👋 Salut {message.author.mention} ! Comment puis-je t'aider ? 😊")
        return
    
    # Montre que le bot est en train de taper
    async with message.channel.typing():
        # Obtient la réponse de l'IA
        ai_response = await get_ai_response(user_message, message.author.id)
        await message.channel.send(f"{message.author.mention} {ai_response}")
    
    # Traite quand même les commandes au cas où
    await bot.process_commands(message)

@bot.command(name='start')
async def start(ctx):
    """Commande pour s'inscrire au Learning Streak Builder"""
    user = get_user(ctx.author.id)
    
    if user:
        embed = discord.Embed(
            title="🎓 Bienvenue de nouveau!",
            description=f"Tu es déjà inscrit, {ctx.author.name}! Continue ton apprentissage!",
            color=discord.Color.blue()
        )
    else:
        create_user(ctx.author.id, ctx.author.name)
        embed = discord.Embed(
            title="🎉 Bienvenue au Learning Streak Builder!",
            description=f"""
            Félicitations {ctx.author.name}! Tu as rejoint la communauté des apprenants!
            
            **Commandes disponibles:**
            • `!log <sujet> <durée> <description>` - Logger une session
            • `!stats` - Voir tes statistiques
            • `!challenge` - Voir le défi du jour
            • `!leaderboard` - Voir le classement
            • `!badges` - Voir tes badges
            • `!interests <sujets>` - Définir tes centres d'intérêt
            • `!help` - Aide complète
            
            **Commence dès maintenant avec `!log` pour logger ta première session!**
            """,
            color=discord.Color.green()
        )
    
    await ctx.send(embed=embed)

@bot.command(name='log')
async def log_session(ctx, subject: str, duration: int, *, description: str = ""):
    """Logger une session d'apprentissage"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    if duration <= 0:
        await ctx.send("❌ La durée doit être supérieure à 0 minutes")
        return
    
    # Mise à jour du streak
    new_streak = update_streak(ctx.author.id)
    
    # Calcul des points
    points = calculate_points(duration, new_streak)
    
    # Ajoute les points
    new_total = user[4] + points
    new_level = calculate_level(new_total)
    
    update_user_points(ctx.author.id, new_total, new_level)
    
    # Log la session
    now = datetime.now().isoformat()
    insert_learning_log(ctx.author.id, subject, description, duration, now, points)
    
    # Vérifier les badges
    new_badges = check_and_award_badges(ctx.author.id, ctx.author.name)
    
    # Message de confirmation
    embed = discord.Embed(
        title="✅ Session loguée avec succès!",
        color=discord.Color.green()
    )
    embed.add_field(name="📚 Sujet", value=subject, inline=True)
    embed.add_field(name="⏱️ Durée", value=f"{duration} min", inline=True)
    embed.add_field(name="🎯 Points gagnés", value=f"+{points}", inline=True)
    embed.add_field(name="🔥 Streak actuel", value=f"{new_streak} jour(s)", inline=True)
    embed.add_field(name="📊 Niveau", value=f"{new_level}", inline=True)
    embed.add_field(name="💰 Total points", value=f"{new_total}", inline=True)
    
    if description:
        embed.add_field(name="📝 Description", value=description, inline=False)
    
    if new_badges:
        badges_text = "\n".join([f"{BADGES[b]['name']} - {BADGES[b]['description']}" for b in new_badges])
        embed.add_field(name="🏆 Nouveaux Badges!", value=badges_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def show_stats(ctx, member: Optional[discord.Member] = None):
    """Affiche les statistiques d'un utilisateur"""
    target = member or ctx.author
    user = get_user(target.id)
    
    if not user:
        await ctx.send(f"❌ {target.name} n'est pas encore inscrit!")
        return
    
    # Compte les logs
    log_stats = execute_query(
        'SELECT COUNT(*), SUM(duration), COUNT(DISTINCT subject) FROM learning_logs WHERE user_id = {ph}',
        (target.id,),
        fetch_one=True
    )
    total_logs = log_stats[0] if log_stats else 0
    total_minutes = log_stats[1] if log_stats and log_stats[1] else 0
    unique_subjects = log_stats[2] if log_stats else 0
    
    # Top 3 sujets
    top_subjects = execute_query(
        '''SELECT subject, COUNT(*) as count FROM learning_logs 
           WHERE user_id = {ph} GROUP BY subject ORDER BY count DESC LIMIT 3''',
        (target.id,),
        fetch_all=True
    )
    
    # Badges
    badge_result = execute_query(
        'SELECT COUNT(*) FROM badges WHERE user_id = {ph}',
        (target.id,),
        fetch_one=True
    )
    badge_count = badge_result[0] if badge_result else 0
    
    embed = discord.Embed(
        title=f"📊 Statistiques de {target.name}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🔥 Streak actuel", value=f"{user[2]} jour(s)", inline=True)
    embed.add_field(name="🏆 Meilleur streak", value=f"{user[3]} jour(s)", inline=True)
    embed.add_field(name="📊 Niveau", value=f"{user[5]}", inline=True)
    embed.add_field(name="💰 Total points", value=f"{user[4]}", inline=True)
    embed.add_field(name="📚 Sessions totales", value=f"{total_logs}", inline=True)
    embed.add_field(name="🏅 Badges", value=f"{badge_count}/{len(BADGES)}", inline=True)
    embed.add_field(name="⏱️ Temps total", value=f"{total_minutes} min ({total_minutes//60}h{total_minutes%60})", inline=True)
    embed.add_field(name="🗺️ Sujets explorés", value=f"{unique_subjects}", inline=True)
    
    if top_subjects:
        top_text = "\n".join([f"**{i+1}.** {subj[0]} ({subj[1]} sessions)" for i, subj in enumerate(top_subjects)])
        embed.add_field(name="🎯 Top sujets", value=top_text, inline=False)
    
    if user[7]:
        embed.add_field(name="📅 Membre depuis", value=datetime.fromisoformat(user[7]).strftime("%d/%m/%Y"), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='badges')
async def show_badges(ctx):
    """Affiche tous les badges de l'utilisateur"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    earned_badges = execute_query(
        'SELECT badge_name, badge_description, earned_date FROM badges WHERE user_id = {ph}',
        (ctx.author.id,),
        fetch_all=True
    )
    
    embed = discord.Embed(
        title=f"🏆 Badges de {ctx.author.name}",
        description=f"**{len(earned_badges)}/{len(BADGES)} badges débloqués**",
        color=discord.Color.gold()
    )
    
    if earned_badges:
        for badge in earned_badges:
            date = datetime.fromisoformat(badge[2]).strftime("%d/%m/%Y")
            embed.add_field(name=badge[0], value=f"{badge[1]}\n*Obtenu le {date}*", inline=True)
    else:
        embed.add_field(name="Aucun badge", value="Continue à apprendre pour débloquer des badges!", inline=False)
    
    # Badges non obtenus
    earned_names = [b[0] for b in earned_badges]
    missing = [f"{v['name']} - {v['description']}" for k, v in BADGES.items() if v['name'] not in earned_names]
    
    if missing:
        embed.add_field(name="🔒 À débloquer", value="\n".join(missing[:5]), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='challenge')
async def daily_challenge(ctx):
    """Affiche le défi du jour généré par IA"""
    today = datetime.now().date().isoformat()
    challenge = get_daily_challenge(today)
    
    if not challenge:
        # Génère un nouveau défi avec l'IA
        async with ctx.channel.typing():
            try:
                # Récupère les infos de l'utilisateur pour personnaliser
                user = get_user(ctx.author.id)
                user_context = ""
                user_stats = ""
                
                if user:
                    # Récupère les statistiques de l'utilisateur
                    streak = user[2]
                    level = user[5]
                    user_stats = f"\nNiveau de l'utilisateur : {level}, Streak actuel : {streak} jours"
                    
                    if user[8]:  # Si l'utilisateur a des intérêts
                        try:
                            interests = json.loads(user[8])
                            if interests:
                                user_context = f"\nCentres d'intérêt : {', '.join(interests)}"
                        except:
                            pass
                
                category = random.choice(list(CHALLENGE_CATEGORIES.keys()))
                
                prompt = f"""Crée un défi d'apprentissage unique, original et motivant pour la catégorie : {category}

IMPORTANT : Ne propose PAS de défis génériques ou trop vus. Sois créatif et original !
{user_context}{user_stats}

Le défi doit :
- Être complètement nouveau et créatif (évite les sujets trop classiques)
- Être réalisable en 15-30 minutes
- Être concret, actionnable et précis
- Susciter la curiosité et l'envie d'explorer
- Inclure un aspect pratique ou interactif si possible
- Être adapté au niveau de l'utilisateur

Exemples de ce qu'on VEUT (originalité) :
- "Découvre comment les algorithmes de compression permettent aux images de tenir sur ton téléphone"
- "Explore pourquoi les chats ont été vénérés dans l'Égypte ancienne et leur impact culturel"
- "Apprends les 5 biais cognitifs qui influencent tes décisions quotidiennes"

Exemples de ce qu'on NE VEUT PAS (trop générique) :
- "Apprends un langage de programmation"
- "Découvre l'histoire ancienne"
- "Étudie la philosophie"

Réponds UNIQUEMENT avec :
Ligne 1 : Le défi (une phrase claire, précise et engageante)
Ligne 2 : (vide)
Ligne 3+ : Une explication captivante (2-4 phrases) expliquant pourquoi c'est fascinant et comment commencer

Format:
[Défi précis et original]

[Explication captivante avec des détails intéressants]"""

                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en pédagogie créative qui invente des défis d'apprentissage originaux, fascinants et peu conventionnels. Tu évites les sujets génériques et préfères les angles inattendus et captivants."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,
                    max_tokens=450
                )
                
                ai_response = response.choices[0].message.content.strip()
                
                # Sépare le défi et l'explication
                if '\n\n' in ai_response:
                    parts = ai_response.split('\n\n', 1)
                    challenge_text = parts[0]
                    explanation = parts[1] if len(parts) > 1 else ""
                elif '\n' in ai_response:
                    parts = ai_response.split('\n', 1)
                    challenge_text = parts[0]
                    explanation = parts[1] if len(parts) > 1 else ""
                else:
                    challenge_text = ai_response
                    explanation = ""
                
                # Sauvegarde dans la base de données
                full_challenge = f"{challenge_text}\n\n{explanation}" if explanation else challenge_text
                insert_daily_challenge(full_challenge, category, today)
                
            except Exception as e:
                print(f"Erreur lors de la génération du défi: {e}")
                # Fallback sur l'ancien système
                challenge_text = random.choice(CHALLENGE_CATEGORIES[category])
                explanation = ""
                
                insert_daily_challenge(challenge_text, category, today)
    else:
        full_text = challenge[0]
        category = challenge[1]
        
        # Sépare le défi et l'explication si possible
        if '\n\n' in full_text:
            parts = full_text.split('\n\n', 1)
            challenge_text = parts[0]
            explanation = parts[1]
        elif '\n' in full_text:
            parts = full_text.split('\n', 1)
            challenge_text = parts[0]
            explanation = parts[1]
        else:
            challenge_text = full_text
            explanation = ""
    
    embed = discord.Embed(
        title="🎯 Défi du Jour",
        description=challenge_text,
        color=discord.Color.purple()
    )
    embed.add_field(name="Catégorie", value=f"📖 {category.capitalize()}", inline=False)
    
    if explanation:
        embed.add_field(name="💡 Pourquoi ce défi?", value=explanation, inline=False)
    
    embed.add_field(name="Comment participer?", value="Explore ce sujet et logue ta session avec `!log`", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Affiche le classement des utilisateurs"""
    top_users = execute_query(
        '''SELECT username, current_streak, longest_streak, total_points, level 
           FROM users ORDER BY total_points DESC LIMIT 10''',
        fetch_all=True
    )
    
    if not top_users:
        await ctx.send("❌ Aucun utilisateur dans le classement")
        return
    
    embed = discord.Embed(
        title="🏆 Classement des Apprenants",
        description="Top 10 des apprenants les plus actifs",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        embed.add_field(
            name=f"{medal} {user[0]}",
            value=f"Niveau {user[4]} • {user[3]} pts • Streak: {user[1]} 🔥",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='interests')
async def set_interests(ctx, *, interests: str):
    """Définir ses centres d'intérêt (séparés par des virgules)"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    interest_list = [i.strip() for i in interests.split(',')]
    interest_json = json.dumps(interest_list)
    
    update_user_interests(ctx.author.id, interest_json)
    
    embed = discord.Embed(
        title="✅ Centres d'intérêt mis à jour!",
        description="Tes centres d'intérêt: " + ", ".join(interest_list),
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='suggest')
async def suggest_topic(ctx):
    """Suggère un sujet d'apprentissage personnalisé avec l'IA"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    interests = json.loads(user[8]) if user[8] else []
    
    if not interests:
        await ctx.send("❌ Définis d'abord tes intérêts avec `!interests <sujets>`")
        return
    
    # Récupère l'historique récent d'apprentissage
    recent_results = execute_query(
        '''SELECT subject FROM learning_logs 
           WHERE user_id = {ph} ORDER BY log_date DESC LIMIT 5''',
        (ctx.author.id,),
        fetch_all=True
    )
    recent_subjects = [row[0] for row in recent_results] if recent_results else []
    
    # Montre que le bot réfléchit
    async with ctx.typing():
        try:
            # Génère une suggestion personnalisée avec l'IA
            prompt = f"""Suggère un sujet d'apprentissage précis et concret pour quelqu'un qui s'intéresse à : {', '.join(interests)}.

Contexte de l'utilisateur :
- Niveau : {user[5]}
- Streak : {user[2]} jours
- Sujets récemment étudiés : {', '.join(recent_subjects) if recent_subjects else 'Aucun'}

Donne UNE suggestion d'apprentissage :
1. Un sujet précis et actionnable (pas générique)
2. Adapté à son niveau actuel
3. Différent de ce qu'il a récemment étudié
4. Avec une courte explication (1-2 phrases) de pourquoi c'est intéressant
5. Un conseil pratique pour commencer

Format : 
Sujet : [titre précis]
Pourquoi : [explication courte]
Comment commencer : [conseil pratique]"""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es un conseiller d'apprentissage expert qui donne des suggestions précises et personnalisées."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=400
            )
            
            ai_suggestion = response.choices[0].message.content
            
            embed = discord.Embed(
                title="💡 Suggestion ",
                description=ai_suggestion,
                color=discord.Color.blue()
            )
            embed.add_field(name="🎯 Tes intérêts", value=", ".join(interests), inline=False)
            if recent_subjects:
                embed.add_field(name="📚 Sujets récents", value=", ".join(recent_subjects[:3]), inline=False)
            embed.set_footer(text="💪 Prêt à apprendre ? Utilise !log pour enregistrer ta session !")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erreur IA suggestion: {e}")
            # Fallback sur l'ancien système si l'IA échoue
            categories = list(CHALLENGE_CATEGORIES.keys())
            matching_categories = [cat for cat in categories if any(interest.lower() in cat for interest in interests)]
            
            if matching_categories:
                category = random.choice(matching_categories)
            else:
                category = random.choice(categories)
            
            suggestion = random.choice(CHALLENGE_CATEGORIES[category])
            
            embed = discord.Embed(
                title="💡 Suggestion d'Apprentissage",
                description=suggestion,
                color=discord.Color.blue()
            )
            embed.add_field(name="Catégorie", value=f"📖 {category.capitalize()}", inline=False)
            embed.add_field(name="Tes intérêts", value=", ".join(interests), inline=False)
            
            await ctx.send(embed=embed)

@bot.command(name='history')
async def show_history(ctx, limit: int = 5):
    """Affiche l'historique des sessions"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    logs = execute_query(
        '''SELECT subject, description, duration, log_date, points_earned 
           FROM learning_logs WHERE user_id = {ph} ORDER BY log_date DESC LIMIT {ph}''',
        (ctx.author.id, min(limit, 10)),
        fetch_all=True
    )
    
    if not logs:
        await ctx.send("❌ Aucune session enregistrée")
        return
    
    embed = discord.Embed(
        title=f"📚 Historique de {ctx.author.name}",
        description=f"Dernières {len(logs)} sessions",
        color=discord.Color.blue()
    )
    
    for log in logs:
        date = datetime.fromisoformat(log[3]).strftime("%d/%m/%Y %H:%M")
        desc = log[1][:50] + "..." if len(log[1]) > 50 else log[1]
        embed.add_field(
            name=f"📖 {log[0]}",
            value=f"{desc}\n⏱️ {log[2]} min • 🎯 {log[4]} pts • 📅 {date}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@tasks.loop(hours=24)
async def daily_reminder():
    """Rappel quotidien pour ceux qui n'ont pas loggué aujourd'hui"""
    await bot.wait_until_ready()
    
    today = datetime.now().date().isoformat()
    inactive_users = execute_query(
        'SELECT user_id, username, current_streak FROM users WHERE last_log_date != {ph} OR last_log_date IS NULL',
        (today,),
        fetch_all=True
    )
    
    for user_data in inactive_users:
        user_id, username, streak = user_data
        try:
            user = await bot.fetch_user(user_id)
            
            embed = discord.Embed(
                title="⏰ Rappel d'Apprentissage!",
                description=f"""
                Hey {username}! 👋
                
                Tu n'as pas encore loggué de session aujourd'hui!
                
                🔥 **Ton streak actuel: {streak} jour(s)**
                
                Ne le perds pas! Prends quelques minutes pour apprendre quelque chose de nouveau.
                Utilise `!challenge` pour voir le défi du jour ou `!suggest` pour une suggestion personnalisée.
                """,
                color=discord.Color.orange()
            )
            
            await user.send(embed=embed)
        except:
            # L'utilisateur a peut-être désactivé les DMs
            pass

@tasks.loop(hours=24)
async def generate_daily_challenge():
    """Génère un nouveau défi quotidien"""
    await bot.wait_until_ready()
    
    category = random.choice(list(CHALLENGE_CATEGORIES.keys()))
    challenge_text = random.choice(CHALLENGE_CATEGORIES[category])
    today = datetime.now().date().isoformat()
    
    # Vérifie si un défi existe déjà aujourd'hui
    existing = execute_query(
        'SELECT id FROM daily_challenges WHERE date = {ph}',
        (today,),
        fetch_one=True
    )
    if not existing:
        insert_daily_challenge(challenge_text, category, today)

@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant: {error.param.name}. Utilise `!help` pour plus d'infos.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Commande inconnue. Utilise `!help` pour voir toutes les commandes.")
    else:
        await ctx.send(f"❌ Une erreur est survenue: {str(error)}")

# Point d'entrée
if __name__ == '__main__':
    # Lit le token depuis une variable d'environnement ou un fichier config
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ Token Discord manquant!")
        print("Crée un fichier .env avec: DISCORD_BOT_TOKEN=ton_token")
        exit(1)
    
    bot.run(token)
