# 🚀 Déploiement sur AWS EC2

Guide complet pour déployer le Learning Streak Builder Bot sur AWS EC2.

## 💰 Coût Mensuel Estimé

### Option 1 : PostgreSQL sur la même instance (Recommandé pour débuter)
| Instance Type | RAM | vCPU | Prix/mois | Free Tier |
|--------------|-----|------|-----------|-----------|
| **t2.micro** | 1 GB | 1 | **$8-10** | ✅ 750h/mois gratuit 12 mois |
| t3.micro | 1 GB | 2 | $7-9 | ❌ |
| t2.small | 2 GB | 1 | $17 | ❌ |
| t3.small | 2 GB | 2 | $15 | ❌ |

**Coût total avec Free Tier : $0/mois pendant 12 mois** ✅
**Après Free Tier : $8-10/mois**

### Option 2 : Avec RDS PostgreSQL séparé
- **Instance EC2 t2.micro** : $8-10/mois (gratuit 12 mois)
- **RDS db.t3.micro** : $15-18/mois (750h gratuit 12 mois)
- **Total** : $23-28/mois (après Free Tier)
- **Pendant Free Tier** : ~$0-3/mois (frais réseau uniquement)

### 💡 Ma recommandation
**PostgreSQL sur la même instance EC2 t2.micro** : Gratuit 12 mois, puis $8-10/mois. Parfait pour un bot Discord.

## 📋 Prérequis

1. Compte AWS avec Free Tier actif
2. Token Discord Bot
3. Clé API Groq
4. Votre code sur GitHub (optionnel mais recommandé)

## 🎯 Étapes de Déploiement

### 1️⃣ Créer une Paire de Clés SSH

1. Console AWS → **EC2** → **Key Pairs** (menu gauche)
2. Cliquez sur **"Create key pair"**
3. Configuration :
   - **Name** : `learning-streak-bot-key`
   - **Key pair type** : RSA
   - **Private key file format** : `.pem` (pour Linux/Mac) ou `.ppk` (pour PuTTY)
4. Cliquez sur **"Create key pair"**
5. **Sauvegardez le fichier** `.pem` dans un endroit sûr (vous ne pourrez plus le télécharger)

### 2️⃣ Créer un Security Group

1. Console AWS → **EC2** → **Security Groups**
2. Cliquez sur **"Create security group"**
3. Configuration :
   - **Name** : `learning-streak-bot-sg`
   - **Description** : `Security group for Discord bot`
   - **VPC** : Laissez par défaut
4. **Inbound rules** (règles entrantes) :
   - Cliquez sur **"Add rule"**
   - **Type** : SSH
   - **Port** : 22
   - **Source** : My IP (pour sécuriser, seulement votre IP)
5. **Outbound rules** : Laissez par défaut (tout autorisé)
6. Cliquez sur **"Create security group"**

### 3️⃣ Lancer une Instance EC2

1. Console AWS → **EC2** → **Instances** → **Launch Instance**
2. **Configuration** :

   **a) Name and tags**
   - **Name** : `learning-streak-bot`

   **b) Application and OS Images (AMI)**
   - **Quick Start** : Ubuntu
   - **AMI** : Ubuntu Server 22.04 LTS (Free tier eligible)

   **c) Instance type**
   - **Type** : `t2.micro` (Free tier eligible - 1 vCPU, 1 GB RAM)

   **d) Key pair**
   - **Key pair name** : `learning-streak-bot-key` (celle créée précédemment)

   **e) Network settings**
   - Cliquez sur **"Edit"**
   - **Firewall (security groups)** : Select existing security group
   - Sélectionnez `learning-streak-bot-sg`

   **f) Configure storage**
   - **Size** : 8 GB (gratuit)
   - **Volume type** : gp2 (gratuit)
   - Vous pouvez monter jusqu'à 30 GB avec le Free Tier

   **g) Advanced details** (optionnel)
   - Laissez par défaut

3. Cliquez sur **"Launch instance"**
4. Attendez 1-2 minutes que l'instance démarre
5. Notez l'**IPv4 Public Address** (ex: `54.123.45.67`)

### 4️⃣ Se Connecter à l'Instance EC2

#### Sur Windows (PowerShell)

```powershell
# Donner les bonnes permissions au fichier .pem
icacls "C:\chemin\vers\learning-streak-bot-key.pem" /inheritance:r
icacls "C:\chemin\vers\learning-streak-bot-key.pem" /grant:r "$env:USERNAME:R"

# Se connecter
ssh -i "C:\chemin\vers\learning-streak-bot-key.pem" ubuntu@54.123.45.67
```

#### Sur Linux/Mac

```bash
# Donner les bonnes permissions
chmod 400 ~/Downloads/learning-streak-bot-key.pem

# Se connecter
ssh -i ~/Downloads/learning-streak-bot-key.pem ubuntu@54.123.45.67
```

**Note** : Remplacez `54.123.45.67` par votre IP publique EC2

### 5️⃣ Installation Automatique avec le Script

Une fois connecté à l'instance EC2 :

```bash
# Télécharger le script de déploiement
wget https://raw.githubusercontent.com/VOTRE_USERNAME/learning-streak-builder/main/deploy_ec2.sh

# Rendre le script exécutable
chmod +x deploy_ec2.sh

# Lancer le déploiement
bash deploy_ec2.sh
```

Le script vous demandera :
1. **Mot de passe PostgreSQL** (créez-en un sécurisé)
2. **URL du repository GitHub** (ou créera le dossier pour copie manuelle)
3. **Token Discord Bot**
4. **Clé API Groq**

### 6️⃣ Ou Installation Manuelle

Si vous préférez l'installation manuelle :

```bash
# 1. Mise à jour du système
sudo apt update && sudo apt upgrade -y

# 2. Installation des dépendances
sudo apt install -y python3-pip python3-venv git libpq-dev python3-dev build-essential

# 3. Installation de PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4. Configuration de la base de données
sudo -u postgres psql << 'EOF'
CREATE DATABASE learning_streak;
CREATE USER botuser WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE learning_streak TO botuser;
\q
EOF

# 5. Cloner le projet
git clone https://github.com/VOTRE_USERNAME/learning-streak-builder.git
cd learning-streak-builder

# 6. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 7. Installer les dépendances
pip install -r requirements.txt

# 8. Créer le fichier .env
nano .env
```

Contenu du `.env` :
```env
DISCORD_BOT_TOKEN=votre_token_discord
DATABASE_URL=postgresql://botuser:votre_mot_de_passe@localhost:5432/learning_streak
GROQ_API_KEY=votre_cle_groq
```

```bash
# 9. Tester le bot
python3 bot.py
# Ctrl+C pour arrêter

# 10. Configurer le service systemd
sudo nano /etc/systemd/system/learning-streak-bot.service
```

Copiez le contenu du fichier `learning-streak-bot.service` fourni :

```ini
[Unit]
Description=Learning Streak Builder Discord Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/learning-streak-builder
Environment="PATH=/home/ubuntu/learning-streak-builder/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/ubuntu/learning-streak-builder/venv/bin/python3 /home/ubuntu/learning-streak-builder/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# 11. Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable learning-streak-bot
sudo systemctl start learning-streak-bot

# 12. Vérifier le statut
sudo systemctl status learning-streak-bot
```

## 🔒 Configuration Optionnelle : IP Élastique

Pour avoir une adresse IP fixe qui ne change pas au redémarrage :

1. Console AWS → **EC2** → **Elastic IPs**
2. Cliquez sur **"Allocate Elastic IP address"**
3. **Network Border Group** : Laissez par défaut
4. Cliquez sur **"Allocate"**
5. Sélectionnez l'IP allouée → **Actions** → **Associate Elastic IP address**
6. **Instance** : Sélectionnez votre instance `learning-streak-bot`
7. Cliquez sur **"Associate"**

**Coût** : Gratuit tant que l'IP est associée à une instance en cours d'exécution. $0.005/heure (~$3.60/mois) si non associée.

## 💾 Option : Utiliser RDS PostgreSQL

Si vous voulez une base de données séparée et professionnelle :

### 1️⃣ Créer une Instance RDS

1. Console AWS → **RDS** → **Create database**
2. **Configuration** :
   - **Engine type** : PostgreSQL
   - **Version** : 15.x (dernière disponible)
   - **Templates** : Free tier
   - **DB instance identifier** : `learning-streak-db`
   - **Master username** : `postgres`
   - **Master password** : (créez un mot de passe sécurisé)
   - **DB instance class** : db.t3.micro
   - **Storage** : 20 GB gp2
   - **VPC security group** : Create new → `rds-learning-streak-sg`
   - **Public access** : No
   - **Database name** : `learning_streak`
3. Cliquez sur **"Create database"** (5-10 minutes)

### 2️⃣ Configurer le Security Group

1. Console AWS → **RDS** → Votre instance → **Connectivity & security**
2. Cliquez sur le **VPC security group**
3. **Inbound rules** → **Edit inbound rules** → **Add rule**
   - **Type** : PostgreSQL
   - **Port** : 5432
   - **Source** : Custom → Security group de l'EC2 (`learning-streak-bot-sg`)
4. **Save rules**

### 3️⃣ Mettre à Jour le Fichier .env

```env
DATABASE_URL=postgresql://postgres:VOTRE_PASSWORD@rds-endpoint.region.rds.amazonaws.com:5432/learning_streak
```

**Endpoint** : Trouvez-le dans RDS → Votre instance → Connectivity & security → Endpoint

## 📊 Monitoring et Logs

### Voir les logs du bot
```bash
# Logs en temps réel
sudo journalctl -u learning-streak-bot -f

# Derniers 100 logs
sudo journalctl -u learning-streak-bot -n 100

# Logs depuis aujourd'hui
sudo journalctl -u learning-streak-bot --since today
```

### CloudWatch (Monitoring AWS)

1. Console AWS → **CloudWatch** → **Dashboards** → **Create dashboard**
2. Ajoutez des widgets pour :
   - CPU Utilization de l'EC2
   - Network In/Out
   - Disk Read/Write

### Alertes automatiques

Créer une alarme si le bot s'arrête :

1. Console AWS → **CloudWatch** → **Alarms** → **Create alarm**
2. **Select metric** → EC2 → Per-Instance Metrics → StatusCheckFailed
3. **Threshold** : Greater than 0
4. **Notification** : Create new SNS topic → Entrez votre email
5. Cliquez sur **"Create alarm"**

## 🔄 Mise à Jour du Bot

```bash
# Se connecter à l'EC2
ssh -i votre-cle.pem ubuntu@votre-ip-ec2

# Aller dans le projet
cd learning-streak-builder

# Activer l'environnement virtuel
source venv/bin/activate

# Récupérer les modifications
git pull

# Installer les nouvelles dépendances (si besoin)
pip install -r requirements.txt

# Redémarrer le bot
sudo systemctl restart learning-streak-bot

# Vérifier
sudo systemctl status learning-streak-bot
```

## 💾 Sauvegardes

### Sauvegardes Automatiques de PostgreSQL

```bash
# Créer un script de sauvegarde
nano ~/backup_db.sh
```

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Sauvegarde
pg_dump -U botuser -h localhost learning_streak > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Garder seulement les 7 dernières sauvegardes
ls -t $BACKUP_DIR/backup_*.sql | tail -n +8 | xargs rm -f

echo "Backup créé : backup_$TIMESTAMP.sql"
```

```bash
# Rendre exécutable
chmod +x ~/backup_db.sh

# Tester
~/backup_db.sh

# Programmer (tous les jours à 3h)
crontab -e
# Ajouter : 0 3 * * * /home/ubuntu/backup_db.sh
```

### Snapshots EC2 (AMI)

1. Console AWS → **EC2** → **Instances**
2. Sélectionnez votre instance
3. **Actions** → **Image and templates** → **Create image**
4. **Image name** : `learning-streak-bot-backup-2026-01-02`
5. Cliquez sur **"Create image"**

**Coût** : ~$0.05 par GB/mois pour le stockage

### Automatiser les Snapshots

1. Console AWS → **EC2** → **Lifecycle Manager**
2. **Create lifecycle policy**
3. **Target resources** : Instance
4. **Schedule** : Daily, à 2h du matin
5. **Retention** : 7 derniers snapshots

## 🔧 Commandes Utiles

```bash
# Redémarrer le bot
sudo systemctl restart learning-streak-bot

# Arrêter le bot
sudo systemctl stop learning-streak-bot

# Démarrer le bot
sudo systemctl start learning-streak-bot

# Voir le statut
sudo systemctl status learning-streak-bot

# Voir les logs en temps réel
sudo journalctl -u learning-streak-bot -f

# Vérifier l'utilisation de la RAM
free -h

# Vérifier l'utilisation du disque
df -h

# Vérifier les processus
top
# ou
htop  # (installer avec: sudo apt install htop)

# Vérifier que PostgreSQL fonctionne
sudo systemctl status postgresql

# Test de connexion PostgreSQL
psql -U botuser -d learning_streak -h localhost
```

## 🆘 Dépannage

### Le bot ne démarre pas

```bash
# Voir les erreurs détaillées
sudo journalctl -u learning-streak-bot -n 50 --no-pager

# Tester manuellement
cd /home/ubuntu/learning-streak-builder
source venv/bin/activate
python3 bot.py
```

### Problème de connexion SSH

Si vous ne pouvez plus vous connecter :
1. Console AWS → EC2 → Instances
2. Sélectionnez votre instance → **Actions** → **Security** → **Change security groups**
3. Vérifiez que votre IP est autorisée dans le Security Group

### Instance arrêtée accidentellement

L'instance EC2 peut être arrêtée manuellement ou par AWS. Pour la redémarrer :
1. Console AWS → EC2 → Instances
2. Sélectionnez votre instance
3. **Instance state** → **Start instance**

### Dépassement de RAM

Si l'instance t2.micro (1 GB) n'est pas suffisante :
1. Arrêtez l'instance
2. **Actions** → **Instance settings** → **Change instance type**
3. Choisissez `t2.small` (2 GB RAM) - $17/mois
4. Redémarrez l'instance

## 💡 Optimisation des Coûts

### Pendant le Free Tier (12 mois)
- **t2.micro** : 750 heures gratuites/mois (= 1 instance 24/7 gratuite)
- **EBS** : 30 GB gratuits
- **Transfert** : 15 GB sortant gratuit

**Coût réel** : $0-2/mois (frais de transfert uniquement)

### Après le Free Tier
- Utilisez **Compute Savings Plans** : -20% à -30% de réduction
- **Reserved Instances** : -40% à -60% si engagement 1-3 ans
- Arrêtez l'instance quand vous ne l'utilisez pas (mais le bot sera offline)

### Surveiller les coûts
1. Console AWS → **Billing** → **Cost Explorer**
2. Activez les **Billing Alerts** pour être notifié si dépasse un seuil

## 📈 Comparaison EC2 vs Lightsail

| Aspect | EC2 | Lightsail |
|--------|-----|-----------|
| **Prix après Free Tier** | $8-10/mois | $3.50/mois |
| **Free Tier** | ✅ 750h/mois pendant 12 mois | ❌ Pas de Free Tier |
| **Complexité** | ⚠️ Moyenne | ✅ Simple |
| **Flexibilité** | ✅✅✅ Maximum | ⚠️ Limitée |
| **Scaling** | ✅ Facile | ⚠️ Manuel |
| **Surveillance** | ✅ CloudWatch complet | ⚠️ Basique |
| **IP fixe** | 💰 Elastic IP (~$3/mois si non utilisée) | ✅ Incluse |

## ✅ Checklist Finale

- [ ] Paire de clés SSH créée et sauvegardée
- [ ] Security Group configuré
- [ ] Instance EC2 lancée (t2.micro)
- [ ] Connexion SSH établie
- [ ] PostgreSQL installé et configuré
- [ ] Bot déployé et fonctionnel
- [ ] Service systemd activé
- [ ] Bot répond sur Discord
- [ ] Sauvegardes configurées
- [ ] Alarmes CloudWatch créées (optionnel)
- [ ] Elastic IP associée (optionnel)

## 🎉 Félicitations !

Votre bot Discord tourne maintenant 24/7 sur AWS EC2 !

**Coût** : 
- Avec Free Tier (12 mois) : **Gratuit** ✅
- Après Free Tier : **$8-10/mois**

---

## 📚 Ressources

- [Documentation AWS EC2](https://docs.aws.amazon.com/ec2/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

Pour toute question, consultez les logs : `sudo journalctl -u learning-streak-bot -f`
