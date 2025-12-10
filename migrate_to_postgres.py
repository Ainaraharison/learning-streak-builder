#!/usr/bin/env python3
"""
Script de migration des données SQLite vers PostgreSQL
Permet de transférer l'historique existant vers la nouvelle base de données
"""

import sqlite3
import os
import sys
from datetime import datetime

# Importe le module de base de données
try:
    from database import DatabaseConnection, USE_POSTGRES, init_db
except ImportError:
    print("❌ Impossible d'importer le module database.py")
    print("Assurez-vous que ce script est dans le même dossier que database.py")
    sys.exit(1)

def migrate_data(sqlite_db_path='learning_streak.db'):
    """
    Migre les données de SQLite vers PostgreSQL
    
    Args:
        sqlite_db_path: Chemin vers la base de données SQLite source
    """
    
    if not USE_POSTGRES:
        print("❌ Migration impossible : PostgreSQL n'est pas configuré")
        print("Assurez-vous que DATABASE_URL est défini dans vos variables d'environnement")
        return False
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Base de données SQLite introuvable : {sqlite_db_path}")
        return False
    
    print(f"🔄 Début de la migration depuis {sqlite_db_path} vers PostgreSQL...")
    print(f"📊 DATABASE_URL: {os.getenv('DATABASE_URL', 'Non défini')[:50]}...")
    
    try:
        # Connexion à SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
        
        # Initialise les tables PostgreSQL
        print("\n1️⃣ Initialisation des tables PostgreSQL...")
        init_db()
        
        # Migration des utilisateurs
        print("\n2️⃣ Migration des utilisateurs...")
        sqlite_cur.execute('SELECT * FROM users')
        users = sqlite_cur.fetchall()
        
        with DatabaseConnection.get_connection() as pg_conn:
            pg_cur = pg_conn.cursor()
            
            migrated_users = 0
            for user in users:
                try:
                    pg_cur.execute('''
                        INSERT INTO users (user_id, username, current_streak, longest_streak, 
                                          total_points, level, last_log_date, created_at, interests)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            username = EXCLUDED.username,
                            current_streak = EXCLUDED.current_streak,
                            longest_streak = EXCLUDED.longest_streak,
                            total_points = EXCLUDED.total_points,
                            level = EXCLUDED.level,
                            last_log_date = EXCLUDED.last_log_date,
                            interests = EXCLUDED.interests
                    ''', tuple(user))
                    migrated_users += 1
                except Exception as e:
                    print(f"⚠️  Erreur lors de la migration de l'utilisateur {user['user_id']}: {e}")
            
            pg_conn.commit()
            print(f"   ✅ {migrated_users}/{len(users)} utilisateurs migrés")
        
        # Migration des logs d'apprentissage
        print("\n3️⃣ Migration des logs d'apprentissage...")
        sqlite_cur.execute('SELECT * FROM learning_logs')
        logs = sqlite_cur.fetchall()
        
        with DatabaseConnection.get_connection() as pg_conn:
            pg_cur = pg_conn.cursor()
            
            migrated_logs = 0
            for log in logs:
                try:
                    pg_cur.execute('''
                        INSERT INTO learning_logs (user_id, subject, description, duration, 
                                                  log_date, points_earned)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (log['user_id'], log['subject'], log['description'], 
                          log['duration'], log['log_date'], log['points_earned']))
                    migrated_logs += 1
                except Exception as e:
                    print(f"⚠️  Erreur lors de la migration du log {log['id']}: {e}")
            
            pg_conn.commit()
            print(f"   ✅ {migrated_logs}/{len(logs)} logs d'apprentissage migrés")
        
        # Migration des badges
        print("\n4️⃣ Migration des badges...")
        sqlite_cur.execute('SELECT * FROM badges')
        badges = sqlite_cur.fetchall()
        
        with DatabaseConnection.get_connection() as pg_conn:
            pg_cur = pg_conn.cursor()
            
            migrated_badges = 0
            for badge in badges:
                try:
                    pg_cur.execute('''
                        INSERT INTO badges (user_id, badge_name, badge_description, earned_date)
                        VALUES (%s, %s, %s, %s)
                    ''', (badge['user_id'], badge['badge_name'], 
                          badge['badge_description'], badge['earned_date']))
                    migrated_badges += 1
                except Exception as e:
                    print(f"⚠️  Erreur lors de la migration du badge {badge['id']}: {e}")
            
            pg_conn.commit()
            print(f"   ✅ {migrated_badges}/{len(badges)} badges migrés")
        
        # Migration des défis quotidiens
        print("\n5️⃣ Migration des défis quotidiens...")
        sqlite_cur.execute('SELECT * FROM daily_challenges')
        challenges = sqlite_cur.fetchall()
        
        with DatabaseConnection.get_connection() as pg_conn:
            pg_cur = pg_conn.cursor()
            
            migrated_challenges = 0
            for challenge in challenges:
                try:
                    pg_cur.execute('''
                        INSERT INTO daily_challenges (challenge_text, category, date)
                        VALUES (%s, %s, %s)
                    ''', (challenge['challenge_text'], challenge['category'], challenge['date']))
                    migrated_challenges += 1
                except Exception as e:
                    print(f"⚠️  Erreur lors de la migration du défi {challenge['id']}: {e}")
            
            pg_conn.commit()
            print(f"   ✅ {migrated_challenges}/{len(challenges)} défis quotidiens migrés")
        
        sqlite_conn.close()
        
        print("\n" + "="*60)
        print("✅ Migration terminée avec succès!")
        print("="*60)
        print(f"\n📊 Résumé:")
        print(f"   - Utilisateurs: {migrated_users}")
        print(f"   - Logs d'apprentissage: {migrated_logs}")
        print(f"   - Badges: {migrated_badges}")
        print(f"   - Défis quotidiens: {migrated_challenges}")
        print(f"\n💡 Vous pouvez maintenant déployer le bot avec PostgreSQL!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur durant la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def backup_sqlite(sqlite_db_path='learning_streak.db'):
    """Crée une sauvegarde de la base SQLite"""
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Base de données introuvable : {sqlite_db_path}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{sqlite_db_path}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(sqlite_db_path, backup_path)
        print(f"✅ Sauvegarde créée : {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        return None

def main():
    """Point d'entrée principal"""
    print("="*60)
    print("🔄 Script de Migration SQLite → PostgreSQL")
    print("   Learning Streak Builder")
    print("="*60)
    
    if not USE_POSTGRES:
        print("\n❌ PostgreSQL n'est pas configuré!")
        print("\nPour configurer PostgreSQL:")
        print("1. Créez une base de données PostgreSQL (ex: sur Railway.app)")
        print("2. Définissez la variable d'environnement DATABASE_URL")
        print("   Exemple: DATABASE_URL=postgresql://user:password@host:port/dbname")
        print("3. Relancez ce script")
        sys.exit(1)
    
    sqlite_path = input("\n📁 Chemin vers la base SQLite [learning_streak.db]: ").strip()
    if not sqlite_path:
        sqlite_path = 'learning_streak.db'
    
    if not os.path.exists(sqlite_path):
        print(f"❌ Fichier introuvable : {sqlite_path}")
        sys.exit(1)
    
    print(f"\n⚠️  ATTENTION: Cette opération va transférer toutes les données")
    print(f"   de {sqlite_path} vers PostgreSQL")
    
    response = input("\n❓ Créer une sauvegarde avant de continuer ? [O/n]: ").strip().lower()
    if response != 'n':
        backup_sqlite(sqlite_path)
    
    response = input("\n❓ Continuer la migration ? [O/n]: ").strip().lower()
    if response == 'n':
        print("❌ Migration annulée")
        sys.exit(0)
    
    success = migrate_data(sqlite_path)
    
    if success:
        print("\n🎉 Migration réussie!")
        sys.exit(0)
    else:
        print("\n❌ Échec de la migration")
        sys.exit(1)

if __name__ == '__main__':
    main()
