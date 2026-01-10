"""
Database module for Spanish Learning App
SQLite database for vocabulary, progress tracking, and session history
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import json

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "hablaconmigo.db"


def get_connection():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Vocabulary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spanish TEXT NOT NULL,
            english TEXT NOT NULL,
            category TEXT,
            example_sentence TEXT,
            audio_path TEXT,
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Spaced repetition table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vocabulary_id INTEGER NOT NULL,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review TIMESTAMP,
            last_review TIMESTAMP,
            FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
        )
    """)

    # Practice phrases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spanish TEXT NOT NULL,
            english TEXT NOT NULL,
            category TEXT,
            difficulty INTEGER DEFAULT 1,
            audio_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Practice sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT NOT NULL,
            duration_seconds INTEGER,
            items_practiced INTEGER,
            average_accuracy REAL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        )
    """)

    # Pronunciation attempts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pronunciation_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_id INTEGER,
            expected_text TEXT NOT NULL,
            spoken_text TEXT,
            accuracy REAL,
            feedback TEXT,
            audio_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phrase_id) REFERENCES phrases(id)
        )
    """)

    # Conversation history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============ Vocabulary Functions ============

def add_vocabulary(spanish: str, english: str, category: str = None,
                   example_sentence: str = None, difficulty: int = 1) -> int:
    """Add a vocabulary word"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vocabulary (spanish, english, category, example_sentence, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (spanish, english, category, example_sentence, difficulty))

    vocab_id = cursor.lastrowid

    # Initialize progress tracking
    cursor.execute("""
        INSERT INTO vocabulary_progress (vocabulary_id, next_review)
        VALUES (?, ?)
    """, (vocab_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    return vocab_id


def get_vocabulary_for_review(limit: int = 10) -> list:
    """Get vocabulary items due for review"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, vp.ease_factor, vp.interval_days, vp.repetitions
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.next_review <= ?
        ORDER BY vp.next_review
        LIMIT ?
    """, (datetime.now().isoformat(), limit))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def update_vocabulary_progress(vocabulary_id: int, quality: int):
    """
    Update vocabulary progress using SM-2 algorithm

    Args:
        vocabulary_id: ID of the vocabulary item
        quality: Quality of recall (0-5)
                0-1: Complete failure
                2: Correct with difficulty
                3: Correct with hesitation
                4: Correct easily
                5: Perfect
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get current progress
    cursor.execute("""
        SELECT * FROM vocabulary_progress WHERE vocabulary_id = ?
    """, (vocabulary_id,))
    progress = dict(cursor.fetchone())

    ease_factor = progress['ease_factor']
    interval = progress['interval_days']
    repetitions = progress['repetitions']

    # SM-2 algorithm
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)

        repetitions += 1

    # Update ease factor
    ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    # Calculate next review date
    next_review = datetime.now() + timedelta(days=interval)

    cursor.execute("""
        UPDATE vocabulary_progress
        SET ease_factor = ?, interval_days = ?, repetitions = ?,
            next_review = ?, last_review = ?
        WHERE vocabulary_id = ?
    """, (ease_factor, interval, repetitions, next_review.isoformat(),
          datetime.now().isoformat(), vocabulary_id))

    conn.commit()
    conn.close()


def get_all_vocabulary(category: str = None) -> list:
    """Get all vocabulary, optionally filtered by category"""
    conn = get_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute("""
            SELECT * FROM vocabulary WHERE category = ? ORDER BY spanish
        """, (category,))
    else:
        cursor.execute("SELECT * FROM vocabulary ORDER BY category, spanish")

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


# ============ Phrase Functions ============

def add_phrase(spanish: str, english: str, category: str = None,
               difficulty: int = 1, notes: str = None) -> int:
    """Add a practice phrase"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO phrases (spanish, english, category, difficulty, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (spanish, english, category, difficulty, notes))

    phrase_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return phrase_id


def get_phrases(category: str = None, difficulty: int = None, limit: int = None) -> list:
    """Get practice phrases with optional filters"""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM phrases WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)

    query += " ORDER BY RANDOM()"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_phrase_by_id(phrase_id: int) -> Optional[dict]:
    """Get a specific phrase by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM phrases WHERE id = ?", (phrase_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============ Practice Session Functions ============

def start_session(session_type: str) -> int:
    """Start a new practice session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO practice_sessions (session_type)
        VALUES (?)
    """, (session_type,))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_session(session_id: int, items_practiced: int, average_accuracy: float):
    """End a practice session"""
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate duration
    cursor.execute("SELECT started_at FROM practice_sessions WHERE id = ?", (session_id,))
    started_at = cursor.fetchone()[0]
    started = datetime.fromisoformat(started_at)
    duration = int((datetime.now() - started).total_seconds())

    cursor.execute("""
        UPDATE practice_sessions
        SET duration_seconds = ?, items_practiced = ?, average_accuracy = ?, ended_at = ?
        WHERE id = ?
    """, (duration, items_practiced, average_accuracy, datetime.now().isoformat(), session_id))

    conn.commit()
    conn.close()


def record_pronunciation_attempt(phrase_id: int, expected_text: str, spoken_text: str,
                                  accuracy: float, feedback: str = None) -> int:
    """Record a pronunciation attempt"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pronunciation_attempts (phrase_id, expected_text, spoken_text, accuracy, feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (phrase_id, expected_text, spoken_text, accuracy, feedback))
    attempt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return attempt_id


# ============ Statistics Functions ============

def get_statistics() -> dict:
    """Get overall learning statistics"""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Total vocabulary
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    stats['total_vocabulary'] = cursor.fetchone()[0]

    # Total phrases
    cursor.execute("SELECT COUNT(*) FROM phrases")
    stats['total_phrases'] = cursor.fetchone()[0]

    # Total practice sessions
    cursor.execute("SELECT COUNT(*) FROM practice_sessions")
    stats['total_sessions'] = cursor.fetchone()[0]

    # Total practice time
    cursor.execute("SELECT SUM(duration_seconds) FROM practice_sessions")
    total_seconds = cursor.fetchone()[0] or 0
    stats['total_practice_minutes'] = round(total_seconds / 60, 1)

    # Average accuracy
    cursor.execute("SELECT AVG(accuracy) FROM pronunciation_attempts")
    avg_accuracy = cursor.fetchone()[0]
    stats['average_accuracy'] = round(avg_accuracy, 1) if avg_accuracy else 0

    # Recent attempts
    cursor.execute("""
        SELECT AVG(accuracy) FROM pronunciation_attempts
        WHERE created_at > datetime('now', '-7 days')
    """)
    recent_accuracy = cursor.fetchone()[0]
    stats['recent_accuracy'] = round(recent_accuracy, 1) if recent_accuracy else 0

    # Vocabulary due for review
    cursor.execute("""
        SELECT COUNT(*) FROM vocabulary_progress WHERE next_review <= ?
    """, (datetime.now().isoformat(),))
    stats['vocabulary_due'] = cursor.fetchone()[0]

    conn.close()
    return stats


# ============ Settings Functions ============

def get_setting(key: str, default: str = None) -> Optional[str]:
    """Get a setting value"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key: str, value: str):
    """Set a setting value"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print(f"Database created at: {DB_PATH}")

    # Test adding some data
    vocab_id = add_vocabulary("hola", "hello", "greetings", "¡Hola! ¿Cómo estás?")
    print(f"Added vocabulary: {vocab_id}")

    phrase_id = add_phrase("Buenos días", "Good morning", "greetings", 1)
    print(f"Added phrase: {phrase_id}")

    stats = get_statistics()
    print(f"Statistics: {stats}")
