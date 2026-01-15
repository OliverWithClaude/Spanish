"""
Database module for Spanish Learning App
SQLite database for vocabulary, progress tracking, learning path, and session history
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

    # ============ Learning Path Tables ============

    # Sections (CEFR levels - A1.1, A1.2, A2.1, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cefr_level TEXT NOT NULL,
            description TEXT,
            order_num INTEGER NOT NULL,
            xp_required INTEGER DEFAULT 0,
            word_target INTEGER DEFAULT 250,
            is_unlocked BOOLEAN DEFAULT FALSE
        )
    """)

    # Units (Topics within sections)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            order_num INTEGER NOT NULL,
            xp_reward INTEGER DEFAULT 100,
            is_unlocked BOOLEAN DEFAULT FALSE,
            is_completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (section_id) REFERENCES sections(id)
        )
    """)

    # User Progress (XP, level, streak)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_xp INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            current_section_id INTEGER DEFAULT 1,
            current_unit_id INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_practice_date DATE,
            words_seen INTEGER DEFAULT 0,
            words_learning INTEGER DEFAULT 0,
            words_mastered INTEGER DEFAULT 0,
            total_practice_seconds INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ============ Vocabulary Tables ============

    # Vocabulary table (enhanced)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spanish TEXT NOT NULL,
            english TEXT NOT NULL,
            category TEXT,
            unit_id INTEGER,
            cefr_level TEXT DEFAULT 'A1',
            example_sentence TEXT,
            audio_path TEXT,
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id)
        )
    """)

    # Spaced repetition table (enhanced)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vocabulary_id INTEGER NOT NULL,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            times_incorrect INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            next_review TIMESTAMP,
            last_review TIMESTAMP,
            FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
        )
    """)
    # status: 'new', 'learning', 'learned', 'due', 'struggling'

    # ============ Phrase Tables ============

    # Practice phrases table (enhanced)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spanish TEXT NOT NULL,
            english TEXT NOT NULL,
            category TEXT,
            unit_id INTEGER,
            cefr_level TEXT DEFAULT 'A1',
            difficulty INTEGER DEFAULT 1,
            audio_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (unit_id) REFERENCES units(id)
        )
    """)

    # ============ Session & Activity Tables ============

    # Practice sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT NOT NULL,
            duration_seconds INTEGER,
            items_practiced INTEGER,
            xp_earned INTEGER DEFAULT 0,
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
            xp_earned INTEGER DEFAULT 0,
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

    # XP Activity Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            xp_amount INTEGER NOT NULL,
            description TEXT,
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

    # Initialize user progress if not exists
    cursor.execute("SELECT COUNT(*) FROM user_progress")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_progress DEFAULT VALUES")
        conn.commit()

    # Migration: Add total_practice_seconds column if it doesn't exist
    try:
        cursor.execute("SELECT total_practice_seconds FROM user_progress LIMIT 1")
    except:
        cursor.execute("ALTER TABLE user_progress ADD COLUMN total_practice_seconds INTEGER DEFAULT 0")
        conn.commit()

    conn.close()


# ============ Learning Path Functions ============

def add_section(name: str, cefr_level: str, description: str, order_num: int,
                xp_required: int = 0, word_target: int = 250) -> int:
    """Add a learning section"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sections (name, cefr_level, description, order_num, xp_required, word_target, is_unlocked)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, cefr_level, description, order_num, xp_required, word_target, order_num == 1))
    section_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return section_id


def add_unit(section_id: int, name: str, description: str, order_num: int,
             xp_reward: int = 100) -> int:
    """Add a unit to a section"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO units (section_id, name, description, order_num, xp_reward, is_unlocked)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (section_id, name, description, order_num, xp_reward, order_num == 1))
    unit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return unit_id


def get_sections() -> list:
    """Get all sections with progress info"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*,
            (SELECT COUNT(*) FROM units WHERE section_id = s.id) as total_units,
            (SELECT COUNT(*) FROM units WHERE section_id = s.id AND is_completed = 1) as completed_units,
            (SELECT COUNT(*) FROM vocabulary WHERE cefr_level = s.cefr_level) as total_words
        FROM sections s
        ORDER BY s.order_num
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_units(section_id: int = None) -> list:
    """Get units, optionally filtered by section"""
    conn = get_connection()
    cursor = conn.cursor()

    if section_id:
        cursor.execute("""
            SELECT u.*,
                (SELECT COUNT(*) FROM vocabulary WHERE unit_id = u.id) as word_count,
                (SELECT COUNT(*) FROM phrases WHERE unit_id = u.id) as phrase_count
            FROM units u
            WHERE u.section_id = ?
            ORDER BY u.order_num
        """, (section_id,))
    else:
        cursor.execute("""
            SELECT u.*, s.name as section_name, s.cefr_level,
                (SELECT COUNT(*) FROM vocabulary WHERE unit_id = u.id) as word_count,
                (SELECT COUNT(*) FROM phrases WHERE unit_id = u.id) as phrase_count
            FROM units u
            JOIN sections s ON u.section_id = s.id
            ORDER BY s.order_num, u.order_num
        """)

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def unlock_unit(unit_id: int):
    """Unlock a unit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE units SET is_unlocked = 1 WHERE id = ?", (unit_id,))
    conn.commit()
    conn.close()


def complete_unit(unit_id: int):
    """Mark a unit as completed and unlock next"""
    conn = get_connection()
    cursor = conn.cursor()

    # Mark current unit complete
    cursor.execute("UPDATE units SET is_completed = 1 WHERE id = ?", (unit_id,))

    # Get next unit in same section
    cursor.execute("""
        SELECT u2.id FROM units u1
        JOIN units u2 ON u1.section_id = u2.section_id AND u2.order_num = u1.order_num + 1
        WHERE u1.id = ?
    """, (unit_id,))
    next_unit = cursor.fetchone()

    if next_unit:
        cursor.execute("UPDATE units SET is_unlocked = 1 WHERE id = ?", (next_unit[0],))

    conn.commit()
    conn.close()


# ============ XP & Progress Functions ============

def add_xp(amount: int, activity_type: str, description: str = None) -> int:
    """Add XP to user and log the activity"""
    conn = get_connection()
    cursor = conn.cursor()

    # Log the XP gain
    cursor.execute("""
        INSERT INTO xp_log (activity_type, xp_amount, description)
        VALUES (?, ?, ?)
    """, (activity_type, amount, description))

    # Update total XP
    cursor.execute("""
        UPDATE user_progress SET total_xp = total_xp + ?
    """, (amount,))

    # Get new total and check for level up
    cursor.execute("SELECT total_xp FROM user_progress LIMIT 1")
    total_xp = cursor.fetchone()[0]

    # Calculate level (every 500 XP = 1 level)
    new_level = (total_xp // 500) + 1
    cursor.execute("UPDATE user_progress SET current_level = ?", (new_level,))

    conn.commit()
    conn.close()
    return total_xp


def get_user_progress() -> dict:
    """Get user progress data"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def update_streak():
    """Update the daily streak"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT last_practice_date, streak_days, longest_streak FROM user_progress LIMIT 1")
    row = cursor.fetchone()

    today = datetime.now().date()
    last_practice = None
    if row['last_practice_date']:
        last_practice = datetime.fromisoformat(row['last_practice_date']).date()

    streak = row['streak_days']
    longest = row['longest_streak']

    if last_practice == today:
        # Already practiced today
        pass
    elif last_practice == today - timedelta(days=1):
        # Consecutive day - increase streak
        streak += 1
        if streak > longest:
            longest = streak
    else:
        # Streak broken - reset to 1
        streak = 1

    cursor.execute("""
        UPDATE user_progress
        SET streak_days = ?, longest_streak = ?, last_practice_date = ?
    """, (streak, longest, today.isoformat()))

    conn.commit()
    conn.close()
    return streak


def get_xp_for_level(level: int) -> int:
    """Get XP required for a specific level"""
    return level * 500


def get_level_thresholds() -> dict:
    """Get XP thresholds for unlocking sections"""
    return {
        1: 0,      # A1.1 - Start
        2: 1000,   # A1.2
        3: 3000,   # A2.1
        4: 6000,   # A2.2
        5: 10000,  # B1.1
    }


# ============ Enhanced Vocabulary Functions ============

def add_vocabulary(spanish: str, english: str, category: str = None,
                   example_sentence: str = None, difficulty: int = 1,
                   unit_id: int = None, cefr_level: str = 'A1') -> int:
    """Add a vocabulary word"""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if word already exists
    cursor.execute("SELECT id FROM vocabulary WHERE spanish = ?", (spanish,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute("""
        INSERT INTO vocabulary (spanish, english, category, example_sentence, difficulty, unit_id, cefr_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (spanish, english, category, example_sentence, difficulty, unit_id, cefr_level))

    vocab_id = cursor.lastrowid

    # Initialize progress tracking
    cursor.execute("""
        INSERT INTO vocabulary_progress (vocabulary_id, next_review, status)
        VALUES (?, ?, 'new')
    """, (vocab_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    return vocab_id


def get_vocabulary_for_review(limit: int = 10, unit_id: int = None) -> list:
    """Get vocabulary items due for review"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT v.*, vp.ease_factor, vp.interval_days, vp.repetitions,
               vp.times_correct, vp.times_incorrect, vp.status
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.next_review <= ?
    """
    params = [datetime.now().isoformat()]

    if unit_id:
        query += " AND v.unit_id = ?"
        params.append(unit_id)

    query += " ORDER BY vp.next_review LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_vocabulary_by_id(vocab_id: int) -> dict:
    """Get a single vocabulary item by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.*, vp.ease_factor, vp.interval_days, vp.repetitions,
               vp.times_correct, vp.times_incorrect, vp.status,
               u.name as unit_name
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        LEFT JOIN units u ON v.unit_id = u.id
        WHERE v.id = ?
    """, (vocab_id,))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_vocabulary_by_status(status: str, limit: int = 20) -> list:
    """Get vocabulary items by their learning status (regardless of due date)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.*, vp.ease_factor, vp.interval_days, vp.repetitions,
               vp.times_correct, vp.times_incorrect, vp.status
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status = ?
        ORDER BY vp.times_incorrect DESC, vp.last_review ASC
        LIMIT ?
    """, (status, limit))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_vocabulary_stats() -> dict:
    """Get vocabulary learning statistics"""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # Count by status
    cursor.execute("""
        SELECT vp.status, COUNT(*) as count
        FROM vocabulary_progress vp
        GROUP BY vp.status
    """)
    for row in cursor.fetchall():
        stats[row['status']] = row['count']

    # Total vocabulary
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    stats['total'] = cursor.fetchone()[0]

    # Due for review
    cursor.execute("""
        SELECT COUNT(*) FROM vocabulary_progress
        WHERE next_review <= ? AND status != 'new'
    """, (datetime.now().isoformat(),))
    stats['due'] = cursor.fetchone()[0]

    # New words available
    cursor.execute("""
        SELECT COUNT(*) FROM vocabulary_progress WHERE status = 'new'
    """)
    stats['new_available'] = cursor.fetchone()[0]

    conn.close()
    return stats


def update_vocabulary_progress(vocabulary_id: int, quality: int):
    """
    Update vocabulary progress using improved SM-2 algorithm

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
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    progress = dict(row)
    ease_factor = progress['ease_factor']
    interval = progress['interval_days']
    repetitions = progress['repetitions']
    times_correct = progress['times_correct']
    times_incorrect = progress['times_incorrect']
    status = progress['status']

    # Update correct/incorrect counts
    if quality >= 3:
        times_correct += 1
    else:
        times_incorrect += 1

    # SM-2 algorithm with modifications
    if quality < 3:
        # Failed - reset to beginning
        repetitions = 0
        interval = 1
        status = 'struggling' if times_incorrect > 2 else 'learning'
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 3  # Changed from 6 to 3 for faster review
        elif repetitions == 2:
            interval = 7
        elif repetitions == 3:
            interval = 14
        else:
            interval = min(int(interval * ease_factor), 90)  # Cap at 90 days

        repetitions += 1

        # Update status based on progress
        if times_correct >= 4 and interval >= 7:
            status = 'learned'
        elif times_correct >= 1:
            status = 'learning'

    # Update ease factor
    ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    # Calculate next review date
    next_review = datetime.now() + timedelta(days=interval)

    cursor.execute("""
        UPDATE vocabulary_progress
        SET ease_factor = ?, interval_days = ?, repetitions = ?,
            times_correct = ?, times_incorrect = ?, status = ?,
            next_review = ?, last_review = ?
        WHERE vocabulary_id = ?
    """, (ease_factor, interval, repetitions, times_correct, times_incorrect,
          status, next_review.isoformat(), datetime.now().isoformat(), vocabulary_id))

    # Update user progress word counts
    cursor.execute("""
        UPDATE user_progress SET
            words_learning = (SELECT COUNT(*) FROM vocabulary_progress WHERE status = 'learning'),
            words_mastered = (SELECT COUNT(*) FROM vocabulary_progress WHERE status = 'learned')
    """)

    # Award XP based on quality
    xp_earned = 0
    if quality >= 3:
        xp_earned = 5 if quality == 3 else (10 if quality == 4 else 15)

    conn.commit()
    conn.close()

    if xp_earned > 0:
        add_xp(xp_earned, 'vocabulary_review', f'Reviewed vocabulary')

    return status


def get_all_vocabulary(category: str = None, unit_id: int = None, cefr_level: str = None) -> list:
    """Get all vocabulary with optional filters"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT v.*, vp.status, vp.times_correct, vp.times_incorrect
        FROM vocabulary v
        LEFT JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND v.category = ?"
        params.append(category)
    if unit_id:
        query += " AND v.unit_id = ?"
        params.append(unit_id)
    if cefr_level:
        query += " AND v.cefr_level = ?"
        params.append(cefr_level)

    query += " ORDER BY v.category, v.spanish"

    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def introduce_new_words(count: int = 5, unit_id: int = None) -> list:
    """Get new words to introduce to the learner"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT v.* FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status = 'new'
    """
    params = []

    if unit_id:
        query += " AND v.unit_id = ?"
        params.append(unit_id)

    query += " ORDER BY v.id LIMIT ?"
    params.append(count)

    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]

    # Mark these as 'learning' now that they've been seen
    for word in results:
        cursor.execute("""
            UPDATE vocabulary_progress
            SET status = 'learning', next_review = ?
            WHERE vocabulary_id = ?
        """, ((datetime.now() + timedelta(days=1)).isoformat(), word['id']))

    conn.commit()
    conn.close()
    return results


# ============ Phrase Functions ============

def add_phrase(spanish: str, english: str, category: str = None,
               difficulty: int = 1, notes: str = None,
               unit_id: int = None, cefr_level: str = 'A1') -> int:
    """Add a practice phrase"""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if phrase already exists
    cursor.execute("SELECT id FROM phrases WHERE spanish = ?", (spanish,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute("""
        INSERT INTO phrases (spanish, english, category, difficulty, notes, unit_id, cefr_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (spanish, english, category, difficulty, notes, unit_id, cefr_level))

    phrase_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return phrase_id


def get_phrases(category: str = None, difficulty: int = None, limit: int = None,
                unit_id: int = None) -> list:
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
    if unit_id:
        query += " AND unit_id = ?"
        params.append(unit_id)

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


def end_session(session_id: int, items_practiced: int, average_accuracy: float, xp_earned: int = 0):
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
        SET duration_seconds = ?, items_practiced = ?, average_accuracy = ?, xp_earned = ?, ended_at = ?
        WHERE id = ?
    """, (duration, items_practiced, average_accuracy, xp_earned, datetime.now().isoformat(), session_id))

    conn.commit()
    conn.close()


def add_practice_time(seconds: int):
    """Add practice time to total (used by smart session tracking)"""
    if seconds <= 0:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_progress
        SET total_practice_seconds = COALESCE(total_practice_seconds, 0) + ?
        WHERE id = 1
    """, (seconds,))
    conn.commit()
    conn.close()


def reset_practice_time():
    """Reset practice time to 0"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_progress SET total_practice_seconds = 0 WHERE id = 1")
    cursor.execute("DELETE FROM practice_sessions")
    conn.commit()
    conn.close()


def record_pronunciation_attempt(phrase_id: int, expected_text: str, spoken_text: str,
                                  accuracy: float, feedback: str = None) -> int:
    """Record a pronunciation attempt and award XP"""
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate XP based on accuracy
    xp_earned = 0
    if accuracy >= 95:
        xp_earned = 20
    elif accuracy >= 80:
        xp_earned = 10
    elif accuracy >= 60:
        xp_earned = 5

    cursor.execute("""
        INSERT INTO pronunciation_attempts (phrase_id, expected_text, spoken_text, accuracy, feedback, xp_earned)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (phrase_id, expected_text, spoken_text, accuracy, feedback, xp_earned))
    attempt_id = cursor.lastrowid
    conn.commit()
    conn.close()

    if xp_earned > 0:
        add_xp(xp_earned, 'pronunciation', f'{accuracy:.0f}% accuracy')

    # Update streak
    update_streak()

    return attempt_id


# ============ Statistics Functions ============

def get_statistics() -> dict:
    """Get comprehensive learning statistics"""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # User progress
    cursor.execute("SELECT * FROM user_progress LIMIT 1")
    progress = cursor.fetchone()
    if progress:
        stats['total_xp'] = progress['total_xp']
        stats['current_level'] = progress['current_level']
        stats['streak_days'] = progress['streak_days']
        stats['longest_streak'] = progress['longest_streak']
        stats['words_learning'] = progress['words_learning']
        stats['words_mastered'] = progress['words_mastered']

    # XP to next level
    next_level_xp = get_xp_for_level(stats.get('current_level', 1) + 1)
    stats['xp_to_next_level'] = next_level_xp - stats.get('total_xp', 0)

    # Total vocabulary
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    stats['total_vocabulary'] = cursor.fetchone()[0]

    # Total phrases
    cursor.execute("SELECT COUNT(*) FROM phrases")
    stats['total_phrases'] = cursor.fetchone()[0]

    # Vocabulary due for review
    cursor.execute("""
        SELECT COUNT(*) FROM vocabulary_progress
        WHERE next_review <= ? AND status IN ('learning', 'learned', 'struggling')
    """, (datetime.now().isoformat(),))
    stats['vocabulary_due'] = cursor.fetchone()[0]

    # New words available
    cursor.execute("SELECT COUNT(*) FROM vocabulary_progress WHERE status = 'new'")
    stats['new_words_available'] = cursor.fetchone()[0]

    # Total practice sessions
    cursor.execute("SELECT COUNT(*) FROM practice_sessions")
    stats['total_sessions'] = cursor.fetchone()[0]

    # Total practice time (from smart session tracking)
    cursor.execute("SELECT total_practice_seconds FROM user_progress LIMIT 1")
    total_seconds = cursor.fetchone()[0] or 0
    stats['total_practice_minutes'] = round(total_seconds / 60, 1)

    # Average accuracy
    cursor.execute("SELECT AVG(accuracy) FROM pronunciation_attempts")
    avg_accuracy = cursor.fetchone()[0]
    stats['average_accuracy'] = round(avg_accuracy, 1) if avg_accuracy else 0

    # Recent accuracy (7 days)
    cursor.execute("""
        SELECT AVG(accuracy) FROM pronunciation_attempts
        WHERE created_at > datetime('now', '-7 days')
    """)
    recent_accuracy = cursor.fetchone()[0]
    stats['recent_accuracy'] = round(recent_accuracy, 1) if recent_accuracy else 0

    # CEFR progress
    cursor.execute("""
        SELECT cefr_level, COUNT(*) as count
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status = 'learned'
        GROUP BY cefr_level
    """)
    stats['words_by_level'] = {row['cefr_level']: row['count'] for row in cursor.fetchall()}

    conn.close()
    return stats


def get_daily_goal_progress() -> dict:
    """Get progress towards daily goals"""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().date().isoformat()

    # XP earned today
    cursor.execute("""
        SELECT SUM(xp_amount) FROM xp_log
        WHERE DATE(created_at) = ?
    """, (today,))
    xp_today = cursor.fetchone()[0] or 0

    # Words reviewed today
    cursor.execute("""
        SELECT COUNT(*) FROM vocabulary_progress
        WHERE DATE(last_review) = ?
    """, (today,))
    words_reviewed = cursor.fetchone()[0]

    # Pronunciation attempts today
    cursor.execute("""
        SELECT COUNT(*) FROM pronunciation_attempts
        WHERE DATE(created_at) = ?
    """, (today,))
    pronunciations_today = cursor.fetchone()[0]

    return {
        'xp_today': xp_today,
        'xp_goal': 50,  # Daily XP goal
        'words_reviewed': words_reviewed,
        'words_goal': 10,
        'pronunciations': pronunciations_today,
        'pronunciation_goal': 5
    }


# ============ AI Coach Functions ============

def get_recommended_activities() -> list:
    """Get AI-recommended activities for today"""
    recommendations = []

    stats = get_vocabulary_stats()
    daily = get_daily_goal_progress()

    # Priority 1: Words due for review
    if stats.get('due', 0) > 0:
        recommendations.append({
            'type': 'review',
            'priority': 1,
            'title': f"Review {min(stats['due'], 10)} vocabulary words",
            'description': f"You have {stats['due']} words due for review",
            'xp_reward': 50
        })

    # Priority 2: Learn new words
    if stats.get('new_available', 0) > 0 and stats.get('due', 0) < 5:
        recommendations.append({
            'type': 'new_words',
            'priority': 2,
            'title': "Learn 5 new words",
            'description': f"{stats['new_available']} new words available",
            'xp_reward': 25
        })

    # Priority 3: Pronunciation practice
    if daily['pronunciations'] < daily['pronunciation_goal']:
        recommendations.append({
            'type': 'pronunciation',
            'priority': 3,
            'title': "Practice pronunciation",
            'description': f"{daily['pronunciations']}/{daily['pronunciation_goal']} completed today",
            'xp_reward': 30
        })

    # Priority 4: Conversation practice
    recommendations.append({
        'type': 'conversation',
        'priority': 4,
        'title': "Chat with María or Carlos",
        'description': "Practice real conversation skills",
        'xp_reward': 40
    })

    return sorted(recommendations, key=lambda x: x['priority'])


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

    stats = get_statistics()
    print(f"Statistics: {stats}")
