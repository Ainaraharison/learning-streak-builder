"""
Module de gestion de la base de données
Supporte SQLite (dev) et PostgreSQL (production)
"""

import os
import sqlite3
from typing import Optional, Any, List, Tuple
from contextlib import contextmanager

# Détecte si PostgreSQL est disponible
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Détermine le type de base de données à utiliser
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRES = DATABASE_URL and POSTGRES_AVAILABLE

class DatabaseConnection:
    """Gestionnaire de connexion unifié pour SQLite et PostgreSQL"""
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Contexte manager pour obtenir une connexion à la base de données"""
        if USE_POSTGRES:
            # PostgreSQL
            conn = psycopg2.connect(DATABASE_URL)
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            # SQLite
            conn = sqlite3.connect('learning_streak.db')
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    @staticmethod
    def get_placeholder():
        """Retourne le placeholder approprié pour les requêtes paramétrées"""
        return '%s' if USE_POSTGRES else '?'

def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    placeholder = DatabaseConnection.get_placeholder()
    
    with DatabaseConnection.get_connection() as conn:
        c = conn.cursor()
        
        if USE_POSTGRES:
            # PostgreSQL - Table des utilisateurs
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_log_date TEXT,
                created_at TEXT,
                interests TEXT
            )''')
            
            # PostgreSQL - Table des logs d'apprentissage
            c.execute('''CREATE TABLE IF NOT EXISTS learning_logs (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                subject TEXT,
                description TEXT,
                duration INTEGER,
                log_date TEXT,
                points_earned INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')
            
            # PostgreSQL - Table des badges
            c.execute('''CREATE TABLE IF NOT EXISTS badges (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                badge_name TEXT,
                badge_description TEXT,
                earned_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')
            
            # PostgreSQL - Table des défis du jour
            c.execute('''CREATE TABLE IF NOT EXISTS daily_challenges (
                id SERIAL PRIMARY KEY,
                challenge_text TEXT,
                category TEXT,
                date TEXT
            )''')
        else:
            # SQLite - Table des utilisateurs
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_log_date TEXT,
                created_at TEXT,
                interests TEXT
            )''')
            
            # SQLite - Table des logs d'apprentissage
            c.execute('''CREATE TABLE IF NOT EXISTS learning_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                description TEXT,
                duration INTEGER,
                log_date TEXT,
                points_earned INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')
            
            # SQLite - Table des badges
            c.execute('''CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                badge_name TEXT,
                badge_description TEXT,
                earned_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )''')
            
            # SQLite - Table des défis du jour
            c.execute('''CREATE TABLE IF NOT EXISTS daily_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_text TEXT,
                category TEXT,
                date TEXT
            )''')
        
        conn.commit()
    
    print(f"✅ Base de données initialisée ({'PostgreSQL' if USE_POSTGRES else 'SQLite'})")

def execute_query(query: str, params: Tuple = (), fetch_one: bool = False, 
                  fetch_all: bool = False) -> Optional[Any]:
    """
    Exécute une requête SQL avec les paramètres appropriés
    
    Args:
        query: Requête SQL (utiliser {ph} comme placeholder)
        params: Paramètres de la requête
        fetch_one: Si True, retourne une seule ligne
        fetch_all: Si True, retourne toutes les lignes
    
    Returns:
        Résultat de la requête ou None
    """
    # Remplace les placeholders
    ph = DatabaseConnection.get_placeholder()
    query = query.replace('{ph}', ph)
    
    with DatabaseConnection.get_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        
        if fetch_one:
            result = c.fetchone()
            # Convertit Row en tuple pour compatibilité
            if result and hasattr(result, 'keys'):
                return tuple(result)
            return result
        elif fetch_all:
            results = c.fetchall()
            # Convertit Rows en tuples pour compatibilité
            if results and hasattr(results[0], 'keys'):
                return [tuple(row) for row in results]
            return results
        
        return None

def execute_insert(query: str, params: Tuple = ()) -> Optional[int]:
    """
    Exécute une requête INSERT et retourne l'ID inséré
    
    Args:
        query: Requête SQL INSERT
        params: Paramètres de la requête
    
    Returns:
        ID de la ligne insérée ou None
    """
    ph = DatabaseConnection.get_placeholder()
    query = query.replace('{ph}', ph)
    
    with DatabaseConnection.get_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        
        if USE_POSTGRES:
            # PostgreSQL retourne l'ID avec RETURNING
            if 'RETURNING' in query.upper():
                return c.fetchone()[0]
            return c.lastrowid if hasattr(c, 'lastrowid') else None
        else:
            # SQLite
            return c.lastrowid

# Fonctions utilitaires pour les opérations courantes

def get_user(user_id: int) -> Optional[Tuple]:
    """Récupère les infos d'un utilisateur"""
    return execute_query(
        'SELECT * FROM users WHERE user_id = {ph}',
        (user_id,),
        fetch_one=True
    )

def create_user(user_id: int, username: str, created_at: str):
    """Crée un nouvel utilisateur"""
    execute_query(
        '''INSERT INTO users (user_id, username, created_at, interests) 
           VALUES ({ph}, {ph}, {ph}, {ph})''',
        (user_id, username, created_at, '[]')
    )

def update_user_streak(user_id: int, current_streak: int, longest_streak: int, last_log_date: str):
    """Met à jour le streak d'un utilisateur"""
    execute_query(
        '''UPDATE users SET current_streak = {ph}, longest_streak = {ph}, last_log_date = {ph}
           WHERE user_id = {ph}''',
        (current_streak, longest_streak, last_log_date, user_id)
    )

def update_user_points(user_id: int, total_points: int, level: int):
    """Met à jour les points et le niveau d'un utilisateur"""
    execute_query(
        '''UPDATE users SET total_points = {ph}, level = {ph} WHERE user_id = {ph}''',
        (total_points, level, user_id)
    )

def insert_learning_log(user_id: int, subject: str, description: str, 
                        duration: int, log_date: str, points_earned: int):
    """Insère un log d'apprentissage"""
    execute_query(
        '''INSERT INTO learning_logs (user_id, subject, description, duration, log_date, points_earned)
           VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})''',
        (user_id, subject, description, duration, log_date, points_earned)
    )

def insert_badge(user_id: int, badge_name: str, badge_description: str, earned_date: str):
    """Insère un nouveau badge"""
    execute_query(
        '''INSERT INTO badges (user_id, badge_name, badge_description, earned_date)
           VALUES ({ph}, {ph}, {ph}, {ph})''',
        (user_id, badge_name, badge_description, earned_date)
    )

def get_user_badges(user_id: int) -> List[str]:
    """Récupère la liste des badges d'un utilisateur"""
    results = execute_query(
        'SELECT badge_name FROM badges WHERE user_id = {ph}',
        (user_id,),
        fetch_all=True
    )
    return [row[0] for row in results] if results else []

def count_user_logs(user_id: int) -> int:
    """Compte le nombre total de logs d'un utilisateur"""
    result = execute_query(
        'SELECT COUNT(*) FROM learning_logs WHERE user_id = {ph}',
        (user_id,),
        fetch_one=True
    )
    return result[0] if result else 0

def count_unique_subjects(user_id: int) -> int:
    """Compte le nombre de sujets uniques étudiés par un utilisateur"""
    result = execute_query(
        'SELECT COUNT(DISTINCT subject) FROM learning_logs WHERE user_id = {ph}',
        (user_id,),
        fetch_one=True
    )
    return result[0] if result else 0

def get_daily_challenge(date: str) -> Optional[Tuple]:
    """Récupère le défi du jour"""
    return execute_query(
        'SELECT challenge_text, category FROM daily_challenges WHERE date = {ph}',
        (date,),
        fetch_one=True
    )

def insert_daily_challenge(challenge_text: str, category: str, date: str):
    """Insère un nouveau défi du jour"""
    execute_query(
        'INSERT INTO daily_challenges (challenge_text, category, date) VALUES ({ph}, {ph}, {ph})',
        (challenge_text, category, date)
    )

def update_user_interests(user_id: int, interests_json: str):
    """Met à jour les centres d'intérêt d'un utilisateur"""
    execute_query(
        'UPDATE users SET interests = {ph} WHERE user_id = {ph}',
        (interests_json, user_id)
    )
