"""
HablaConmigo - Spanish Learning App
Main Gradio application
"""

import gradio as gr
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.audio import (
    text_to_speech,
    transcribe_audio,
    compare_pronunciation,
    get_whisper_model,
    SPANISH_VOICES
)
from src.llm import (
    chat,
    get_pronunciation_feedback,
    explain_grammar,
    get_vocabulary_help,
    get_available_models,
    translate_to_english,
    suggest_response,
    generate_memory_sentence,
    DEFAULT_MODEL
)
from src.images import get_memory_image, is_imageable
from src.database import (
    init_database,
    get_phrases,
    get_all_vocabulary,
    get_vocabulary_for_review,
    get_vocabulary_by_id,
    get_vocabulary_by_status,
    count_vocabulary_by_status,
    get_vocabulary_pipeline_stats,
    update_vocabulary_progress,
    record_pronunciation_attempt,
    get_statistics,
    start_session,
    end_session,
    get_sections,
    get_units,
    get_user_progress,
    get_vocabulary_stats,
    get_recommended_activities,
    get_daily_goal_progress,
    get_xp_for_level,
    introduce_new_words,
    get_connection,
    add_practice_time,
    reset_practice_time
)
from src.content import populate_database

# Initialize database and content
init_database()
populate_database()


# Preload Whisper model at startup to avoid timeout during first request
print("Preloading Whisper model (this may take a minute on first run)...")
get_whisper_model()
print("Whisper model loaded!")

# Global state
current_phrase = None
conversation_history = []
current_session_id = None
practice_stats = {"attempts": 0, "total_accuracy": 0}

# Smart session tracking - based on interaction gaps
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 3  # Gap threshold for session timeout
last_interaction_time = None
session_items = 0
session_total_accuracy = 0.0


def record_practice_activity(accuracy: float):
    """Record a practice activity with smart time tracking.

    Only counts time if the gap since last interaction is < 3 minutes.
    """
    global last_interaction_time, session_items, session_total_accuracy

    now = datetime.now()
    time_to_add = 0

    if last_interaction_time is not None:
        gap = (now - last_interaction_time).total_seconds()
        # Only count time if gap is less than 3 minutes (180 seconds)
        if gap < SESSION_TIMEOUT_MINUTES * 60:
            time_to_add = int(gap)

    # Update tracking
    last_interaction_time = now
    session_items += 1
    session_total_accuracy += accuracy

    # Save to database - add practice time using database function
    add_practice_time(time_to_add)

    # Also record as a session for stats
    avg_accuracy = session_total_accuracy / session_items if session_items > 0 else accuracy
    session_id = start_session("practice")
    end_session(session_id, 1, accuracy)


# ============ Speaking Practice Tab ============

def get_random_phrase(category: str = "all", voice: str = "female"):
    """Get a random phrase for practice and automatically generate audio"""
    global current_phrase

    cat = None if category == "all" else category
    phrases = get_phrases(category=cat, limit=1)
    if phrases:
        current_phrase = phrases[0]
        spanish = current_phrase['spanish']
        english = current_phrase['english']
        notes = current_phrase.get('notes', '')
        # Auto-generate audio
        audio_path = text_to_speech(spanish, voice)
        # Return None for user_recording to clear it
        return spanish, english, notes, audio_path, None
    return "No phrases found", "", "", None, None


def play_phrase_audio(spanish_text: str, voice: str = "female"):
    """Generate and return audio for the phrase"""
    if not spanish_text:
        return None
    audio_path = text_to_speech(spanish_text, voice)
    return audio_path


def evaluate_pronunciation(audio_file, expected_text: str):
    """Evaluate user's pronunciation"""
    global practice_stats

    if audio_file is None:
        return "Please record your voice first.", "", 0

    if not expected_text:
        return "No phrase to compare against.", "", 0

    try:
        # Transcribe the audio
        result = transcribe_audio(audio_file)
        spoken_text = result['text']

        # Check if transcription failed (non-Spanish detected)
        if not result.get('success', True):
            return "Audio unclear - please try again. Speak clearly into the microphone.", f"Whisper heard: {spoken_text}", 0

        # Compare pronunciation
        comparison = compare_pronunciation(expected_text, spoken_text)
        accuracy = comparison['accuracy']

        # Update stats
        practice_stats["attempts"] += 1
        practice_stats["total_accuracy"] += accuracy

        # Get detailed feedback from LLM
        feedback = get_pronunciation_feedback(expected_text, spoken_text, accuracy)

        # Record attempt in database
        if current_phrase:
            record_pronunciation_attempt(
                current_phrase['id'],
                expected_text,
                spoken_text,
                accuracy,
                feedback
            )

        # Record practice activity with smart time tracking
        record_practice_activity(accuracy)

        # Format word-by-word results
        word_results = ""
        for wr in comparison['word_results']:
            if wr['correct']:
                word_results += f"✓ {wr['expected']}\n"
            elif wr['expected'] and wr['spoken']:
                word_results += f"✗ Expected: '{wr['expected']}' → You said: '{wr['spoken']}'\n"
            elif wr['expected']:
                word_results += f"✗ Missing: '{wr['expected']}'\n"
            else:
                word_results += f"? Extra word: '{wr['spoken']}'\n"

        return feedback, word_results, accuracy

    except Exception as e:
        return f"Error processing audio: {e}", "", 0


# ============ Conversation Tab ============

def chat_with_ai(user_message: str, history: list, voice: str = "female"):
    """Chat with AI conversation partner"""
    global conversation_history

    if not user_message.strip():
        return history, "", None

    # Add user message to history for LLM
    conversation_history.append({"role": "user", "content": user_message})

    # Use Maria (female) or Carlos (male) based on voice selection
    mode = "conversation_female" if voice == "female" else "conversation_male"

    # Get AI response
    response = chat(user_message, mode=mode, history=conversation_history[:-1])

    # Add AI response to history
    conversation_history.append({"role": "assistant", "content": response})

    # Update Gradio chat history (Gradio 6.0 format)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})

    # Generate audio for auto-play with matching voice
    audio_path = text_to_speech(response, voice)

    return history, "", audio_path


def speak_ai_response(history: list):
    """Convert last AI response to speech"""
    if history and len(history) > 0:
        # Gradio 6.0 format: list of dicts with 'role' and 'content'
        last_msg = history[-1]
        if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
            content = last_msg.get("content", "")
            # Handle case where content might be a complex object
            if hasattr(content, 'text'):
                content = content.text
            elif not isinstance(content, str):
                content = str(content)
            if content:
                audio_path = text_to_speech(content, "female")
                return audio_path
    return None


def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return [], "", ""


def translate_last_response(history: list):
    """Translate the last AI response to English and show below it"""
    if not history or len(history) < 1:
        return history

    # Find the last assistant message
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content", "")

            # Handle Gradio 6.0 format where content might be a list
            if isinstance(content, list):
                # Extract text from list of content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = " ".join(text_parts)
            elif hasattr(content, 'text'):
                content = content.text

            # Skip if already has a translation
            if "_Translation:_" in str(content):
                return history

            # Translate
            translation = translate_to_english(content)

            # Add translation in smaller italic text below
            history[i]["content"] = f"{content}\n\n_Translation: {translation}_"
            break

    return history


def suggest_next_response(history: list):
    """Suggest what the user could say next"""
    global conversation_history

    if not conversation_history:
        return history, "Try saying: ¡Hola! ¿Cómo estás?"

    # Get suggestion from LLM
    suggestion = suggest_response(conversation_history)

    # Return suggestion as helper text (not added to history yet)
    return history, f"💡 Try saying: _{suggestion}_"


def transcribe_voice_input(audio_file):
    """Transcribe voice input for conversation"""
    if audio_file is None:
        return ""
    try:
        result = transcribe_audio(audio_file)
        return result['text']
    except Exception as e:
        return f"Error: {e}"


# ============ Vocabulary Tab ============

# Store the current vocab English translation for reveal
current_vocab_english = ""
# Queue for on-demand practice (struggling/learning words)
vocab_practice_queue = []
# Track offset for "Practice N Words" buttons (reset when switching status)
vocab_practice_offset = {'learning': 0, 'struggling': 0}

def get_vocab_for_review():
    """Get vocabulary items due for review - hide English initially, autoplay audio"""
    global current_vocab_english, vocab_practice_queue

    # First check if we have queued words from "Practice Struggling/Learning" buttons
    if vocab_practice_queue:
        item = vocab_practice_queue.pop(0)
        current_vocab_english = item['english']
        audio_path = text_to_speech(item['spanish'], "female")
        remaining = len(vocab_practice_queue)
        status_msg = f"({remaining} more in queue)" if remaining > 0 else ""
        return item['spanish'], f"Click 'Reveal' to see translation {status_msg}", item['id'], "", audio_path

    # Otherwise use normal spaced repetition
    vocab = get_vocabulary_for_review(limit=1)
    if vocab:
        item = vocab[0]
        current_vocab_english = item['english']
        # Generate audio for autoplay
        audio_path = text_to_speech(item['spanish'], "female")
        # Return Spanish but hide English (show placeholder), plus audio
        return item['spanish'], "Click 'Reveal' to see translation", item['id'], "", audio_path
    current_vocab_english = ""
    return "No vocabulary due for review!", "", None, "", None


def load_struggling_words():
    """Load next 20 struggling words into the practice queue"""
    global vocab_practice_queue, vocab_practice_offset

    # Get total count to know when to wrap around
    total = count_vocabulary_by_status('struggling')
    if total == 0:
        return "No struggling words found."

    # Get next batch with current offset
    words = get_vocabulary_by_status('struggling', limit=20, offset=vocab_practice_offset['struggling'])

    # If we got fewer words than requested, we've reached the end - wrap around
    if len(words) < 20:
        vocab_practice_offset['struggling'] = 0
        if len(words) == 0:
            words = get_vocabulary_by_status('struggling', limit=20, offset=0)
    else:
        vocab_practice_offset['struggling'] += 20

    if words:
        vocab_practice_queue = words
        remaining = total - vocab_practice_offset['struggling']
        if remaining < 0:
            remaining = total
        return f"📚 Loaded {len(words)} struggling words ({remaining} more available). Go to Vocabulary tab!"
    return "No struggling words found."


def load_learning_words():
    """Load next 20 learning words into the practice queue"""
    global vocab_practice_queue, vocab_practice_offset

    # Get total count to know when to wrap around
    total = count_vocabulary_by_status('learning')
    if total == 0:
        return "No learning words found."

    # Get next batch with current offset
    words = get_vocabulary_by_status('learning', limit=20, offset=vocab_practice_offset['learning'])

    # If we got fewer words than requested, we've reached the end - wrap around
    if len(words) < 20:
        vocab_practice_offset['learning'] = 0
        if len(words) == 0:
            words = get_vocabulary_by_status('learning', limit=20, offset=0)
    else:
        vocab_practice_offset['learning'] += 20

    if words:
        vocab_practice_queue = words
        remaining = total - vocab_practice_offset['learning']
        if remaining < 0:
            remaining = total
        return f"📚 Loaded {len(words)} learning words ({remaining} more available). Go to Vocabulary tab!"
    return "No learning words found."


def get_pipeline_display():
    """Generate the vocabulary pipeline display for the Home tab"""
    stats = get_vocabulary_pipeline_stats()

    learning_reps = stats['learning_by_reps']

    display = f"""### 📊 Vocabulary Pipeline

| Stage | Count | Description |
|-------|------:|-------------|
| 🆕 New | {stats['new']} | Never practiced |
| 😤 Struggling | {stats['struggling']} | Need extra practice |
| 📖 Learning (1 rep) | {learning_reps['1']} | 1 successful recall |
| 📖 Learning (2 reps) | {learning_reps['2']} | 2 successful recalls |
| 📖 Learning (3 reps) | {learning_reps['3']} | 3 successful recalls |
| 📖 Learning (4+ reps) | {learning_reps['4+']} | Almost mastered |
| ✅ Learned | {stats['learned']} | Mastered! |

**Today:** {stats['practiced_today']} practiced, {stats['remaining_today']} remaining

**Total:** {stats['total']} words
"""
    return display


def reveal_vocab_translation():
    """Reveal the English translation"""
    global current_vocab_english
    vocab = get_vocabulary_for_review(limit=1)
    if vocab:
        item = vocab[0]
        return item['english'], item.get('example_sentence', '')
    return current_vocab_english, ""


def play_vocab_audio(spanish_word: str):
    """Generate audio for vocabulary word"""
    if spanish_word and spanish_word != "No vocabulary due for review!":
        return text_to_speech(spanish_word, "female")
    return None


def submit_vocab_review(vocab_id: int, quality: int):
    """Submit vocabulary review result and get next word with autoplay"""
    if vocab_id:
        update_vocabulary_progress(vocab_id, quality)

        # Record practice activity - quality 3+ = "correct" (Good/Easy)
        accuracy = 100.0 if quality >= 3 else 0.0
        record_practice_activity(accuracy)

        return get_vocab_for_review()
    return "No vocabulary selected", "", None, "", None


def get_vocab_help(word: str):
    """Get help with a vocabulary word"""
    if word:
        return get_vocabulary_help(word)
    return ""


def help_me_remember(vocab_id: int):
    """
    Generate memory aids for the current vocabulary word:
    - An image (for concrete words)
    - A memorable sentence with audio
    """
    if not vocab_id:
        return None, "No word selected", "", None, ""

    # Get the vocabulary item directly by ID
    vocab_item = get_vocabulary_by_id(int(vocab_id))

    if not vocab_item:
        return None, "Word not found", "", None, ""

    spanish = vocab_item['spanish']
    english = vocab_item['english']
    # Use unit_name as category (category field is often None)
    category = vocab_item.get('unit_name') or vocab_item.get('category') or ''

    # Get image (only for imageable categories)
    image_url, credit, imageable = get_memory_image(spanish, english, category)

    # Generate a memorable sentence
    sentence = generate_memory_sentence(spanish, english)

    # Translate the sentence to English
    sentence_english = translate_to_english(sentence)

    # Generate audio for the sentence
    sentence_audio = text_to_speech(sentence, "female")

    # Build info message
    if imageable and not image_url:
        info = f"{credit}" if credit else "Image not found"
    elif not imageable:
        info = "This word is abstract - no image available"
    else:
        info = credit if credit else ""

    return image_url, sentence, sentence_english, sentence_audio, info


# ============ Listening Tab ============

def generate_listening_exercise(category: str = "all"):
    """Generate a listening exercise"""
    cat = None if category == "all" else category
    phrases = get_phrases(category=cat, limit=1)
    if phrases:
        phrase = phrases[0]
        audio_path = text_to_speech(phrase['spanish'], "female")
        return audio_path, phrase['spanish'], phrase['english'], ""
    return None, "", "", ""


def normalize_for_comparison(text: str) -> str:
    """Normalize text for lenient comparison (beginner-friendly).
    Removes accents, special punctuation, and normalizes whitespace.
    """
    import unicodedata

    # Remove inverted punctuation (¿ ¡) and regular punctuation
    text = text.replace('¿', '').replace('¡', '')
    text = text.replace('?', '').replace('!', '').replace(',', '').replace('.', '')

    # Normalize unicode and remove accents
    # NFD decomposes accented chars (é -> e + combining accent)
    # Then we filter out the combining marks
    normalized = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    # Lowercase and normalize whitespace
    text = ' '.join(text.lower().split())

    return text


def check_listening_answer(user_answer: str, correct_answer: str):
    """Check user's listening comprehension answer (lenient for beginners)"""
    if not user_answer or not correct_answer:
        return "Please type what you heard."

    # Normalize both for lenient comparison
    user_normalized = normalize_for_comparison(user_answer)
    correct_normalized = normalize_for_comparison(correct_answer)

    # Check for exact match after normalization
    if user_normalized == correct_normalized:
        accuracy = 100.0
    else:
        # Word-by-word comparison on normalized text
        user_words = user_normalized.split()
        correct_words = correct_normalized.split()

        correct_count = 0
        for i, word in enumerate(correct_words):
            if i < len(user_words) and user_words[i] == word:
                correct_count += 1

        total = max(len(correct_words), len(user_words))
        accuracy = (correct_count / total * 100) if total > 0 else 0

    # Record practice activity with smart time tracking
    record_practice_activity(accuracy)

    if accuracy >= 90:
        return f"✓ Excellent! {accuracy:.0f}% correct!\nYou wrote: {user_answer}"
    elif accuracy >= 70:
        return f"◐ Good! {accuracy:.0f}% correct.\nYou wrote: {user_answer}\nCorrect: {correct_answer}"
    else:
        return f"✗ Keep practicing! {accuracy:.0f}% correct.\nYou wrote: {user_answer}\nCorrect: {correct_answer}"


# ============ Grammar Tab ============

def explain_phrase_grammar(phrase: str):
    """Explain grammar in a phrase"""
    if phrase:
        return explain_grammar(phrase)
    return "Enter a Spanish phrase to analyze."


# ============ Learning Path Tab ============

def get_learning_path_display():
    """Generate visual learning path display"""
    sections = get_sections()
    units = get_units()
    progress = get_user_progress()

    # Build unit lookup by section
    units_by_section = {}
    for unit in units:
        section_id = unit['section_id']
        if section_id not in units_by_section:
            units_by_section[section_id] = []
        units_by_section[section_id].append(unit)

    # Build markdown display
    md = "## Your Learning Journey\n\n"

    for section in sections:
        section_id = section['id']
        is_unlocked = section['is_unlocked']

        # Section header
        lock_icon = "" if is_unlocked else " (Locked)"
        completed_units = section.get('completed_units', 0)
        total_units = section.get('total_units', 0)

        md += f"### {'🔓' if is_unlocked else '🔒'} {section['name']}{lock_icon}\n"
        md += f"*{section['description']}*\n\n"

        if section_id in units_by_section:
            for unit in units_by_section[section_id]:
                unit_unlocked = unit['is_unlocked']
                unit_completed = unit['is_completed']
                word_count = unit.get('word_count', 0)
                phrase_count = unit.get('phrase_count', 0)

                # Unit status icon
                if unit_completed:
                    status_icon = "✅"
                elif unit_unlocked:
                    status_icon = "📖"
                else:
                    status_icon = "🔒"

                md += f"  {status_icon} **{unit['name']}** ({word_count} words, {phrase_count} phrases)\n"

        md += "\n---\n\n"

    return md


def get_xp_display():
    """Get XP and level display"""
    progress = get_user_progress()
    total_xp = progress.get('total_xp', 0)
    level = progress.get('current_level', 1)
    streak = progress.get('streak_days', 0)
    longest_streak = progress.get('longest_streak', 0)

    # Calculate progress to next level
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    xp_in_level = total_xp - current_level_xp + 500  # Adjust for level calculation
    xp_needed = 500  # Fixed 500 XP per level
    progress_pct = min(100, int((xp_in_level / xp_needed) * 100))

    # XP progress bar
    bar_filled = int(progress_pct / 5)
    bar_empty = 20 - bar_filled
    progress_bar = "█" * bar_filled + "░" * bar_empty

    md = f"""
## Level {level}

**Total XP:** {total_xp}

**Progress to Level {level + 1}:**
`[{progress_bar}]` {progress_pct}%

**Streak:** {streak} days {"🔥" * min(streak, 7)}
**Longest Streak:** {longest_streak} days

---

### Vocabulary Progress
"""

    vocab_stats = get_vocabulary_stats()
    md += f"""
| Status | Count |
|--------|-------|
| 🆕 New | {vocab_stats.get('new', 0)} |
| 📖 Learning | {vocab_stats.get('learning', 0)} |
| ✅ Learned | {vocab_stats.get('learned', 0)} |
| ⚠️ Struggling | {vocab_stats.get('struggling', 0)} |
| 🔄 Due for Review | {vocab_stats.get('due', 0)} |
| **Total** | {vocab_stats.get('total', 0)} |
"""

    return md


def get_ai_coach_display():
    """Get AI Coach recommendations"""
    recommendations = get_recommended_activities()
    daily = get_daily_goal_progress()
    progress = get_user_progress()
    streak = progress.get('streak_days', 0)

    # Build greeting
    if streak > 0:
        greeting = f"Great to see you! You're on a **{streak}-day streak**! 🔥"
    else:
        greeting = "Welcome back! Let's start learning today!"

    md = f"""
## Your AI Coach

{greeting}

---

### Daily Goals

| Goal | Progress |
|------|----------|
| XP Today | {daily['xp_today']} / {daily['xp_goal']} |
| Words Reviewed | {daily['words_reviewed']} / {daily['words_goal']} |
| Pronunciation Practice | {daily['pronunciations']} / {daily['pronunciation_goal']} |

---

### Recommended Activities

"""

    for rec in recommendations:
        emoji = {
            'review': '📚',
            'new_words': '🆕',
            'pronunciation': '🎤',
            'conversation': '💬'
        }.get(rec['type'], '📌')

        md += f"**{emoji} {rec['title']}**\n"
        md += f"*{rec['description']}* (+{rec['xp_reward']} XP)\n\n"

    return md


def get_new_words_display():
    """Introduce new words to learn"""
    new_words = introduce_new_words(5)

    if not new_words:
        return "No new words available right now. Complete more units to unlock new vocabulary!"

    md = "## New Words to Learn\n\n"

    for word in new_words:
        md += f"**{word['spanish']}** - {word['english']}\n"
        if word.get('example_sentence'):
            md += f"*{word['example_sentence']}*\n"
        md += "\n"

    md += "\n*These words have been added to your review queue!*"

    return md


# ============ Statistics Tab ============

def get_stats_display():
    """Get formatted statistics"""
    stats = get_statistics()
    progress = get_user_progress()

    return f"""
## Your Learning Progress

### Overall Stats
| Metric | Value |
|--------|-------|
| **Level** | {progress.get('current_level', 1)} |
| **Total XP** | {progress.get('total_xp', 0)} |
| **Current Streak** | {progress.get('streak_days', 0)} days |
| **Longest Streak** | {progress.get('longest_streak', 0)} days |

### Content Progress
| Metric | Value |
|--------|-------|
| Total Vocabulary | {stats['total_vocabulary']} words |
| Words Learning | {progress.get('words_learning', 0)} |
| Words Mastered | {progress.get('words_mastered', 0)} |
| Total Phrases | {stats['total_phrases']} phrases |

### Practice Stats
| Metric | Value |
|--------|-------|
| Practice Sessions | {stats['total_sessions']} |
| Total Practice Time | {stats['total_practice_minutes']} minutes |
| Average Accuracy | {stats['average_accuracy']}% |
| Recent Accuracy (7 days) | {stats['recent_accuracy']}% |
| Vocabulary Due for Review | {stats['vocabulary_due']} words |

Keep practicing daily for best results!
"""


# ============ Build Gradio Interface ============

def create_app():
    """Create the Gradio application"""

    with gr.Blocks(
        title="HablaConmigo - Learn Spanish"
    ) as app:

        gr.Markdown("# 🇪🇸 HablaConmigo - Learn Spanish")

        with gr.Tabs():

            # ============ Learning Path Tab (HOME) ============
            with gr.Tab("🏠 Home"):
                with gr.Row():
                    with gr.Column(scale=2):
                        ai_coach_display = gr.Markdown()
                    with gr.Column(scale=1):
                        xp_display = gr.Markdown()

                with gr.Row():
                    refresh_home_btn = gr.Button("🔄 Refresh", size="sm", scale=1)
                    learn_new_btn = gr.Button("🆕 Learn 5 New Words", variant="primary", scale=2)

                new_words_display = gr.Markdown()

                gr.Markdown("**Practice on Demand:**")
                with gr.Row():
                    practice_struggling_btn = gr.Button("😤 Practice 20 Struggling Words", variant="secondary", scale=1)
                    practice_learning_btn = gr.Button("📖 Practice 20 Learning Words", variant="secondary", scale=1)

                practice_queue_status = gr.Markdown()

                # Vocabulary Pipeline View
                pipeline_display = gr.Markdown()

                with gr.Accordion("📚 Learning Path", open=False):
                    learning_path_display = gr.Markdown()
                    refresh_path_btn = gr.Button("Refresh Path")

                # Event handlers
                refresh_home_btn.click(get_ai_coach_display, outputs=[ai_coach_display])
                refresh_home_btn.click(get_xp_display, outputs=[xp_display])
                refresh_home_btn.click(get_pipeline_display, outputs=[pipeline_display])
                refresh_path_btn.click(get_learning_path_display, outputs=[learning_path_display])
                learn_new_btn.click(get_new_words_display, outputs=[new_words_display])
                practice_struggling_btn.click(load_struggling_words, outputs=[practice_queue_status])
                practice_learning_btn.click(load_learning_words, outputs=[practice_queue_status])

                # Load on startup
                app.load(get_ai_coach_display, outputs=[ai_coach_display])
                app.load(get_xp_display, outputs=[xp_display])
                app.load(get_pipeline_display, outputs=[pipeline_display])
                app.load(get_learning_path_display, outputs=[learning_path_display])

            # ============ Speaking Practice Tab ============
            with gr.Tab("🎤 Speaking Practice"):
                with gr.Row():
                    category_select = gr.Dropdown(
                        choices=["all", "greetings", "workplace", "smalltalk", "numbers", "time", "slang"],
                        value="all", label="Category", scale=1
                    )
                    voice_select = gr.Radio(choices=["female", "male"], value="female", label="Voice", scale=1)
                    new_phrase_btn = gr.Button("Get New Phrase", variant="primary", scale=1)
                    play_btn = gr.Button("🔊 Listen", scale=1)

                with gr.Row():
                    spanish_phrase = gr.Textbox(label="Spanish", interactive=False, scale=2)
                    english_phrase = gr.Textbox(label="English", interactive=False, scale=2)
                    phrase_notes = gr.Textbox(label="Notes", interactive=False, scale=1)

                with gr.Row():
                    phrase_audio = gr.Audio(label="Native", type="filepath", autoplay=True, scale=1)
                    user_recording = gr.Audio(label="Your Recording (auto-evaluates when done)", sources=["microphone"], type="filepath", scale=1)

                with gr.Row():
                    accuracy_score = gr.Number(label="Accuracy", value=0, scale=1)
                    word_comparison = gr.Textbox(label="Word Analysis", lines=2, scale=2)
                    feedback_text = gr.Textbox(label="Feedback", lines=2, scale=2)

                # Event handlers
                new_phrase_btn.click(
                    get_random_phrase,
                    inputs=[category_select, voice_select],
                    outputs=[spanish_phrase, english_phrase, phrase_notes, phrase_audio, user_recording]
                )
                play_btn.click(
                    play_phrase_audio,
                    inputs=[spanish_phrase, voice_select],
                    outputs=[phrase_audio]
                )
                # Auto-evaluate when recording changes (user stops recording)
                user_recording.change(
                    evaluate_pronunciation,
                    inputs=[user_recording, spanish_phrase],
                    outputs=[feedback_text, word_comparison, accuracy_score]
                )

            # ============ Conversation Tab ============
            with gr.Tab("💬 Conversation"):
                with gr.Row():
                    conv_voice_select = gr.Radio(
                        choices=["female", "male"], value="female",
                        label="Partner (María/Carlos)", scale=1
                    )
                    clear_btn = gr.Button("Clear Chat", scale=1)

                chatbot = gr.Chatbot(label="Conversation", height=300)

                # Help me buttons
                with gr.Row():
                    translate_btn = gr.Button("🔤 Translate", scale=1)
                    suggest_btn = gr.Button("💡 Suggest", scale=1)
                    speak_response_btn = gr.Button("🔊 Hear Again", scale=1)

                # Suggestion display area
                suggestion_text = gr.Markdown(value="", visible=True)

                with gr.Row():
                    user_input = gr.Textbox(label="Your message", placeholder="Type in Spanish...", lines=1, scale=4)
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Row():
                    voice_input = gr.Audio(label="Voice input", sources=["microphone"], type="filepath", scale=2)
                    transcribe_btn = gr.Button("Transcribe", scale=1)

                response_audio = gr.Audio(label="AI Response", type="filepath", autoplay=True)

                # Event handlers
                send_btn.click(
                    chat_with_ai,
                    inputs=[user_input, chatbot, conv_voice_select],
                    outputs=[chatbot, user_input, response_audio]
                )
                user_input.submit(
                    chat_with_ai,
                    inputs=[user_input, chatbot, conv_voice_select],
                    outputs=[chatbot, user_input, response_audio]
                )
                clear_btn.click(clear_conversation, outputs=[chatbot, user_input, suggestion_text])
                transcribe_btn.click(
                    transcribe_voice_input,
                    inputs=[voice_input],
                    outputs=[user_input]
                )
                speak_response_btn.click(
                    speak_ai_response,
                    inputs=[chatbot],
                    outputs=[response_audio]
                )
                translate_btn.click(
                    translate_last_response,
                    inputs=[chatbot],
                    outputs=[chatbot]
                )
                suggest_btn.click(
                    suggest_next_response,
                    inputs=[chatbot],
                    outputs=[chatbot, suggestion_text]
                )

            # ============ Listening Tab ============
            with gr.Tab("👂 Listening"):
                with gr.Row():
                    listen_category = gr.Dropdown(
                        choices=["all", "greetings", "workplace", "smalltalk"],
                        value="all", label="Category", scale=1
                    )
                    new_listen_btn = gr.Button("New Exercise", variant="primary", scale=1)
                    play_again_btn = gr.Button("🔊 Play Again", scale=1)

                listen_audio = gr.Audio(label="Listen...", type="filepath")

                with gr.Row():
                    user_answer = gr.Textbox(label="Type what you heard", placeholder="Spanish phrase...", scale=3)
                    check_btn = gr.Button("Check", variant="primary", scale=1)

                listen_result = gr.Textbox(label="Result", lines=2)

                with gr.Accordion("Show Answer", open=False):
                    with gr.Row():
                        correct_spanish = gr.Textbox(label="Spanish", scale=1)
                        correct_english = gr.Textbox(label="English", scale=1)

                # Event handlers
                new_listen_btn.click(
                    generate_listening_exercise,
                    inputs=[listen_category],
                    outputs=[listen_audio, correct_spanish, correct_english, user_answer]
                )
                check_btn.click(
                    check_listening_answer,
                    inputs=[user_answer, correct_spanish],
                    outputs=[listen_result]
                )

            # ============ Vocabulary Tab ============
            with gr.Tab("📚 Vocabulary"):
                with gr.Row():
                    get_vocab_btn = gr.Button("Get Word", variant="primary", scale=1)
                    vocab_audio_btn = gr.Button("🔊 Listen", scale=1)
                    reveal_btn = gr.Button("👁 Reveal", scale=1)

                with gr.Row():
                    vocab_spanish = gr.Textbox(label="Spanish", interactive=False, scale=1)
                    vocab_english = gr.Textbox(label="English", interactive=False, scale=1)
                    vocab_example = gr.Textbox(label="Example", interactive=False, scale=1)

                vocab_id = gr.Number(visible=False)
                vocab_audio = gr.Audio(label="Pronunciation", type="filepath", autoplay=True)

                # Help me remember feature
                help_remember_btn = gr.Button("💡 Help me remember", variant="secondary")
                with gr.Accordion("Memory Aid", open=False) as memory_accordion:
                    with gr.Row():
                        memory_image = gr.Image(label="Visual", scale=1)
                        with gr.Column(scale=2):
                            memory_sentence = gr.Textbox(label="Example Sentence", interactive=False)
                            memory_sentence_english = gr.Textbox(label="Example English", interactive=False)
                            memory_audio = gr.Audio(label="Listen", type="filepath", autoplay=False)
                            memory_info = gr.Markdown()

                gr.Markdown("**Rate your recall:**")
                with gr.Row():
                    btn_again = gr.Button("Again (0)", scale=1)
                    btn_hard = gr.Button("Hard (2)", scale=1)
                    btn_good = gr.Button("Good (3)", scale=1)
                    btn_easy = gr.Button("Easy (5)", scale=1)

                with gr.Row():
                    lookup_word = gr.Textbox(label="Look up word", scale=3)
                    lookup_btn = gr.Button("Explain", scale=1)
                lookup_result = gr.Textbox(label="Explanation", lines=3)

                # Event handlers
                get_vocab_btn.click(
                    get_vocab_for_review,
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                vocab_audio_btn.click(
                    play_vocab_audio,
                    inputs=[vocab_spanish],
                    outputs=[vocab_audio]
                )
                reveal_btn.click(
                    reveal_vocab_translation,
                    outputs=[vocab_english, vocab_example]
                )
                help_remember_btn.click(
                    help_me_remember,
                    inputs=[vocab_id],
                    outputs=[memory_image, memory_sentence, memory_sentence_english, memory_audio, memory_info]
                )
                btn_again.click(
                    lambda vid: submit_vocab_review(vid, 0),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                btn_hard.click(
                    lambda vid: submit_vocab_review(vid, 2),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                btn_good.click(
                    lambda vid: submit_vocab_review(vid, 3),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                btn_easy.click(
                    lambda vid: submit_vocab_review(vid, 5),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                lookup_btn.click(
                    get_vocab_help,
                    inputs=[lookup_word],
                    outputs=[lookup_result]
                )

            # ============ Grammar Tab ============
            with gr.Tab("📖 Grammar"):
                with gr.Row():
                    grammar_input = gr.Textbox(label="Spanish phrase to analyze", placeholder="e.g., Tengo que ir...", scale=3)
                    grammar_btn = gr.Button("Explain", variant="primary", scale=1)
                grammar_output = gr.Textbox(label="Explanation", lines=8)

                grammar_btn.click(
                    explain_phrase_grammar,
                    inputs=[grammar_input],
                    outputs=[grammar_output]
                )

            # ============ Statistics Tab ============
            with gr.Tab("📊 Progress"):
                stats_display = gr.Markdown()
                refresh_stats_btn = gr.Button("Refresh")
                refresh_stats_btn.click(get_stats_display, outputs=[stats_display])
                app.load(get_stats_display, outputs=[stats_display])

            # ============ Help Tab ============
            with gr.Tab("❓ Help"):
                gr.Markdown("""
## How Progress Works

### Two Progress Systems

This app tracks your progress in **two complementary ways**:

| System | What it measures | How you advance |
|--------|------------------|-----------------|
| **XP & Levels** | Overall activity & engagement | Any practice earns XP |
| **Vocabulary Mastery** | True word retention | Correct recalls over time |

---

## XP & Levels Explained

**XP (Experience Points)** rewards you for practicing:

| Activity | XP Earned |
|----------|-----------|
| Vocabulary review (correct) | 5-15 XP |
| Pronunciation 60%+ accuracy | 5 XP |
| Pronunciation 80%+ accuracy | 10 XP |
| Pronunciation 95%+ accuracy | 20 XP |

**Levels:** Every **500 XP** = 1 level up

> **Example:** At 505 XP, you're Level 2 (just crossed the 500 XP threshold)

⚠️ **Important:** Levels measure *activity*, not *mastery*. You can reach Level 10 without truly learning words if you just click through!

---

## Vocabulary Mastery Explained

Words progress through **stages** based on spaced repetition:

```
🆕 NEW → 📖 LEARNING → ✅ LEARNED
              ↑
          ⚠️ STRUGGLING (if you fail reviews)
```

### How a word becomes "Learned":

| Step | What happens | Review interval |
|------|--------------|-----------------|
| 1 | First correct recall | Wait 1 day |
| 2 | Second correct recall | Wait 3 days |
| 3 | Third correct recall | Wait 7 days |
| 4 | Fourth correct recall | Wait 14 days |
| ✅ | **LEARNED!** | Reviews continue at longer intervals |

> **Why 0 Learned?** A word needs **4+ correct recalls over 7+ days** to be "Learned". If you started recently, no word has had time to complete this journey yet!

### If you fail a review:
- The word resets to step 1
- Interval goes back to 1 day
- After multiple failures → marked as "Struggling"

---

## CEFR Sections & Unlock Requirements

The learning path has **sections** that unlock based on XP:

| Section | CEFR | XP Required | Word Target |
|---------|------|-------------|-------------|
| A1.1 - Survival Basics | A1 | 0 (unlocked) | 250 words |
| A1.2 - Daily Life | A1 | 1,000 XP | 250 words |
| A2.1 - Workplace Basics | A2 | 3,000 XP | 250 words |

---

## Your Progress Timeline

Based on typical practice patterns:

| Daily Practice | Time to "Learned" words | Time to A1.2 unlock |
|----------------|-------------------------|---------------------|
| 5 min/day | 2-3 weeks for first words | ~4 weeks |
| 15 min/day | 1-2 weeks for first words | ~2 weeks |
| 30 min/day | 1 week for first words | ~1 week |

### Realistic expectations:

- **Week 1:** Many words in "Learning", 0 "Learned" (normal!)
- **Week 2-3:** First words reach "Learned" status
- **Month 1:** 50-100 words "Learned" with consistent practice
- **Month 3:** A1.1 mastered, working on A1.2

---

## Tips for Faster Progress

1. **Review daily** - Streaks matter! Missing a day resets word intervals
2. **Be honest with ratings** - "Again" is better than guessing "Easy"
3. **Focus on due words first** - The AI Coach recommends what to do
4. **Use all features** - Speaking practice earns more XP than just vocab
5. **Quality over quantity** - 10 words truly learned > 50 words seen once

---

## Understanding Your Current Status

If you see:
- **67 Learning, 0 Learned** → You've seen 67 words, but none have completed the 4-recall journey yet. Keep reviewing daily!
- **Level 2 (505 XP)** → You've been active! But XP ≠ mastery
- **Words due: X** → These need review today to stay on track

The gap between "Learning" and "Learned" will close as you **consistently review over time**.
""")


    return app


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7860
    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        theme=gr.themes.Soft(primary_hue="orange")
    )
