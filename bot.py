"""
Learning Streak Builder - Bot Discord
Un bot pour suivre et gamifier votre apprentissage quotidien
"""

import discord
from discord.ext import commands, tasks
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio
import random
import os
from typing import Optional
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour lire les commandes
# intents.members = True  # Désactivé - nécessite Privileged Intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Connexion à la base de données
def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    # Table des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        total_points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        last_log_date TEXT,
        created_at TEXT,
        interests TEXT
    )''')
    
    # Table des logs d'apprentissage
    c.execute('''CREATE TABLE IF NOT EXISTS learning_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        description TEXT,
        duration INTEGER,
        log_date TEXT,
        points_earned INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )''')
    
    # Table des badges
    c.execute('''CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        badge_name TEXT,
        badge_description TEXT,
        earned_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )''')
    
    # Table des défis du jour
    c.execute('''CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenge_text TEXT,
        category TEXT,
        date TEXT
    )''')
    
    conn.commit()
    conn.close()

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

def get_user(user_id: int):
    """Récupère les infos d'un utilisateur"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id: int, username: str):
    """Crée un nouvel utilisateur"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''INSERT INTO users (user_id, username, created_at, interests) 
                 VALUES (?, ?, ?, ?)''', (user_id, username, now, '[]'))
    conn.commit()
    conn.close()

def update_streak(user_id: int):
    """Met à jour le streak de l'utilisateur"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
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
    
    c.execute('''UPDATE users SET current_streak = ?, longest_streak = ?, last_log_date = ? 
                 WHERE user_id = ?''', (new_streak, new_longest, today.isoformat(), user_id))
    conn.commit()
    conn.close()
    
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
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    user = get_user(user_id)
    if not user:
        return []
    
    current_streak = int(user[2])
    longest_streak = int(user[3])
    total_points = int(user[4])
    level = int(user[5])
    
    # Compte le nombre de logs
    c.execute('SELECT COUNT(*) FROM learning_logs WHERE user_id = ?', (user_id,))
    total_logs = c.fetchone()[0]
    
    # Compte les sujets uniques
    c.execute('SELECT COUNT(DISTINCT subject) FROM learning_logs WHERE user_id = ?', (user_id,))
    unique_subjects = c.fetchone()[0]
    
    # Vérifie quels badges l'utilisateur a déjà
    c.execute('SELECT badge_name FROM badges WHERE user_id = ?', (user_id,))
    earned_badges = [row[0] for row in c.fetchall()]
    
    new_badges = []
    
    # Vérification des conditions
    if total_logs == 1 and 'first_step' not in earned_badges:
        new_badges.append('first_step')
    
    if current_streak >= 7 and 'week_warrior' not in earned_badges:
        new_badges.append('week_warrior')
    
    if current_streak >= 30 and 'month_master' not in earned_badges:
        new_badges.append('month_master')
    
    if current_streak >= 50 and 'marathon' not in earned_badges:
        new_badges.append('marathon')
    
    if total_logs >= 100 and 'century' not in earned_badges:
        new_badges.append('century')
    
    if unique_subjects >= 10 and 'explorer' not in earned_badges:
        new_badges.append('explorer')
    
    if unique_subjects >= 25 and 'polymath' not in earned_badges:
        new_badges.append('polymath')
    
    if level >= 5 and 'dedicated' not in earned_badges:
        new_badges.append('dedicated')
    
    # Attribuer les nouveaux badges
    now = datetime.now().isoformat()
    for badge_key in new_badges:
        badge = BADGES[badge_key]
        c.execute('''INSERT INTO badges (user_id, badge_name, badge_description, earned_date)
                     VALUES (?, ?, ?, ?)''', 
                  (user_id, badge['name'], badge['description'], now))
    
    conn.commit()
    conn.close()
    
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
    
    # Sinon, conversation naturelle
    content_lower = message.content.lower()
    
    # Salutations
    if any(word in content_lower for word in ['bonjour', 'salut', 'hello', 'hey', 'coucou', 'bonsoir']):
        await message.channel.send(f"👋 Salut {message.author.mention} ! Je suis le Learning Streak Builder, ton compagnon d'apprentissage ! Comment puis-je t'aider aujourd'hui ? 📚\n\n💡 Tape `!start` pour commencer ou `!help` pour voir toutes les commandes !")
        return
    
    # Questions sur le bot
    if any(word in content_lower for word in ['qui es-tu', 'qui es tu', 'what are you', 'c\'est quoi', "c'est quoi"]):
        await message.channel.send(f"🤖 Je suis un bot qui t'aide à rester régulier dans ton apprentissage ! Je te permets de :\n\n🔥 Suivre tes **streaks** quotidiens\n🎯 Gagner des **points** et des **badges**\n📊 Visualiser tes **statistiques**\n💡 Recevoir des **suggestions** et **défis**\n\nTape `!start` pour commencer ton aventure ! 🚀")
        return
    
    # Aide
    if any(word in content_lower for word in ['aide', 'help', 'comment', 'commandes']):
        await message.channel.send(f"📖 **Commandes principales :**\n\n`!start` - S'inscrire\n`!log <sujet> <minutes> <description>` - Logger une session\n`!stats` - Voir tes stats\n`!challenge` - Défi du jour\n`!badges` - Tes badges\n`!suggest` - Suggestion d'apprentissage\n`!leaderboard` - Classement\n\n💬 Tu peux aussi me parler normalement ! 😊")
        return
    
    # Motivation
    if any(word in content_lower for word in ['motivé', 'motivation', 'encouragement', 'fatigue', 'fatigué']):
        motivations = [
            "💪 Chaque petit pas compte ! Continue comme ça !",
            "🌟 Tu es sur la bonne voie ! L'apprentissage est un marathon, pas un sprint !",
            "🔥 Ne lâche rien ! Tes efforts d'aujourd'hui sont les succès de demain !",
            "⚡ Tu as déjà fait le plus dur : commencer ! Continue !",
            "🎯 Chaque jour d'apprentissage te rapproche de tes objectifs !"
        ]
        await message.channel.send(random.choice(motivations))
        return
    
    # Merci
    if any(word in content_lower for word in ['merci', 'thanks', 'thank you', 'cool', 'super', 'génial']):
        await message.channel.send(f"😊 Avec plaisir {message.author.mention} ! Continue à apprendre et à grandir ! 🚀")
        return
    
    # Questions sur l'apprentissage
    if any(word in content_lower for word in ['apprendre', 'étudier', 'learn', 'study']):
        await message.channel.send(f"📚 L'apprentissage est un voyage passionnant ! Voici ce que je peux faire pour toi :\n\n✅ Tape `!challenge` pour un défi quotidien\n✅ Tape `!suggest` pour une suggestion personnalisée\n✅ Tape `!log <sujet> <durée> <description>` pour enregistrer ta session\n\nQu'est-ce qui t'intéresse d'apprendre aujourd'hui ? 🤔")
        return
    
    # Streak
    if any(word in content_lower for word in ['streak', 'série', 'consécutif']):
        user = get_user(message.author.id)
        if user:
            await message.channel.send(f"🔥 Ton streak actuel : **{user[2]} jour(s)** !\n🏆 Ton record : **{user[3]} jour(s)** !\n\nContinue comme ça ! Tape `!stats` pour plus de détails 📊")
        else:
            await message.channel.send(f"Tu n'es pas encore inscrit ! Tape `!start` pour commencer ton aventure d'apprentissage ! 🚀")
        return
    
    # Au revoir
    if any(word in content_lower for word in ['au revoir', 'bye', 'salut', 'à plus', 'a plus', 'ciao']):
        await message.channel.send(f"👋 À bientôt {message.author.mention} ! N'oublie pas de revenir pour maintenir ton streak ! 🔥")
        return
    
    # Réponse générale
    responses = [
        f"🤔 Intéressant ! Tu veux en savoir plus ? Tape `!help` pour voir ce que je peux faire !",
        f"💡 Je suis là pour t'aider dans ton apprentissage ! Tape `!challenge` pour un défi du jour !",
        f"📚 Prêt à apprendre quelque chose de nouveau ? Tape `!suggest` pour une suggestion !",
        f"😊 Je suis ton assistant d'apprentissage ! Tape `!start` si tu n'es pas encore inscrit, ou `!help` pour voir les commandes !"
    ]
    await message.channel.send(random.choice(responses))
    
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
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    new_total = user[4] + points
    new_level = calculate_level(new_total)
    
    c.execute('''UPDATE users SET total_points = ?, level = ? WHERE user_id = ?''',
              (new_total, new_level, ctx.author.id))
    
    # Log la session
    now = datetime.now().isoformat()
    c.execute('''INSERT INTO learning_logs (user_id, subject, description, duration, log_date, points_earned)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (ctx.author.id, subject, description, duration, now, points))
    
    conn.commit()
    conn.close()
    
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    # Compte les logs
    c.execute('SELECT COUNT(*), SUM(duration), COUNT(DISTINCT subject) FROM learning_logs WHERE user_id = ?', 
              (target.id,))
    log_stats = c.fetchone()
    total_logs = log_stats[0] or 0
    total_minutes = log_stats[1] or 0
    unique_subjects = log_stats[2] or 0
    
    # Top 3 sujets
    c.execute('''SELECT subject, COUNT(*) as count FROM learning_logs 
                 WHERE user_id = ? GROUP BY subject ORDER BY count DESC LIMIT 3''', (target.id,))
    top_subjects = c.fetchall()
    
    # Badges
    c.execute('SELECT COUNT(*) FROM badges WHERE user_id = ?', (target.id,))
    badge_count = c.fetchone()[0]
    
    conn.close()
    
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    c.execute('SELECT badge_name, badge_description, earned_date FROM badges WHERE user_id = ?', 
              (ctx.author.id,))
    earned_badges = c.fetchall()
    conn.close()
    
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
    """Affiche le défi du jour"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    today = datetime.now().date().isoformat()
    c.execute('SELECT challenge_text, category FROM daily_challenges WHERE date = ?', (today,))
    challenge = c.fetchone()
    conn.close()
    
    if not challenge:
        # Génère un nouveau défi si aucun n'existe
        category = random.choice(list(CHALLENGE_CATEGORIES.keys()))
        challenge_text = random.choice(CHALLENGE_CATEGORIES[category])
        
        conn = sqlite3.connect('learning_streak.db')
        c = conn.cursor()
        c.execute('INSERT INTO daily_challenges (challenge_text, category, date) VALUES (?, ?, ?)',
                  (challenge_text, category, today))
        conn.commit()
        conn.close()
    else:
        challenge_text, category = challenge
    
    embed = discord.Embed(
        title="🎯 Défi du Jour",
        description=challenge_text,
        color=discord.Color.purple()
    )
    embed.add_field(name="Catégorie", value=f"📖 {category.capitalize()}", inline=False)
    embed.add_field(name="Comment participer?", value="Explore ce sujet et logue ta session avec `!log`", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Affiche le classement des utilisateurs"""
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    c.execute('''SELECT username, current_streak, longest_streak, total_points, level 
                 FROM users ORDER BY total_points DESC LIMIT 10''')
    top_users = c.fetchall()
    conn.close()
    
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    c.execute('UPDATE users SET interests = ? WHERE user_id = ?', (interest_json, ctx.author.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Centres d'intérêt mis à jour!",
        description="Tes centres d'intérêt: " + ", ".join(interest_list),
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='suggest')
async def suggest_topic(ctx):
    """Suggère un sujet d'apprentissage basé sur les intérêts"""
    user = get_user(ctx.author.id)
    
    if not user:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!start`")
        return
    
    interests = json.loads(user[8]) if user[8] else []
    
    if not interests:
        await ctx.send("❌ Définis d'abord tes intérêts avec `!interests <sujets>`")
        return
    
    # Sélectionne une catégorie basée sur les intérêts ou aléatoirement
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    c.execute('''SELECT subject, description, duration, log_date, points_earned 
                 FROM learning_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT ?''',
              (ctx.author.id, min(limit, 10)))
    logs = c.fetchall()
    conn.close()
    
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    today = datetime.now().date().isoformat()
    c.execute('SELECT user_id, username, current_streak FROM users WHERE last_log_date != ? OR last_log_date IS NULL',
              (today,))
    inactive_users = c.fetchall()
    conn.close()
    
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
    
    conn = sqlite3.connect('learning_streak.db')
    c = conn.cursor()
    
    # Vérifie si un défi existe déjà aujourd'hui
    c.execute('SELECT id FROM daily_challenges WHERE date = ?', (today,))
    if not c.fetchone():
        c.execute('INSERT INTO daily_challenges (challenge_text, category, date) VALUES (?, ?, ?)',
                  (challenge_text, category, today))
        conn.commit()
    
    conn.close()

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
