"""
Database Management Module for Apla Shetkari
Handles SQLite database initialization, schema creation, connection lifecycle,
and parameterized queries for users, chat histories, and crop recommendations.
"""

import sqlite3
import os
from contextlib import contextmanager
from config import Config

def get_db_path():
    """Returns the database file path from configuration."""
    return Config.DATABASE_PATH

@contextmanager
def get_db_connection():
    """
    Context manager providing a SQLite database connection with row factory
    enabled for dictionary-style attribute access and automatic commit/rollback.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """
    Initializes database tables if they do not exist.
    Creates users, chat_history, and crop_recommendations tables.
    """
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(get_db_path()), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                mobile TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Chat History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # 3. Crop Recommendations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crop_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                soil_type TEXT NOT NULL,
                location TEXT NOT NULL,
                season TEXT NOT NULL,
                recommended_crops TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # Indexes for query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history (user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crop_user ON crop_recommendations (user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_mobile ON users (mobile);")

# ----------------- User Authentication Queries -----------------

def create_user(full_name, mobile, email, password_hash, state, district):
    """
    Inserts a newly registered user into the database.
    Returns the newly created user_id.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (full_name, mobile, email, password_hash, state, district)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (full_name.strip(), mobile.strip(), email.strip().lower(), password_hash, state.strip(), district.strip()))
        return cursor.lastrowid

def get_user_by_email_or_mobile(identifier):
    """
    Fetches user record matching email or mobile number.
    Returns sqlite3.Row object or None.
    """
    clean_id = identifier.strip().lower()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE LOWER(email) = ? OR mobile = ?
            LIMIT 1
        """, (clean_id, identifier.strip()))
        return cursor.fetchone()

def get_user_by_id(user_id):
    """Fetches user record by primary key id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
        return cursor.fetchone()

def update_user_profile(user_id, full_name, state, district):
    """Updates basic profile info for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET full_name = ?, state = ?, district = ?
            WHERE id = ?
        """, (full_name.strip(), state.strip(), district.strip(), user_id))
        return cursor.rowcount > 0

# ----------------- Chat History Queries -----------------

def save_chat_message(user_id, user_message, ai_response):
    """
    Saves a conversation turn into chat_history.
    user_id can be None for guest interactions, or integer for authenticated users.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (user_id, user_message, ai_response)
            VALUES (?, ?, ?)
        """, (user_id, user_message.strip(), ai_response.strip()))
        return cursor.lastrowid

def get_chat_history(user_id, limit=50):
    """
    Retrieves recent chat history for a specific user, ordered chronologically.
    """
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, user_message, ai_response, timestamp
            FROM chat_history
            WHERE user_id = ?
            ORDER BY id ASC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()

def clear_chat_history(user_id):
    """Deletes all chat messages for a specific user."""
    if not user_id:
        return 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        return cursor.rowcount

# ----------------- Crop Recommendation Queries -----------------

def save_crop_recommendation(user_id, soil_type, location, season, recommended_crops_json):
    """
    Stores an AI-generated crop recommendation session.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crop_recommendations (user_id, soil_type, location, season, recommended_crops)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, soil_type, location, season, recommended_crops_json))
        return cursor.lastrowid

def get_crop_recommendations(user_id, limit=20):
    """
    Retrieves saved crop recommendations for a user.
    """
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, soil_type, location, season, recommended_crops, created_at
            FROM crop_recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()

def get_user_dashboard_stats(user_id):
    """
    Computes dashboard summary statistics for a user.
    Returns dict with count of chat questions and crop recommendations.
    """
    if not user_id:
        return {'total_chats': 0, 'total_recommendations': 0}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM chat_history WHERE user_id = ?", (user_id,))
        total_chats = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) AS total FROM crop_recommendations WHERE user_id = ?", (user_id,))
        total_recs = cursor.fetchone()['total']
        
        return {
            'total_chats': total_chats,
            'total_recommendations': total_recs
        }
