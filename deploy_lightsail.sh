#!/bin/bash
# Script de déploiement automatisé pour AWS Lightsail
# Usage: bash deploy_lightsail.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage du déploiement du Learning Streak Bot..."

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "\n${GREEN}▶ $1${NC}\n"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Vérifier qu'on est sur Ubuntu
if [ ! -f /etc/lsb-release ]; then
    error "Ce script est conçu pour Ubuntu. Système non supporté."
fi

# 1. Mise à jour du système
step "1/8 Mise à jour du système"
sudo apt update && sudo apt upgrade -y
success "Système mis à jour"

# 2. Installation de Python et dépendances
step "2/8 Installation de Python et des outils"
sudo apt install -y python3-pip python3-venv git libpq-dev python3-dev build-essential
success "Python et outils installés"

# 3. Installation de PostgreSQL
step "3/8 Installation de PostgreSQL"
if ! command -v psql &> /dev/null; then
    sudo apt install -y postgresql postgresql-contrib
    success "PostgreSQL installé"
else
    success "PostgreSQL déjà installé"
fi

# Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4. Configuration de la base de données
step "4/8 Configuration de la base de données"
echo -e "${YELLOW}Veuillez entrer un mot de passe sécurisé pour l'utilisateur PostgreSQL :${NC}"
read -s DB_PASSWORD

sudo -u postgres psql << EOF
-- Créer la base de données si elle n'existe pas
SELECT 'CREATE DATABASE learning_streak' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'learning_streak')\gexec

-- Créer l'utilisateur si il n'existe pas
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'botuser') THEN
        CREATE USER botuser WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Donner les privilèges
GRANT ALL PRIVILEGES ON DATABASE learning_streak TO botuser;
EOF

success "Base de données configurée"

# 5. Cloner ou mettre à jour le projet
step "5/8 Configuration du projet"
PROJECT_DIR="$HOME/learning-streak-builder"

if [ -d "$PROJECT_DIR" ]; then
    echo "Le projet existe déjà. Mise à jour..."
    cd "$PROJECT_DIR"
    git pull || echo "Pas un repository git, on continue..."
else
    echo -e "${YELLOW}URL du repository GitHub (ou laissez vide pour créer manuellement) :${NC}"
    read REPO_URL
    if [ -n "$REPO_URL" ]; then
        git clone "$REPO_URL" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    else
        mkdir -p "$PROJECT_DIR"
        cd "$PROJECT_DIR"
        echo "Veuillez copier vos fichiers dans $PROJECT_DIR puis relancer ce script."
        exit 0
    fi
fi

success "Projet configuré dans $PROJECT_DIR"

# 6. Créer l'environnement virtuel et installer les dépendances
step "6/8 Installation des dépendances Python"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
success "Dépendances Python installées"

# 7. Configuration du fichier .env
step "7/8 Configuration des variables d'environnement"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Token Discord Bot :${NC}"
    read DISCORD_TOKEN
    
    echo -e "${YELLOW}Clé API Groq :${NC}"
    read GROQ_KEY
    
    cat > .env << EOF
DISCORD_BOT_TOKEN=$DISCORD_TOKEN
DATABASE_URL=postgresql://botuser:$DB_PASSWORD@localhost:5432/learning_streak
GROQ_API_KEY=$GROQ_KEY
EOF
    success "Fichier .env créé"
else
    success "Fichier .env existe déjà"
fi

# 8. Configuration du service systemd
step "8/8 Configuration du service système"
SERVICE_FILE="/etc/systemd/system/learning-streak-bot.service"

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Learning Streak Builder Discord Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Sécurité
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Recharger systemd et activer le service
sudo systemctl daemon-reload
sudo systemctl enable learning-streak-bot
sudo systemctl start learning-streak-bot

success "Service configuré et démarré"

# Afficher le statut
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
success "🎉 Déploiement terminé avec succès !"
echo ""
echo "📊 Statut du bot :"
sudo systemctl status learning-streak-bot --no-pager

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Commandes utiles :"
echo ""
echo "  • Voir les logs en temps réel :"
echo "    sudo journalctl -u learning-streak-bot -f"
echo ""
echo "  • Redémarrer le bot :"
echo "    sudo systemctl restart learning-streak-bot"
echo ""
echo "  • Arrêter le bot :"
echo "    sudo systemctl stop learning-streak-bot"
echo ""
echo "  • Voir le statut :"
echo "    sudo systemctl status learning-streak-bot"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Votre bot Discord est maintenant opérationnel 24/7 !"
echo ""
