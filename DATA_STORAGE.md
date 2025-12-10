# 💾 Stockage Permanent des Données

## 🎯 Vue d'ensemble

Le **Learning Streak Builder** supporte maintenant deux types de bases de données :

- **SQLite** (développement local) - Fichier `learning_streak.db`
- **PostgreSQL** (production) - Stockage permanent sur Railway

## ✨ Fonctionnalités

### Détection Automatique

Le bot détecte automatiquement le type de base de données :

```python
# Avec DATABASE_URL → PostgreSQL
# Sans DATABASE_URL → SQLite
```

### Migration Transparente

Un script de migration permet de transférer facilement vos données de SQLite vers PostgreSQL :

```powershell
python migrate_to_postgres.py
```

### Compatibilité Totale

Toutes les fonctionnalités fonctionnent de manière identique sur les deux bases :
- ✅ Gestion des utilisateurs
- ✅ Logs d'apprentissage
- ✅ Système de badges
- ✅ Défis quotidiens
- ✅ Statistiques et classements

## 🚀 Configuration Rapide

### Développement Local (SQLite)

```powershell
# Clonez le projet
git clone https://github.com/votre-username/learning-streak-builder.git
cd learning-streak-builder

# Installez les dépendances
pip install -r requirements.txt

# Configurez vos tokens dans .env
cp .env.example .env
# Éditez .env avec vos tokens

# Lancez le bot
python bot.py
```

Le bot créera automatiquement `learning_streak.db` 🎉

### Production (PostgreSQL sur Railway)

1. **Créez un projet sur Railway.app**
2. **Ajoutez PostgreSQL** : New → Database → PostgreSQL
3. **Configurez les variables** :
   - `DISCORD_BOT_TOKEN`
   - `GROQ_API_KEY`
   - `DATABASE_URL` (créé automatiquement par Railway)
4. **Déployez** : Railway détecte et déploie automatiquement

Le bot utilisera PostgreSQL automatiquement ! 🚀

## 📊 Architecture

### Module Database (`database.py`)

Gère de manière unifiée SQLite et PostgreSQL :

```python
from database import (
    init_db,           # Initialise la base
    get_user,          # Récupère un utilisateur
    create_user,       # Crée un utilisateur
    insert_learning_log, # Ajoute un log
    # ... et plus
)
```

### Abstraction des Requêtes

```python
# Le placeholder est géré automatiquement
execute_query(
    'SELECT * FROM users WHERE user_id = {ph}',
    (user_id,),
    fetch_one=True
)
```

- SQLite : `{ph}` → `?`
- PostgreSQL : `{ph}` → `%s`

## 🔄 Migration des Données

### Quand Migrer ?

Migrez de SQLite vers PostgreSQL si :
- Vous déployez en production
- Vous voulez un stockage permanent
- Vous avez déjà des utilisateurs sur SQLite

### Comment Migrer ?

```powershell
# 1. Configurez DATABASE_URL
$env:DATABASE_URL="postgresql://user:password@host:port/dbname"

# 2. Lancez la migration
python migrate_to_postgres.py
```

Le script :
- ✅ Crée une sauvegarde de SQLite
- ✅ Transfère toutes les données
- ✅ Vérifie l'intégrité
- ✅ Affiche un rapport détaillé

### Exemple de Sortie

```
🔄 Début de la migration depuis learning_streak.db vers PostgreSQL...

1️⃣ Initialisation des tables PostgreSQL...
✅ Base de données initialisée (PostgreSQL)

2️⃣ Migration des utilisateurs...
   ✅ 42/42 utilisateurs migrés

3️⃣ Migration des logs d'apprentissage...
   ✅ 1337/1337 logs d'apprentissage migrés

4️⃣ Migration des badges...
   ✅ 89/89 badges migrés

5️⃣ Migration des défis quotidiens...
   ✅ 15/15 défis quotidiens migrés

============================================================
✅ Migration terminée avec succès!
============================================================
```

## 🛠️ Développement

### Structure du Projet

```
learning-streak-builder/
├── bot.py                    # Bot Discord principal
├── database.py               # Module de gestion BDD
├── migrate_to_postgres.py    # Script de migration
├── requirements.txt          # Dépendances Python
├── DEPLOYMENT.md             # Guide de déploiement
├── MIGRATION.md              # Guide de migration détaillé
└── DATA_STORAGE.md           # Ce fichier
```

### Ajouter une Nouvelle Table

1. **Modifiez `database.py`** :

```python
def init_db():
    # ... code existant ...
    
    if USE_POSTGRES:
        c.execute('''CREATE TABLE IF NOT EXISTS ma_table (
            id SERIAL PRIMARY KEY,
            data TEXT
        )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS ma_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        )''')
```

2. **Ajoutez des fonctions d'accès** :

```python
def insert_data(data: str):
    execute_query(
        'INSERT INTO ma_table (data) VALUES ({ph})',
        (data,)
    )
```

3. **Mettez à jour la migration** :

```python
# Dans migrate_to_postgres.py
sqlite_cur.execute('SELECT * FROM ma_table')
rows = sqlite_cur.fetchall()

for row in rows:
    pg_cur.execute('INSERT INTO ma_table (data) VALUES (%s)', (row['data'],))
```

## 📦 Dépendances

### Production (PostgreSQL)

```txt
discord.py>=2.3.0
python-dotenv>=1.0.0
groq>=0.4.0
psycopg2-binary>=2.9.9
```

### Développement (SQLite seulement)

```txt
discord.py>=2.3.0
python-dotenv>=1.0.0
groq>=0.4.0
```

SQLite est inclus dans Python, pas besoin d'installation !

## 🔐 Variables d'Environnement

### Obligatoires

```env
DISCORD_BOT_TOKEN=your_token_here
GROQ_API_KEY=your_groq_key_here
```

### Optionnelles

```env
# Active PostgreSQL (sinon SQLite)
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## 🐛 Dépannage

### Le bot utilise SQLite au lieu de PostgreSQL

- Vérifiez que `DATABASE_URL` est défini
- Vérifiez que `psycopg2-binary` est installé
- Consultez les logs au démarrage

### Erreur "Module psycopg2 not found"

```powershell
pip install psycopg2-binary
```

### Les données ne persistent pas sur Railway

- Vérifiez que PostgreSQL est ajouté au projet
- Vérifiez que `DATABASE_URL` existe dans les variables
- Redéployez après avoir ajouté PostgreSQL

### Connexion PostgreSQL refusée

- Attendez quelques minutes après création
- Vérifiez le format de `DATABASE_URL`
- Testez la connexion avec `psql`

## 📈 Performance

### SQLite
- ✅ Parfait pour développement
- ✅ Pas de dépendances externes
- ⚠️ Un seul processus à la fois
- ⚠️ Données temporaires sur Railway

### PostgreSQL
- ✅ Production-ready
- ✅ Support multi-instances
- ✅ Sauvegardes automatiques
- ✅ Meilleure performance à grande échelle

## 🔒 Sécurité

### SQLite
- Fichier local `learning_streak.db`
- Pas de credentials nécessaires
- Protégez l'accès au fichier

### PostgreSQL
- Connexion chiffrée (SSL)
- Credentials dans `DATABASE_URL`
- Ne commitez JAMAIS `DATABASE_URL` !

## 📚 Documentation Complète

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Déployer sur Railway
- **[MIGRATION.md](MIGRATION.md)** - Guide de migration détaillé
- **[README.md](README.md)** - Documentation générale du bot

## 🎉 Conclusion

Le système de stockage permanent permet au bot de :

✅ Conserver tous les historiques d'utilisateurs
✅ Survivre aux redéploiements
✅ Évoluer avec votre communauté
✅ Passer de dev à prod sans réécriture

**Votre bot est maintenant prêt pour la production ! 🚀**

---

*Développé avec ❤️ pour la communauté des apprenants*
