# 🚀 Déploiement sur AWS Lightsail

Guide complet pour déployer le Learning Streak Builder Bot sur AWS Lightsail.

## 💰 Coût

- **$3.50/mois** (plan le plus économique)
- 512 MB RAM, 1 vCPU, 20 GB SSD
- 1 TB de transfert de données inclus

## 📋 Prérequis

1. Un compte AWS
2. Votre token Discord Bot
3. Votre clé API Groq
4. Votre code sur GitHub (recommandé)

## 🎯 Étapes de Déploiement

### 1️⃣ Créer l'Instance Lightsail

1. Connectez-vous à la [Console AWS Lightsail](https://lightsail.aws.amazon.com/)
2. Cliquez sur **"Create instance"**
3. Choisissez :
   - **Platform** : Linux/Unix
   - **Blueprint** : OS Only → **Ubuntu 22.04 LTS**
   - **Instance plan** : $3.50/month (512 MB RAM)
   - **Instance name** : `learning-streak-bot`
4. Cliquez sur **"Create instance"**
5. Attendez 1-2 minutes que l'instance démarre

### 2️⃣ Configurer la Base de Données PostgreSQL

#### Option A : PostgreSQL sur la même instance (Recommandé pour débuter)

Cette option est gratuite et incluse dans les $3.50/mois.

```bash
# Installer PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Créer la base de données
sudo -u postgres psql
```

Dans psql :
```sql
CREATE DATABASE learning_streak;
CREATE USER botuser WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE learning_streak TO botuser;
\q
```

Votre `DATABASE_URL` sera :
```
postgresql://botuser:votre_mot_de_passe_securise@localhost:5432/learning_streak
```

#### Option B : Amazon RDS PostgreSQL (Pour production)

**Coût supplémentaire** : ~$15/mois (db.t3.micro)

1. Console AWS → RDS → Create database
2. PostgreSQL, version 15+
3. Templates : Free tier (si disponible)
4. Notez l'endpoint, username, password

### 3️⃣ Connecter à l'Instance et Installer le Bot

1. **Se connecter via SSH** (dans la console Lightsail, cliquez sur l'icône terminal)

2. **Installer les dépendances**
   ```bash
   # Mise à jour du système
   sudo apt update
   sudo apt upgrade -y
   
   # Installer Python 3 et pip
   sudo apt install python3-pip python3-venv git -y
   
   # Installer les dépendances système pour psycopg2
   sudo apt install libpq-dev python3-dev build-essential -y
   ```

3. **Cloner votre projet**
   ```bash
   # Via GitHub (recommandé)
   git clone https://github.com/VOTRE_USERNAME/learning-streak-builder.git
   cd learning-streak-builder
   
   # OU télécharger directement
   # wget https://github.com/VOTRE_USERNAME/learning-streak-builder/archive/refs/heads/main.zip
   # unzip main.zip
   # cd learning-streak-builder-main
   ```

4. **Créer un environnement virtuel Python**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

6. **Créer le fichier de configuration**
   ```bash
   nano .env
   ```
   
   Contenu du `.env` :
   ```env
   DISCORD_BOT_TOKEN=votre_token_discord_ici
   DATABASE_URL=postgresql://botuser:votre_mot_de_passe@localhost:5432/learning_streak
   GROQ_API_KEY=votre_cle_groq_ici
   ```
   
   💾 Sauvegarder : `Ctrl+O`, `Enter`, `Ctrl+X`

7. **Initialiser la base de données**
   ```bash
   python3 bot.py
   ```
   
   Si tout fonctionne, vous verrez :
   ```
   ✓ Base de données initialisée avec succès
   [VotreBot] est connecté et prêt!
   ```
   
   Arrêtez avec `Ctrl+C`

### 4️⃣ Configurer le Bot comme Service Système

Pour que le bot démarre automatiquement et tourne en arrière-plan :

```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/learning-streak-bot.service
```

Copiez le contenu du fichier `learning-streak-bot.service` fourni dans le projet, ou utilisez :

```ini
[Unit]
Description=Learning Streak Builder Discord Bot
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/learning-streak-builder
Environment="PATH=/home/ubuntu/learning-streak-builder/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/ubuntu/learning-streak-builder/venv/bin/python3 /home/ubuntu/learning-streak-builder/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Activer et démarrer le service :**
```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable learning-streak-bot

# Démarrer le service
sudo systemctl start learning-streak-bot

# Vérifier le statut
sudo systemctl status learning-streak-bot
```

### 5️⃣ Vérifier que Tout Fonctionne

**Voir les logs en temps réel :**
```bash
sudo journalctl -u learning-streak-bot -f
```

**Commandes utiles :**
```bash
# Redémarrer le bot
sudo systemctl restart learning-streak-bot

# Arrêter le bot
sudo systemctl stop learning-streak-bot

# Voir le statut
sudo systemctl status learning-streak-bot

# Voir les derniers logs
sudo journalctl -u learning-streak-bot -n 50
```

**Tester sur Discord :**
```
!start
!challenge
!streak
```

## 🔄 Mettre à Jour le Bot

Quand vous faites des changements dans votre code :

```bash
# Se connecter à l'instance Lightsail
cd learning-streak-builder

# Activer l'environnement virtuel
source venv/bin/activate

# Récupérer les dernières modifications
git pull

# Installer les nouvelles dépendances (si nécessaire)
pip install -r requirements.txt

# Redémarrer le bot
sudo systemctl restart learning-streak-bot

# Vérifier les logs
sudo journalctl -u learning-streak-bot -f
```

## 🔒 Sécurité

### Configurer le Firewall

Lightsail inclut un firewall intégré. Par défaut, seul SSH (port 22) est ouvert, ce qui est parfait pour un bot Discord.

**Dans la console Lightsail :**
1. Allez dans votre instance
2. Onglet **"Networking"**
3. Les règles par défaut sont suffisantes (SSH port 22 uniquement)

### Sécuriser SSH

```bash
# Créer un nouvel utilisateur (optionnel)
sudo adduser botadmin
sudo usermod -aG sudo botadmin

# Désactiver la connexion root SSH
sudo nano /etc/ssh/sshd_config
# Changer : PermitRootLogin no
sudo systemctl restart sshd
```

## 💾 Sauvegardes

### Sauvegarder la Base de Données

```bash
# Créer un script de sauvegarde
nano ~/backup_db.sh
```

Contenu :
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Sauvegarde PostgreSQL
pg_dump -U botuser learning_streak > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Garder seulement les 7 dernières sauvegardes
ls -t $BACKUP_DIR/backup_*.sql | tail -n +8 | xargs rm -f

echo "Backup créé : backup_$TIMESTAMP.sql"
```

```bash
# Rendre le script exécutable
chmod +x ~/backup_db.sh

# Tester
~/backup_db.sh

# Programmer des sauvegardes automatiques (tous les jours à 3h du matin)
crontab -e
# Ajouter : 0 3 * * * /home/ubuntu/backup_db.sh
```

### Snapshot Lightsail

Dans la console Lightsail :
1. Cliquez sur votre instance
2. Onglet **"Snapshots"**
3. **"Create snapshot"**
4. Nommez-le (ex: `bot-backup-2026-01-02`)

**Snapshots automatiques** : Activez-les dans les paramètres (1 snapshot/jour, 7 jours de rétention)

## 📊 Monitoring

### Voir les Métriques dans Lightsail

1. Console Lightsail → Votre instance
2. Onglet **"Metrics"**
3. Vous verrez : CPU, Network In/Out, Status

### Configurer des Alertes

Vous pouvez configurer des alertes email si le bot s'arrête :

```bash
# Installer un script de monitoring simple
nano ~/check_bot.sh
```

```bash
#!/bin/bash
if ! systemctl is-active --quiet learning-streak-bot; then
    echo "Bot is down! Restarting..." | mail -s "Bot Alert" votre@email.com
    sudo systemctl restart learning-streak-bot
fi
```

```bash
chmod +x ~/check_bot.sh
# Vérifier toutes les 5 minutes
crontab -e
# Ajouter : */5 * * * * /home/ubuntu/check_bot.sh
```

## 🆘 Dépannage

### Le bot ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u learning-streak-bot -n 100

# Vérifier que PostgreSQL fonctionne
sudo systemctl status postgresql

# Tester manuellement
cd learning-streak-builder
source venv/bin/activate
python3 bot.py
```

### Problèmes de connexion PostgreSQL

```bash
# Vérifier que PostgreSQL écoute
sudo -u postgres psql -c "SELECT version();"

# Tester la connexion avec vos credentials
psql -U botuser -d learning_streak -h localhost
```

### Manque de Mémoire (RAM)

Si vous recevez des erreurs mémoire, passez au plan supérieur ($5/mois, 1 GB RAM) :
1. Console Lightsail → Votre instance
2. Manage → **"Change your instance plan"**

## 📈 Mise à l'Échelle

Si votre bot grandit :

1. **$5/mois** (1 GB RAM) - jusqu'à ~10 serveurs Discord
2. **$10/mois** (2 GB RAM) - jusqu'à ~50 serveurs
3. Migrer vers **EC2 + RDS** pour plus de flexibilité

## ✅ Checklist Finale

- [ ] Instance Lightsail créée et démarrée
- [ ] PostgreSQL installé et configuré
- [ ] Bot cloné et dépendances installées
- [ ] Fichier `.env` créé avec les bonnes credentials
- [ ] Service systemd configuré et actif
- [ ] Bot répond aux commandes Discord
- [ ] Snapshots automatiques activés
- [ ] Sauvegardes PostgreSQL configurées

## 🎉 Félicitations !

Votre bot Discord tourne maintenant 24/7 sur AWS Lightsail !

**Coût total** : $3.50/mois
**Disponibilité** : 99.9%+
**Maintenance** : Minimale

---

## 📚 Ressources Utiles

- [Documentation AWS Lightsail](https://lightsail.aws.amazon.com/ls/docs)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

Pour toute question, consultez les logs avec `sudo journalctl -u learning-streak-bot -f`
