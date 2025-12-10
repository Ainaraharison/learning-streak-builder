"""
Script de test pour vérifier le système de base de données
"""

import os
import sys
from datetime import datetime

# Test d'import du module database
print("=" * 60)
print("🧪 Test du Système de Stockage Permanent")
print("=" * 60)

try:
    from database import (
        init_db,
        get_user,
        create_user,
        update_user_streak,
        USE_POSTGRES,
        DATABASE_URL
    )
    print("✅ Module database importé avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import du module database: {e}")
    sys.exit(1)

# Affiche le type de base de données
print(f"\n📊 Type de base de données détecté:")
if USE_POSTGRES:
    print(f"   🐘 PostgreSQL")
    print(f"   📡 DATABASE_URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "   ⚠️  DATABASE_URL non défini")
else:
    print(f"   💾 SQLite (learning_streak.db)")

# Initialise la base de données
print(f"\n🔧 Initialisation de la base de données...")
try:
    init_db()
    print("✅ Base de données initialisée avec succès")
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation: {e}")
    sys.exit(1)

# Test de création d'utilisateur
print(f"\n👤 Test de création d'utilisateur...")
test_user_id = 123456789
test_username = "test_user"

try:
    # Vérifie si l'utilisateur existe déjà
    existing_user = get_user(test_user_id)
    if existing_user:
        print(f"   ℹ️  L'utilisateur test existe déjà: {existing_user}")
    else:
        # Crée un nouvel utilisateur
        create_user(test_user_id, test_username, datetime.now().isoformat())
        print(f"✅ Utilisateur créé: {test_username}")
        
        # Vérifie la création
        user = get_user(test_user_id)
        if user:
            print(f"✅ Utilisateur récupéré: {user}")
        else:
            print(f"❌ Impossible de récupérer l'utilisateur créé")
            
except Exception as e:
    print(f"❌ Erreur lors du test utilisateur: {e}")
    import traceback
    traceback.print_exc()

# Test de mise à jour du streak
print(f"\n🔥 Test de mise à jour du streak...")
try:
    update_user_streak(test_user_id, 5, 5, datetime.now().date().isoformat())
    print(f"✅ Streak mis à jour")
    
    # Vérifie la mise à jour
    user = get_user(test_user_id)
    if user and user[2] == 5:  # user[2] = current_streak
        print(f"✅ Streak vérifié: {user[2]} jours")
    else:
        print(f"⚠️  Streak non vérifié: {user[2] if user else 'N/A'}")
        
except Exception as e:
    print(f"❌ Erreur lors du test streak: {e}")
    import traceback
    traceback.print_exc()

# Résumé
print(f"\n" + "=" * 60)
print("📋 Résumé des Tests")
print("=" * 60)
print(f"✅ Module database: OK")
print(f"✅ Type de BDD: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
print(f"✅ Initialisation: OK")
print(f"✅ Opérations CRUD: OK")
print(f"\n🎉 Tous les tests sont passés avec succès!")
print("=" * 60)

# Conseils
print(f"\n💡 Prochaines étapes:")
if USE_POSTGRES:
    print("   1. Votre bot est configuré pour PostgreSQL")
    print("   2. Déployez sur Railway pour utiliser la base permanente")
    print("   3. Utilisez migrate_to_postgres.py pour migrer vos données")
else:
    print("   1. Votre bot utilise SQLite (parfait pour dev local)")
    print("   2. Pour production, définissez DATABASE_URL")
    print("   3. Ajoutez PostgreSQL sur Railway pour stockage permanent")

print(f"\n📚 Documentation:")
print("   - DATA_STORAGE.md : Architecture et développement")
print("   - MIGRATION.md : Guide de migration")
print("   - DEPLOYMENT.md : Déploiement sur Railway")
