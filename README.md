# 🎓 Learning Streak Builder - Bot Discord

Un bot Discord gamifié pour suivre et encourager ton apprentissage quotidien. Accumule des streaks, gagne des badges, et monte de niveau en apprenant de nouvelles choses chaque jour!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-7289DA.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Fonctionnalités

### 🔥 Système de Streaks
- **Streaks quotidiens**: Maintiens une série de jours consécutifs d'apprentissage
- **Suivi automatique**: Le bot détecte automatiquement si tu as cassé ton streak
- **Meilleur streak**: Enregistre ton record personnel

### 🎯 Gamification
- **Système de points**: Gagne des points basés sur la durée de tes sessions, ton streak, et tes quiz
- **Niveaux**: Monte de niveau en accumulant des points
- **Badges**: Débloquer 11 badges différents en accomplissant des objectifs
  - 🌱 Premier Pas
  - 🔥 Guerrier Hebdomadaire (7 jours)
  - 🏆 Maître du Mois (30 jours)
  - 🎯 Marathon (50 jours)
  - 💯 Centurion (100 sessions)
  - 🗺️ Explorateur (10 sujets différents)
  - 🧠 Polymathe (25 sujets différents)
  - ⚡ Dédié (niveau 5)
  - 🎓 Apprenti Quiz (5 quiz réussis)
  - 🏅 Expert Quiz (20 quiz réussis)
  - 💎 Score Parfait (100% à un quiz)

### 📊 Statistiques & Tracking
- **Statistiques personnelles**: Visualise tes progrès (points, niveau, sessions, temps total)
- **Historique des sessions**: Consulte tes dernières sessions d'apprentissage
- **Sujets explorés**: Suivi des différents domaines étudiés
- **Classement**: Compare-toi avec les autres membres du serveur

### 🎲 Défis & Suggestions
- **Défi du jour**: Un nouveau défi quotidien dans 6 catégories (science, technologie, histoire, art, philosophie, langues)
- **Suggestions personnalisées**: Reçois des suggestions basées sur tes centres d'intérêt
- **Quiz interactifs IA**: Questions générées dynamiquement par IA sur n'importe quel sujet
- **Rappels quotidiens**: Le bot t'envoie un message si tu n'as pas loggué de session

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Un compte Discord
- Un serveur Discord où tu as les permissions d'ajouter un bot

### Étape 1: Créer un Bot Discord

1. Va sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique sur "New Application" et donne-lui un nom
3. Va dans l'onglet "Bot" et clique sur "Add Bot"
4. Active les **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Copie le token du bot (garde-le secret!)

### Étape 2: Inviter le Bot sur ton Serveur

1. Va dans l'onglet "OAuth2" > "URL Generator"
2. Coche les scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Coche les permissions:
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Add Reactions
4. Copie l'URL générée et ouvre-la dans ton navigateur pour inviter le bot

### Étape 3: Configuration du Projet

1. **Clone ou télécharge le projet**
```powershell
cd "e:\Professionnal Legend\project_perso\Learning_streak_builder"
```

2. **Crée un environnement virtuel**
```powershell
python -m venv venv
```

3. **Active l'environnement virtuel**
```powershell
.\venv\Scripts\Activate.ps1
```

4. **Installe les dépendances**
```powershell
pip install -r requirements.txt
```

5. **Configure le token**
```powershell
# Copie le fichier d'exemple
Copy-Item .env.example .env

# Édite le fichier .env et remplace par ton token
# DISCORD_BOT_TOKEN=ton_token_ici
```

### Étape 4: Lancer le Bot

```powershell
python bot.py
```

Tu devrais voir:
```
[Nom du Bot] est connecté et prêt!
Connecté à X serveur(s)
```

## 📖 Commandes Disponibles

### Commandes de Base
| Commande | Description | Exemple |
|----------|-------------|---------|
| `!start` | S'inscrire au Learning Streak Builder | `!start` |
| `!help` | Afficher l'aide | `!help` |

### Logging & Apprentissage
| Commande | Description | Exemple |
|----------|-------------|---------|
| `!log <sujet> <durée> <description>` | Logger une session d'apprentissage | `!log Python 30 Appris les decorateurs` |
| `!history [limite]` | Voir l'historique de tes sessions (max 10) | `!history 5` |

### Statistiques & Progression
| Commande | Description | Exemple |
|----------|-------------|---------|
| `!stats [@utilisateur]` | Voir les stats (toi ou un autre) | `!stats` ou `!stats @User` |
| `!badges` | Voir tous tes badges | `!badges` |
| `!leaderboard` | Voir le classement du serveur | `!leaderboard` |

### Défis & Suggestions
| Commande | Description | Exemple |
|----------|-------------|---------|
| `!challenge` | Voir le défi du jour | `!challenge` |
| `!suggest` | Obtenir une suggestion personnalisée | `!suggest` |
| `!interests <sujets>` | Définir tes centres d'intérêt | `!interests Python, IA, Philosophie` |
| `!quiz [sujet]` | Lancer un quiz IA interactif | `!quiz` ou `!quiz la photosynthèse` |

## 💡 Exemples d'Utilisation

### Première utilisation
```
Toi: !start
Bot: 🎉 Bienvenue au Learning Streak Builder! [...]

Toi: !interests Python, Machine Learning, Science
Bot: ✅ Centres d'intérêt mis à jour!

Toi: !challenge
Bot: 🎯 Défi du Jour
     Découvre ce qu'est le machine learning
     Catégorie: 📖 Technologie
```

### Logger une session
```
Toi: !log MachineLearning 45 Introduction aux réseaux de neurones
Bot: ✅ Session loguée avec succès!
     📚 Sujet: MachineLearning
     ⏱️ Durée: 45 min
     🎯 Points gagnés: +455
     🔥 Streak actuel: 1 jour(s)
     🏆 Nouveaux Badges!
     🌱 Premier Pas - Première session loguée
```

### Voir ses stats
```
Toi: !stats
Bot: 📊 Statistiques de [Ton Nom]
     🔥 Streak actuel: 7 jour(s)
     🏆 Meilleur streak: 7 jour(s)
     📊 Niveau: 2
     💰 Total points: 3150
     📚 Sessions totales: 7
     🏅 Badges: 2/8
     ⏱️ Temps total: 315 min (5h15)
     🗺️ Sujets explorés: 5
```

## 🎮 Système de Points

### Calcul des Points
```
Points gagnés = (Durée en minutes × 10) + (Streak actuel × 5)
```

**Exemple**: Session de 30 minutes avec un streak de 5 jours
```
Points = (30 × 10) + (5 × 5) = 300 + 25 = 325 points
```

### Calcul du Niveau
```
Niveau = √(Total points / 100)
```

| Points | Niveau |
|--------|--------|
| 0-99 | 1 |
| 100-399 | 2 |
| 400-899 | 3 |
| 900-1599 | 4 |
| 1600-2499 | 5 |
| 2500+ | 6+ |

## 🗄️ Base de Données

Le bot supporte **deux types de bases de données** :

### 🏠 SQLite (Développement Local)
- Stockage dans le fichier `learning_streak.db`
- Aucune configuration requise
- Parfait pour tester en local

### 🚀 PostgreSQL (Production)
- Stockage permanent sur Railway.app
- Les données survivent aux redéploiements
- Configuration automatique avec `DATABASE_URL`

**Le bot détecte automatiquement le type de base à utiliser !**

### Tables
- **users**: Informations des utilisateurs (streaks, points, niveau)
- **learning_logs**: Historique de toutes les sessions
- **badges**: Badges débloqués par les utilisateurs
- **daily_challenges**: Défis quotidiens générés

### 🔄 Migration
Pour migrer vos données de SQLite vers PostgreSQL :
```powershell
python migrate_to_postgres.py
```

Voir [DATA_STORAGE.md](DATA_STORAGE.md) et [MIGRATION.md](MIGRATION.md) pour plus de détails.

## 🔧 Personnalisation

### Ajouter des Défis Personnalisés

Édite le dictionnaire `CHALLENGE_CATEGORIES` dans `bot.py`:

```python
CHALLENGE_CATEGORIES = {
    'ta_categorie': [
        "Ton défi 1",
        "Ton défi 2",
        # ...
    ]
}
```

### Créer de Nouveaux Badges

Ajoute des badges dans le dictionnaire `BADGES`:

```python
BADGES = {
    'ton_badge': {
        'name': '🎨 Ton Badge', 
        'description': 'Description du badge'
    }
}
```

Puis ajoute la logique de déverrouillage dans `check_and_award_badges()`.

## 🐛 Résolution de Problèmes

### Le bot ne se connecte pas
- Vérifie que ton token est correct dans le fichier `.env`
- Assure-toi que les "Privileged Gateway Intents" sont activés

### Les rappels ne fonctionnent pas
- Vérifie que l'utilisateur accepte les messages privés
- Le bot doit rester en ligne 24/7 pour les rappels (considère un hébergement cloud)

### Erreur "Missing Permissions"
- Vérifie que le bot a les permissions nécessaires sur le serveur
- Le rôle du bot doit être placé assez haut dans la hiérarchie

## 🚀 Déploiement (Hébergement 24/7)

Pour que le bot fonctionne en permanence avec les rappels quotidiens:

### Option 1: Hébergement Cloud Gratuit
- **Replit**: [replit.com](https://replit.com)
- **Railway**: [railway.app](https://railway.app)
- **Heroku**: [heroku.com](https://heroku.com) (plan gratuit limité)

### Option 2: VPS
- **DigitalOcean**, **AWS EC2**, **Google Cloud**
- Installe Python et lance le bot en arrière-plan avec `screen` ou `tmux`

### Option 3: Ordinateur Local 24/7
```powershell
# Lance en arrière-plan (pas recommandé pour production)
Start-Process python -ArgumentList "bot.py" -WindowStyle Hidden
```

## 📝 Structure du Projet

```
Learning_streak_builder/
│
├── bot.py                    # Code principal du bot
├── database.py               # Module de gestion base de données
├── migrate_to_postgres.py    # Script de migration SQLite → PostgreSQL
├── requirements.txt          # Dépendances Python
├── .env                      # Configuration (tokens) - À créer
├── .env.example              # Exemple de configuration
├── .gitignore                # Fichiers à ignorer par Git
├── README.md                 # Documentation principale
├── DEPLOYMENT.md             # Guide de déploiement sur Railway
├── MIGRATION.md              # Guide de migration PostgreSQL
├── DATA_STORAGE.md           # Documentation stockage données
├── Procfile.bot              # Configuration Railway
├── runtime.txt               # Version Python pour Railway
└── learning_streak.db        # Base SQLite (créée en local)
```

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésite pas à:
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 🎯 Quiz Interactifs par IA

Le bot utilise l'IA (Groq) pour générer des quiz dynamiques sur n'importe quel sujet !

### Fonctionnalités
- **Questions générées par IA**: Chaque quiz est unique et adapté au sujet demandé
- **3 questions par quiz** avec 4 options chacune
- **30 secondes** par question pour répondre
- **Explications détaillées**: L'IA fournit une explication après chaque réponse
- **Système de points bonus**:
  - 50 points par bonne réponse
  - +100 points pour un score parfait (100%)
  - +50 points pour un très bon score (≥66%)

### Utilisation
```
# Quiz basé sur tes centres d'intérêt
Toi: !quiz
Bot: 🤖 Génération d'un quiz sur Python... ⏳
     🎯 Quiz : Python
     Question 1/3: Qu'est-ce qu'un décorateur en Python ?
     1. Une fonction qui modifie une autre fonction
     2. Un commentaire de documentation
     3. Une variable globale
     4. Un type de classe
     
Toi: 1
Bot: ✅ Bonne réponse ! Les décorateurs permettent de modifier le comportement d'une fonction.

# Quiz sur un sujet spécifique
Toi: !quiz la photosynthèse
Bot: 🤖 Génération d'un quiz sur la photosynthèse... ⏳
     [...]
```

## 💡 Idées d'Améliorations Futures

- [ ] Intégration d'APIs externes (Wikipedia, YouTube) pour suggestions enrichies
- [ ] Système de groupes d'étude avec défis collaboratifs
- [ ] Graphiques de progression avec charts interactifs
- [ ] Export des données en PDF/CSV
- [ ] Mode "Focus Time" avec minuteur Pomodoro
- [ ] Intégration avec Notion/Trello pour suivi de projets
- [ ] Système de récompenses réelles (code promo, etc.)
- [ ] Mode compétition avec saisons et trophées
- [x] Quiz interactifs générés par IA

## 📄 Licence

Ce projet est sous licence MIT. Tu es libre de l'utiliser, le modifier et le distribuer.

## 🙏 Remerciements

- [Discord.py](https://github.com/Rapptz/discord.py) pour la librairie Discord
- La communauté Discord pour l'inspiration
- Tous les apprenants qui utilisent cet outil!

## 📧 Contact

Pour toute question ou suggestion, ouvre une issue sur GitHub!

---

**Bon apprentissage! 🎓🔥**
