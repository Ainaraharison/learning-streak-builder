# Guide de Démarrage Rapide - Learning Streak Builder

## 🚀 Installation en 5 Minutes

### 1. Créer ton Bot Discord

1. Va sur https://discord.com/developers/applications
2. Clique "New Application" → Donne un nom
3. Va dans "Bot" → "Add Bot"
4. Active les 3 "Privileged Gateway Intents":
   - ✅ Presence Intent
   - ✅ Server Members Intent  
   - ✅ Message Content Intent
5. Copie le TOKEN (bouton "Reset Token" puis "Copy")

### 2. Inviter le Bot

1. Va dans "OAuth2" → "URL Generator"
2. Coche: `bot` + `applications.commands`
3. Permissions: `Send Messages`, `Embed Links`, `Read Message History`
4. Copie l'URL et ouvre-la pour inviter le bot

### 3. Installation Python

```powershell
# Ouvre PowerShell dans le dossier du projet
cd "e:\Professionnal Legend\project_perso\Learning_streak_builder"

# Crée un environnement virtuel
python -m venv venv

# Active-le
.\venv\Scripts\Activate.ps1

# Installe les dépendances
pip install -r requirements.txt

# Crée le fichier de configuration
Copy-Item .env.example .env
```

### 4. Configuration

Ouvre `.env` avec un éditeur de texte et colle ton token:
```
DISCORD_BOT_TOKEN=ton_token_copié_ici
```

### 5. Lancer le Bot

```powershell
python bot.py
```

✅ Tu devrais voir: `[NomDuBot] est connecté et prêt!`

## 🎮 Première Utilisation

Sur Discord, dans ton serveur:

```
!start                                    # S'inscrire
!interests Python, IA, Science           # Définir tes intérêts
!challenge                               # Voir le défi du jour
!log Python 30 J'ai appris les listes   # Logger ta première session
!stats                                   # Voir tes stats
```

## 🎯 Commandes Principales

| Commande | Action |
|----------|--------|
| `!log <sujet> <minutes> <description>` | Logger une session |
| `!stats` | Voir tes statistiques |
| `!badges` | Voir tes badges |
| `!challenge` | Défi du jour |
| `!suggest` | Suggestion personnalisée |
| `!history` | Tes dernières sessions |
| `!leaderboard` | Classement |

## ❓ Problèmes Courants

**Bot hors ligne?**
- Vérifie le token dans `.env`
- Vérifie les "Privileged Gateway Intents"

**Commandes ne fonctionnent pas?**
- Le préfixe est `!` (point d'exclamation)
- Vérifie que le bot a la permission "Send Messages"

**Erreur "Module not found"?**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🎉 C'est Tout!

Commence à apprendre et accumule des streaks! 🔥
