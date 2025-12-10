# 🚀 Déploiement du Bot sur Railway.app

Ce guide vous aide à déployer le Learning Streak Builder sur Railway.app pour qu'il fonctionne 24/7 gratuitement.

## 📋 Prérequis

1. Un compte GitHub (pour connecter à Railway)
2. Un compte Railway.app (gratuit)
3. Votre token Discord

## 🎯 Étapes de Déploiement

### 1️⃣ Préparer le Repository GitHub

#### Option A : Créer un nouveau repository

```powershell
# Initialise Git dans le projet
cd "E:\Professionnal Legend\project_perso\Learning_streak_builder"
git init

# Ajoute tous les fichiers (sauf ceux dans .gitignore)
git add .

# Crée le premier commit
git commit -m "Initial commit - Learning Streak Builder Bot"

# Crée un repository sur GitHub puis lie-le
git remote add origin https://github.com/TON_USERNAME/learning-streak-builder.git
git branch -M main
git push -u origin main
```

#### Option B : Repository déjà existant

```powershell
git add .
git commit -m "Add Railway deployment files"
git push
```

### 2️⃣ Déployer sur Railway

1. **Va sur** https://railway.app/
2. **Connecte-toi** avec GitHub
3. Clique sur **"New Project"**
4. Choisis **"Deploy from GitHub repo"**
5. Sélectionne ton repository `learning-streak-builder`
6. Railway détectera automatiquement le projet Python

### 3️⃣ Configurer les Variables d'Environnement

1. Dans le projet Railway, va dans **"Variables"**
2. Clique sur **"New Variable"**
3. Ajoute :
   - **Key** : `DISCORD_BOT_TOKEN`
   - **Value** : `ton_token_discord`
4. Clique sur **"Add"**

### 4️⃣ Vérifier le Déploiement

1. Va dans l'onglet **"Deployments"**
2. Attends que le statut passe à **"Success"** (peut prendre 2-3 minutes)
3. Clique sur **"View Logs"** pour voir :
   ```
   [NomDuBot] est connecté et prêt!
   Connecté à X serveur(s)
   ```

## ✅ Vérification

Sur ton serveur Discord, teste :
```
!start
!challenge
```

Le bot devrait répondre ! 🎉

## 📊 Surveillance

- **Logs en temps réel** : Onglet "Deployments" → "View Logs"
- **Métriques** : Railway affiche l'utilisation CPU/RAM
- **Redémarrage automatique** : Railway redémarre le bot en cas de crash

## 💾 Stockage Permanent des Données avec PostgreSQL

✅ **Le bot supporte maintenant PostgreSQL pour un stockage permanent !**

### Configuration PostgreSQL sur Railway

#### 1️⃣ Ajouter PostgreSQL à votre projet

1. Dans Railway, clique sur **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway créera automatiquement la variable d'environnement `DATABASE_URL`
3. **C'est tout !** Le bot détectera automatiquement PostgreSQL et l'utilisera

#### 2️⃣ Migrer vos données existantes (Optionnel)

Si vous avez déjà des données dans SQLite local :

```powershell
# 1. Assurez-vous que DATABASE_URL est défini
$env:DATABASE_URL="postgresql://user:password@host:port/dbname"

# 2. Lancez le script de migration
python migrate_to_postgres.py
```

Le script va :
- Créer une sauvegarde de votre base SQLite
- Transférer tous les utilisateurs, logs, badges et défis
- Confirmer le succès de la migration

#### 3️⃣ Fonctionnement Automatique

Le bot détecte automatiquement le type de base de données :

- **Avec `DATABASE_URL`** → PostgreSQL (production)
- **Sans `DATABASE_URL`** → SQLite (développement local)

Aucune modification de code nécessaire ! 🎉

### Avantages de PostgreSQL

✅ **Persistance totale** : Les données survivent aux redéploiements
✅ **Sauvegarde automatique** : Railway sauvegarde votre base
✅ **Scalabilité** : Support de plusieurs instances du bot
✅ **Performance** : Meilleur pour de nombreux utilisateurs

### Mode Développement Local

Pour tester localement avec SQLite :

```powershell
# Ne définissez PAS DATABASE_URL
# Le bot utilisera automatiquement learning_streak.db
python bot.py
```

### Vérifier le Type de Base de Données

Les logs au démarrage affichent :
```
✅ Base de données initialisée (PostgreSQL)
```
ou
```
✅ Base de données initialisée (SQLite)
```

## 🔧 Redéployer après Modifications

```powershell
# Modifie ton code
# Puis :
git add .
git commit -m "Description des modifications"
git push

# Railway redéploie automatiquement !
```

## 💰 Plan Gratuit Railway

- **500 heures gratuites/mois** (suffisant pour 1 bot 24/7)
- **1 GB RAM**
- **1 GB stockage**
- Pas de carte bancaire requise au début

## 🐛 Résolution de Problèmes

### Le bot ne démarre pas
- Vérifie les logs dans Railway
- Assure-toi que `DISCORD_BOT_TOKEN` est bien configuré
- Vérifie que les "Privileged Gateway Intents" sont activés sur Discord

### "Out of Memory"
- Le bot utilise très peu de RAM (<100MB normalement)
- Si problème, contacte Railway support

### Le bot se déconnecte
- Railway redémarre automatiquement le bot
- Normal lors des mises à jour de la plateforme

## 🌟 Prochaines Étapes (Optionnel)

### Ajouter un Healthcheck

Pour que Railway vérifie que le bot fonctionne, ajoute à `bot.py` :

```python
# Serveur web simple pour healthcheck
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def healthcheck():
    return 'Bot is running!', 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Dans on_ready(), ajoute :
threading.Thread(target=run_flask, daemon=True).start()
```

Puis ajoute `flask` dans `requirements.txt`.

### Monitoring Avancé

- **UptimeRobot** : Ping le bot toutes les 5 minutes
- **Discord Webhooks** : Notifications en cas de crash

## 📚 Ressources

- [Documentation Railway](https://docs.railway.app/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Railway Discord Server](https://discord.gg/railway)

---

**Félicitations ! Ton bot est maintenant hébergé 24/7 ! 🎉**
