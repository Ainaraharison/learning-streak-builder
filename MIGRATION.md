# 🔄 Migration vers PostgreSQL

Ce document explique comment migrer vos données de SQLite vers PostgreSQL pour un stockage permanent.

## 📋 Pourquoi PostgreSQL ?

- ✅ **Stockage permanent** : Les données survivent aux redéploiements
- ✅ **Sauvegarde automatique** : Railway sauvegarde votre base de données
- ✅ **Scalabilité** : Support de plusieurs instances du bot
- ✅ **Performance** : Meilleur pour de nombreux utilisateurs

## 🎯 Configuration Rapide

### Sur Railway.app

1. **Ajoutez PostgreSQL à votre projet**
   - Cliquez sur **"New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway crée automatiquement `DATABASE_URL`

2. **Redéployez le bot**
   - Le bot détecte automatiquement PostgreSQL
   - Les tables sont créées automatiquement

C'est tout ! 🎉

### Migration des Données Existantes

Si vous avez déjà des utilisateurs et données dans SQLite :

#### Option 1 : Via le Script de Migration (Recommandé)

```powershell
# 1. Configurez DATABASE_URL localement
$env:DATABASE_URL="postgresql://user:password@host:port/dbname"

# 2. Installez psycopg2 si nécessaire
pip install psycopg2-binary

# 3. Lancez le script
python migrate_to_postgres.py
```

Le script vous guidera et :
- Créera une sauvegarde de SQLite
- Transférera toutes les données
- Affichera un résumé de la migration

#### Option 2 : Migration Manuelle

Si vous préférez migrer manuellement :

1. **Exportez vos données SQLite**
   ```python
   import sqlite3
   import json
   
   conn = sqlite3.connect('learning_streak.db')
   cursor = conn.cursor()
   
   # Export users
   cursor.execute('SELECT * FROM users')
   users = cursor.fetchall()
   
   with open('users_backup.json', 'w') as f:
       json.dump([dict(u) for u in users], f)
   ```

2. **Importez dans PostgreSQL**
   - Utilisez le script `migrate_to_postgres.py` qui gère tout automatiquement

## 🔍 Vérification

### Vérifier le Type de Base de Données

Au démarrage du bot, vérifiez les logs :

```
✅ Base de données initialisée (PostgreSQL)
```

### Tester les Commandes

```
!stats
!history
!leaderboard
```

Toutes vos données devraient être présentes !

## 🏗️ Architecture Technique

### Détection Automatique

Le bot détecte automatiquement le type de base de données :

```python
# Avec DATABASE_URL → PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL and POSTGRES_AVAILABLE

# Sans DATABASE_URL → SQLite (développement)
```

### Compatibilité des Requêtes

Le module `database.py` gère automatiquement les différences de syntaxe :

- **Placeholders** : `?` (SQLite) vs `%s` (PostgreSQL)
- **AUTO_INCREMENT** : `AUTOINCREMENT` vs `SERIAL`
- **Types** : `INTEGER` vs `BIGINT` pour les IDs Discord

## 🛠️ Développement Local

### Tester avec SQLite

```powershell
# Ne définissez PAS DATABASE_URL
python bot.py
```

Le bot utilisera automatiquement `learning_streak.db`

### Tester avec PostgreSQL Local

```powershell
# Installez PostgreSQL localement
# Puis créez une base de données
createdb learning_streak_test

# Configurez DATABASE_URL
$env:DATABASE_URL="postgresql://localhost/learning_streak_test"

# Lancez le bot
python bot.py
```

## 🔧 Dépannage

### "Module psycopg2 not found"

```powershell
pip install psycopg2-binary
```

### "Connection refused" sur PostgreSQL

- Vérifiez que `DATABASE_URL` est correct
- Format attendu : `postgresql://user:password@host:port/dbname`
- Sur Railway, cette variable est créée automatiquement

### Les données ne sont pas migrées

1. Vérifiez que le script de migration s'est bien exécuté
2. Consultez les logs pour voir les erreurs
3. Essayez de relancer la migration

### Erreur de connexion sur Railway

- Attendez quelques minutes après la création de PostgreSQL
- Redéployez le bot pour qu'il détecte `DATABASE_URL`

## 📊 Surveillance des Données

### Accéder à PostgreSQL sur Railway

1. Dans Railway, cliquez sur votre base PostgreSQL
2. Onglet **"Data"** pour voir les tables
3. Onglet **"Connect"** pour obtenir les informations de connexion

### Requêtes Utiles

Connectez-vous avec `psql` ou un client PostgreSQL :

```sql
-- Nombre d'utilisateurs
SELECT COUNT(*) FROM users;

-- Statistiques globales
SELECT 
  COUNT(DISTINCT user_id) as total_users,
  SUM(total_points) as total_points,
  MAX(current_streak) as max_streak
FROM users;

-- Logs récents
SELECT user_id, subject, duration, log_date 
FROM learning_logs 
ORDER BY log_date DESC 
LIMIT 10;
```

## 🔐 Sécurité

### Protégez vos Credentials

- ✅ Ne commitez JAMAIS `DATABASE_URL` dans Git
- ✅ Utilisez les variables d'environnement
- ✅ Railway gère automatiquement la sécurité

### Sauvegardes

Railway sauvegarde automatiquement votre base PostgreSQL :
- Sauvegardes quotidiennes
- Rétention de 7 jours (plan gratuit)
- Restauration possible depuis l'interface

## 🚀 Migration en Production

### Checklist avant Migration

- [ ] PostgreSQL créé sur Railway
- [ ] `DATABASE_URL` configuré
- [ ] Script de migration testé localement
- [ ] Sauvegarde SQLite créée
- [ ] Utilisateurs informés de la maintenance

### Plan de Migration

1. **Informez les utilisateurs** (5 minutes de downtime)
2. **Arrêtez le bot** sur Railway
3. **Lancez la migration** depuis votre machine locale
4. **Redéployez le bot** avec PostgreSQL
5. **Vérifiez** avec `!stats` et `!leaderboard`

### Rollback en Cas de Problème

Si quelque chose ne va pas :

1. Supprimez `DATABASE_URL` de Railway
2. Redéployez → le bot reviendra à SQLite
3. Restaurez la sauvegarde SQLite si nécessaire

## 📚 Ressources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Railway PostgreSQL Guide](https://docs.railway.app/databases/postgresql)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

**Besoin d'aide ?** Consultez les logs ou ouvrez une issue sur GitHub !
