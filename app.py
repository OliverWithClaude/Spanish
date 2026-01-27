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
    DEFAULT_MODEL,
    FAST_MODEL
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
    reset_practice_time,
    save_content_package,
    add_package_vocabulary,
    get_content_packages,
    get_package_vocabulary,
    add_package_words_to_vocabulary,
    fix_missing_translations,
    delete_vocabulary_word
)
from src.content import populate_database
from src.content_analysis import (
    analyze_content,
    get_comprehension_recommendation,
    ContentAnalysis,
    process_words_with_llm
)
from src.dele_tracker import (
    init_dele_topics,
    format_readiness_display,
    calculate_dele_readiness,
    get_study_priorities,
    add_missing_dele_vocabulary,
    get_dele_vocabulary_summary
)
from src.content_sources import (
    extract_content,
    extract_youtube_transcript,
    fetch_website_content,
    extract_text_from_file,
    detect_source_type,
    ContentResult
)

# Initialize database and content
init_database()
populate_database()
init_dele_topics()  # Initialize DELE topics


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


def delete_current_vocab(vocab_id: int):
    """Delete the current vocabulary word and get the next one."""
    if vocab_id:
        success = delete_vocabulary_word(int(vocab_id))
        if success:
            # Get next word after deletion
            next_word = get_vocab_for_review()
            return ("✅ Word deleted!",) + next_word
        else:
            return ("❌ Word not found",) + get_vocab_for_review()
    return ("No word selected",) + get_vocab_for_review()


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

    # Translate the sentence to English (use FAST_MODEL for speed - simple sentences don't need ACCURATE_MODEL)
    sentence_english = translate_to_english(sentence, model=FAST_MODEL)

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

def display_word_forms_info():
    """Display word forms generation statistics"""
    try:
        from src.word_forms import get_word_forms_count
        stats = get_word_forms_count()

        if stats['total_forms'] == 0:
            return """### 💡 Unlock the Multiplication Effect!

**What are Word Forms?**

When you learn a base verb like *hablar* (to speak) and understand present tense conjugation, you can recognize:
- hablo, hablas, habla, hablamos, habláis, hablan (6 forms!)

**The Effect:**
- **Base Vocabulary** × **Grammar Knowledge** = **Word Forms You Can Recognize**
- Example: 50 verbs × 6 conjugations = 300 recognized words!

Click **Generate Word Forms** to multiply your vocabulary comprehension.

**Status:** No word forms generated yet."""
        else:
            return f"""### 🎯 Word Forms Statistics

**Multiplication Effect Active!**

- **Base Words:** {stats['base_words_with_forms']} words
- **Total Forms:** {stats['total_forms']} forms
- **Generated Forms:** {stats['generated_forms']} additional forms
- **Multiplier:** {stats['multiplier']:.1f}x

This means you can recognize **{stats['total_forms']} different word forms** in Spanish content, not just {stats['base_words_with_forms']} base words!

Your grammar knowledge is multiplying your vocabulary comprehension by **{stats['multiplier']:.1f}x**.

Click **Generate Word Forms** again to update based on your latest vocabulary and grammar progress."""
    except Exception as e:
        return f"Error loading word forms: {e}"


def generate_word_forms_ui():
    """Generate word forms and return status message"""
    try:
        from src.word_forms import generate_all_word_forms

        # Show progress
        result = generate_all_word_forms(force_regenerate=False)

        return f"""### ✅ Word Forms Generated!

**Results:**
- **Words Processed:** {result['words_processed']}
- **Total Forms Generated:** {result['total_forms_generated']}
- **Average Multiplier:** {result['average_multiplier']:.1f}x

Your vocabulary comprehension has been multiplied! These forms will now be recognized when analyzing Spanish content.

**Next Steps:**
1. Go to **Discover** tab to analyze Spanish content
2. Import text and see how many words you now recognize
3. Your comprehension % will reflect the multiplication effect!
"""
    except Exception as e:
        return f"### ❌ Error\n\nFailed to generate word forms: {e}\n\nMake sure Ollama is running and try again."


def display_unified_cefr_score():
    """Display unified multi-dimensional CEFR proficiency score"""
    from src.database import calculate_unified_cefr_score

    result = calculate_unified_cefr_score()

    # Main score display
    main_display = f"""### Overall Proficiency: **{result['overall_cefr']}** ({result['sublevel']})

**Score: {result['overall_score']}%**

Progress to next level: {'█' * int(result['overall_score'] / 10)}{'░' * (10 - int(result['overall_score'] / 10))} {result['overall_score']}%
"""

    # Dimension displays
    vocab_dim = result['dimensions']['vocabulary']
    vocab_display = f"""**📚 Vocabulary ({result['weights']['vocabulary']}%)**

**{vocab_dim['cefr_level']}** - {vocab_dim['score']:.1f}%

{'█' * int(vocab_dim['score'] / 10)}{'░' * (10 - int(vocab_dim['score'] / 10))}

📊 {vocab_dim['effective_word_count']} effective words
🎯 Target for next level: {vocab_dim['target_benchmark']} words

✓ {vocab_dim['learned']} learned
📖 {vocab_dim['learning']} learning
⭕ {vocab_dim['new']} new
"""

    grammar_dim = result['dimensions']['grammar']
    grammar_display = f"""**📖 Grammar ({result['weights']['grammar']}%)**

**{grammar_dim['cefr_level']}** - {grammar_dim['score']:.1f}%

{'█' * int(grammar_dim['score'] / 10)}{'░' * (10 - int(grammar_dim['score'] / 10))}

✓ {grammar_dim['mastered']} mastered
📝 {grammar_dim['learned']} learned
📖 {grammar_dim['learning']} learning
"""

    speaking_dim = result['dimensions']['speaking']
    speaking_display = f"""**🗣️ Speaking ({result['weights']['speaking']}%)**

**{speaking_dim['cefr_level']}** - {speaking_dim['score']:.1f}%

{'█' * int(speaking_dim['score'] / 10)}{'░' * (10 - int(speaking_dim['score'] / 10))}

🎤 {speaking_dim['attempts']} attempts
📊 {speaking_dim['recent_avg']:.1f}% recent accuracy
"""

    content_dim = result['dimensions']['content']
    content_display = f"""**🔍 Content ({result['weights']['content']}%)**

**{content_dim['cefr_level']}** - {content_dim['score']:.1f}%

{'█' * int(content_dim['score'] / 10)}{'░' * (10 - int(content_dim['score'] / 10))}

✓ {content_dim['mastered_packages']} mastered
📦 {content_dim['total_packages']} total packages
"""

    # Gating status
    gating = result['gating']
    gating_display = f"""### Level Requirements

**A1** - ✅ Always Available
- Vocabulary: {gating['a1']['vocab_mastery']}%
- Grammar: {gating['a1']['grammar_mastery']}%

**A2** - {'✅ Unlocked' if gating['a2']['unlocked'] else '🔒 Locked'}
- Vocabulary: {gating['a2']['vocab_mastery']}% (need 80%)
- Grammar: {gating['a2']['grammar_mastery']}% (need 80%)
{'' if gating['a2']['unlocked'] else f"- {gating['a2']['requirement']}"}

**B1** - {'✅ Unlocked' if gating['b1']['unlocked'] else '🔒 Locked'}
- Vocabulary: {gating['b1']['vocab_mastery']}% (need 80%)
- Grammar: {gating['b1']['grammar_mastery']}% (need 80%)
{'' if gating['b1']['unlocked'] else f"- {gating['b1']['requirement']}"}
"""

    return main_display, vocab_display, grammar_display, speaking_display, content_display, gating_display


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


# ============ Content Analysis Functions ============

def analyze_text_content(text: str):
    """Analyze Spanish text and return results for display."""
    if not text or not text.strip():
        return "Please enter some Spanish text to analyze.", "", "", gr.update(visible=False), ""

    try:
        result = analyze_content(text)

        # Build summary display
        summary = f"""## Analysis Results

| Metric | Value |
|--------|-------|
| **Total Words** | {result.total_words} |
| **Unique Words** | {result.unique_words} |
| **Words You Know** | {result.known_count} |
| **Words Learning** | {result.learning_count} |
| **New Words** | {result.new_count} |
| **Comprehension** | {result.comprehension_pct:.1f}% |
| **Difficulty** | {result.difficulty_label} |

### Grammar Analysis

**Grammar Readiness:** {result.grammar_readiness:.1f}%

"""

        # Add grammar patterns matched
        if result.grammar_patterns_matched:
            summary += "**Grammar You Know:**\n"
            for pattern in result.grammar_patterns_matched:
                summary += f"- ✅ {pattern['display_name']} ({pattern['count']} uses)\n"
            summary += "\n"

        # Add unknown grammar patterns
        if result.grammar_patterns_unknown:
            summary += "**Grammar to Learn:**\n"
            for pattern in result.grammar_patterns_unknown:
                summary += f"- ❌ {pattern['display_name']} ({pattern['count']} uses)\n"
            summary += "\n"

        # Grammar recommendation
        from src.grammar_patterns import get_grammar_recommendation
        grammar_rec = get_grammar_recommendation(
            {'grammar_readiness': result.grammar_readiness,
             'unknown_patterns': result.grammar_patterns_unknown},
            result.comprehension_pct
        )
        summary += f"### Recommendation\n{grammar_rec}\n"
"""

        # Build new words display
        if result.new_words_details:
            new_words_md = "## New Words to Learn\n\n"
            new_words_md += "| Word | Translation | Level | Frequency | DELE A2 |\n"
            new_words_md += "|------|-------------|-------|-----------|--------|\n"

            for word in result.new_words_details[:30]:  # Limit to 30 words
                dele_marker = "✅" if word.in_dele_a2 else ""
                freq_label = "⭐" if word.frequency_rank <= 1500 else ""
                translation = word.english or "—"
                new_words_md += f"| {word.spanish} | {translation} | {word.cefr_level} | {freq_label} {word.frequency_rank} | {dele_marker} |\n"

            if len(result.new_words_details) > 30:
                new_words_md += f"\n*...and {len(result.new_words_details) - 30} more words*"
        else:
            new_words_md = "**Great!** You know all the words in this text!"

        # High value words (top frequency to prioritize)
        high_value = result.high_value_words
        if high_value:
            priority_md = f"### Priority Words ({len(high_value)} high-frequency)\n"
            priority_md += "These words appear in the top 1500 most common Spanish words:\n\n"
            priority_words = [f"**{w.spanish}** ({w.english or '?'})" for w in high_value[:10]]
            priority_md += ", ".join(priority_words)
        else:
            priority_md = ""

        # Show save button if there are new words
        show_save = len(result.new_words_details) > 0

        return summary, new_words_md, priority_md, gr.update(visible=show_save), text

    except Exception as e:
        return f"Error analyzing text: {str(e)}", "", "", gr.update(visible=False), ""


def extract_and_analyze_content(source_type: str, url_input: str, file_obj, text_input: str):
    """Extract content from various sources and analyze it."""
    # Determine source and extract content
    if source_type == "YouTube URL":
        if not url_input or not url_input.strip():
            return "Please enter a YouTube URL.", "", "", gr.update(visible=False), "", ""
        result = extract_youtube_transcript(url_input.strip())
    elif source_type == "Website URL":
        if not url_input or not url_input.strip():
            return "Please enter a website URL.", "", "", gr.update(visible=False), "", ""
        result = fetch_website_content(url_input.strip())
    elif source_type == "Upload File":
        if file_obj is None:
            return "Please upload a file (TXT, SRT, or PDF).", "", "", gr.update(visible=False), "", ""
        result = extract_text_from_file(file_obj.name)
    else:  # Paste Text
        if not text_input or not text_input.strip():
            return "Please enter some Spanish text.", "", "", gr.update(visible=False), "", ""
        # For pasted text, we just use it directly
        return analyze_text_content(text_input.strip()) + ("",)

    # Check for extraction errors
    if result.error:
        return f"**Error:** {result.error}", "", "", gr.update(visible=False), "", ""

    if not result.text:
        return "Could not extract any text from this source.", "", "", gr.update(visible=False), "", ""

    # Build source info
    source_info = f"**Source:** {result.title}"
    if result.source_url:
        source_info += f" ([link]({result.source_url}))"
    if result.duration_seconds:
        minutes = result.duration_seconds // 60
        seconds = result.duration_seconds % 60
        source_info += f" | Duration: {minutes}:{seconds:02d}"
    source_info += f"\n\n**Extracted {len(result.text)} characters**"

    # Analyze the extracted text
    analysis_result = analyze_text_content(result.text)

    # Prepend source info to the analysis summary
    if analysis_result[0]:
        updated_summary = f"{source_info}\n\n---\n\n{analysis_result[0]}"
    else:
        updated_summary = source_info

    return (updated_summary, analysis_result[1], analysis_result[2],
            analysis_result[3], analysis_result[4], result.text[:500] + "..." if len(result.text) > 500 else result.text)


def save_analysis_as_package(name: str, text: str, progress=gr.Progress()):
    """Save analyzed content as a vocabulary package.

    Uses LLM to verify words, filter out names/stop words, and get correct base forms.
    """
    if not name or not name.strip():
        return "Please enter a name for the package."

    if not text or not text.strip():
        return "No text to save. Please analyze some content first."

    try:
        # Re-analyze to get current results
        progress(0, desc="Analyzing content...")
        result = analyze_content(text)

        if result.new_count == 0:
            return "No new words to save - you already know all the vocabulary!"

        # Estimate processing time
        # Word analysis uses TRANSLATE_MODEL (translategemma:4b) - fast and accurate
        # Approximately 5-10 seconds per batch of 20 words on typical hardware
        num_words = len(result.new_words_details)
        batch_size = 20
        num_batches = (num_words + batch_size - 1) // batch_size
        estimated_seconds = num_batches * 8  # Average 8 seconds per batch for TranslateGemma 4B

        if estimated_seconds < 60:
            time_str = f"{int(estimated_seconds)}s"
        else:
            minutes = int(estimated_seconds // 60)
            seconds = int(estimated_seconds % 60)
            time_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"

        progress(0.1, desc=f"Processing {num_words} words (~{time_str} estimated)...")

        # Create a progress callback that updates Gradio progress
        def update_progress(current_batch, total_batches, message):
            # Map batch progress to 0.1-0.9 range (leave 0-0.1 and 0.9-1.0 for other steps)
            progress_value = 0.1 + (current_batch / total_batches) * 0.8
            remaining_batches = total_batches - current_batch
            remaining_seconds = int(remaining_batches * 8)  # 8 seconds per batch (TranslateGemma 4B)
            if remaining_seconds > 0:
                if remaining_seconds < 60:
                    time_remaining = f"{remaining_seconds}s"
                else:
                    mins = remaining_seconds // 60
                    secs = remaining_seconds % 60
                    time_remaining = f"{mins}m {secs}s" if secs > 0 else f"{mins}m"
                progress(progress_value, desc=f"Batch {current_batch}/{total_batches} (~{time_remaining} remaining)")
            else:
                progress(progress_value, desc=f"Batch {current_batch}/{total_batches} - Almost done!")

        # Process words through LLM to filter names, get base forms, translations
        processed_words = process_words_with_llm(result.new_words_details, text, progress_callback=update_progress)

        if not processed_words:
            return "No vocabulary words remaining after filtering names and stop words."

        # Save the package
        progress(0.9, desc="Saving package to database...")
        package_id = save_content_package(
            name=name.strip(),
            source_type='text',
            source_url='',
            source_text=text,
            analysis_data={
                'total_words': result.total_words,
                'unique_words': result.unique_words,
                'new_words_count': len(processed_words),  # Use processed count
                'comprehension_pct': result.comprehension_pct,
                'difficulty_level': result.difficulty_label
            }
        )

        # Add vocabulary to package (using LLM-processed words)
        progress(0.95, desc="Adding vocabulary to package...")
        words_data = [
            {
                'spanish': w.spanish,
                'english': w.english or '',
                'frequency_rank': w.frequency_rank,
                'cefr_level': w.cefr_level,
                'context_sentence': w.context_sentences[0] if w.context_sentences else ''
            }
            for w in processed_words
        ]
        add_package_vocabulary(package_id, words_data)

        progress(1.0, desc="Complete!")
        return f"✅ Saved package '{name}' with {len(processed_words)} words (LLM verified)!"

    except Exception as e:
        return f"Error saving package: {str(e)}"


def get_packages_display():
    """Get display of saved content packages."""
    packages = get_content_packages(limit=10)

    if not packages:
        return "No content packages saved yet. Analyze some text and save it to create your first package!"

    md = "## Your Content Packages\n\n"
    md += "| Name | New Words | Comprehension | Created |\n"
    md += "|------|-----------|---------------|--------|\n"

    for pkg in packages:
        new_words = pkg.get('new_words_count', 0)
        comp_pct = pkg.get('comprehension_pct', 0)
        created = pkg.get('created_at', '')[:10]  # Just the date
        md += f"| {pkg['name']} | {new_words} | {comp_pct:.0f}% | {created} |\n"

    return md


def get_package_choices():
    """Get packages as dropdown choices."""
    packages = get_content_packages()
    if not packages:
        return []
    return [(f"{pkg['name']} ({pkg.get('new_words_count', 0)} new words)", pkg['id']) for pkg in packages]


def add_words_from_package(package_selection):
    """Add all words from a package to vocabulary."""
    if not package_selection:
        return "Please select a package first.", gr.update(choices=get_package_choices())

    try:
        package_id = package_selection  # This is the ID from the dropdown value
        added, skipped_count, skipped = add_package_words_to_vocabulary(package_id)

        # Build status message
        msg = f"✅ Added {added} new words to your vocabulary!"
        if skipped_count > 0:
            msg += f"\n⚠️ Skipped {skipped_count} words (quality check failed):"
            for word, reason in skipped[:5]:  # Show first 5
                msg += f"\n  - {word}: {reason}"
            if skipped_count > 5:
                msg += f"\n  ... and {skipped_count - 5} more"

        return msg, gr.update(choices=get_package_choices())
    except Exception as e:
        return f"Error adding words: {str(e)}", gr.update()


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
                # Compact action buttons at the top
                with gr.Row():
                    get_vocab_btn = gr.Button("Get Word", variant="primary", size="sm")
                    btn_known = gr.Button("✓ Known", variant="secondary", size="sm")
                    reveal_btn = gr.Button("Reveal", size="sm")
                    btn_again = gr.Button("Again", variant="stop", size="sm")
                    vocab_audio_btn = gr.Button("🔊 Listen", size="sm")

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

                with gr.Row():
                    delete_vocab_btn = gr.Button("🗑️ Delete Word", variant="stop", scale=1)
                    delete_status = gr.Textbox(label="", interactive=False, scale=2, visible=True)

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
                btn_known.click(
                    lambda vid: submit_vocab_review(vid, 5),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                btn_again.click(
                    lambda vid: submit_vocab_review(vid, 0),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
                )
                delete_vocab_btn.click(
                    delete_current_vocab,
                    inputs=[vocab_id],
                    outputs=[delete_status, vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
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
                # Unified CEFR Score Section
                with gr.Row():
                    gr.Markdown("## 🎯 Your Spanish Proficiency")

                unified_score_display = gr.Markdown()
                refresh_unified_btn = gr.Button("🔄 Refresh Proficiency Score", variant="primary")

                # Dimension breakdown
                with gr.Row():
                    vocab_dimension = gr.Markdown()
                    grammar_dimension = gr.Markdown()
                    speaking_dimension = gr.Markdown()
                    content_dimension = gr.Markdown()

                # Level gating status
                with gr.Accordion("Level Unlocking Status", open=False):
                    gating_display = gr.Markdown()

                gr.Markdown("---")

                # Word Forms Generation Section
                with gr.Row():
                    gr.Markdown("## 🔄 Word Forms Multiplication Effect")

                with gr.Row():
                    with gr.Column():
                        word_forms_info = gr.Markdown()
                        with gr.Row():
                            generate_forms_btn = gr.Button("✨ Generate Word Forms", variant="primary", scale=2)
                            refresh_forms_btn = gr.Button("🔄 Refresh", scale=1)
                        generation_status = gr.Markdown(visible=True)

                gr.Markdown("---")

                # Original sections
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("## Learning Statistics")
                        stats_display = gr.Markdown()
                        refresh_stats_btn = gr.Button("🔄 Refresh Stats")
                        refresh_stats_btn.click(get_stats_display, outputs=[stats_display])

                    with gr.Column(scale=1):
                        gr.Markdown("## DELE Exam Readiness")
                        dele_level = gr.Dropdown(
                            choices=["A1", "A2"],
                            value="A1",
                            label="Target DELE Level"
                        )
                        dele_display = gr.Markdown()

                        with gr.Row():
                            refresh_dele_btn = gr.Button("🔄 Refresh", scale=1)
                            add_dele_words_btn = gr.Button("📚 Add Missing Words", variant="primary", scale=2)

                        add_words_status = gr.Markdown(visible=True)

                        def get_dele_display(level):
                            return format_readiness_display(level)

                        def add_missing_words(level):
                            """Add missing DELE vocabulary and return status."""
                            summary_before = get_dele_vocabulary_summary(level)
                            added, skipped, topics = add_missing_dele_vocabulary(level)

                            if added == 0 and skipped == 0:
                                return f"✅ **Great!** You already have all DELE {level} vocabulary!"

                            topic_list = ", ".join(topics[:5])
                            if len(topics) > 5:
                                topic_list += f" (+{len(topics)-5} more)"

                            return f"""### ✅ Words Added!

**{added}** new words added to your vocabulary
**{skipped}** words already in your collection

**Topics updated:** {topic_list}

Go to the **Vocabulary** tab to start learning these words!"""

                        refresh_dele_btn.click(
                            get_dele_display,
                            inputs=[dele_level],
                            outputs=[dele_display]
                        )
                        dele_level.change(
                            get_dele_display,
                            inputs=[dele_level],
                            outputs=[dele_display]
                        )
                        add_dele_words_btn.click(
                            add_missing_words,
                            inputs=[dele_level],
                            outputs=[add_words_status]
                        ).then(
                            get_dele_display,
                            inputs=[dele_level],
                            outputs=[dele_display]
                        )

                # Grammar Progress Section
                with gr.Row():
                    gr.Markdown("## Grammar Progress (Kwiziq Brain Map)")

                with gr.Row():
                    grammar_level_filter = gr.Dropdown(
                        choices=["All Levels", "A1", "A2", "B1"],
                        value="All Levels",
                        label="Filter by CEFR Level"
                    )
                    refresh_grammar_btn = gr.Button("🔄 Refresh", size="sm")

                grammar_summary = gr.Markdown()
                grammar_topics_display = gr.Dataframe(
                    headers=["Topic", "Level", "Category", "Status", "Practiced"],
                    datatype=["str", "str", "str", "str", "number"],
                    column_count=(5, "fixed"),
                    interactive=False,
                    wrap=True
                )

                # Topic selection and status update
                with gr.Row():
                    topic_selector = gr.Dropdown(
                        choices=[],
                        label="Select topic to update",
                        interactive=True
                    )
                    topic_status = gr.Radio(
                        choices=["new", "learning", "learned", "mastered"],
                        value="new",
                        label="Set Status",
                        interactive=True
                    )
                    update_topic_btn = gr.Button("Update Status", variant="primary")

                update_status_msg = gr.Markdown()

                def display_grammar_summary():
                    """Display grammar progress summary"""
                    from src.database import get_grammar_progress_summary

                    summary = get_grammar_progress_summary()

                    output = f"""### Progress Summary

**Total Topics:** {summary['total_topics']}
- ✅ **Mastered:** {summary.get('mastered', 0)}
- 📝 **Learned:** {summary.get('learned', 0)}
- 📖 **Learning:** {summary.get('learning', 0)}
- ⭕ **New:** {summary.get('new', 0)}

#### By CEFR Level:
"""
                    for level, data in summary['by_level'].items():
                        bar = "█" * int(data['percentage'] / 10) + "░" * (10 - int(data['percentage'] / 10))
                        output += f"\n**{level}:** {data['mastered']}/{data['total']} ({data['percentage']}%) {bar}"

                    output += "\n\n#### By Category:\n"
                    for category, data in summary['by_category'].items():
                        bar = "█" * int(data['percentage'] / 10) + "░" * (10 - int(data['percentage'] / 10))
                        output += f"\n**{category.title()}:** {data['mastered']}/{data['total']} ({data['percentage']}%) {bar}"

                    return output

                def display_grammar_topics(level_filter):
                    """Display grammar topics with progress"""
                    from src.database import get_grammar_topics_with_progress

                    cefr_level = None if level_filter == "All Levels" else level_filter
                    topics = get_grammar_topics_with_progress(cefr_level=cefr_level)

                    # Format for dataframe
                    rows = []
                    topic_choices = []

                    for topic in topics:
                        # Status emoji
                        status_map = {
                            'mastered': '✅ Mastered',
                            'learned': '📝 Learned',
                            'learning': '📖 Learning',
                            'new': '⭕ New'
                        }
                        status = status_map.get(topic.get('mastery_level', 'new'), '⭕ New')

                        rows.append([
                            topic['title'],
                            topic['cefr_level'],
                            topic['category'].title(),
                            status,
                            topic.get('times_practiced', 0)
                        ])

                        topic_choices.append(f"{topic['id']}: {topic['title']}")

                    return rows, gr.Dropdown(choices=topic_choices)

                def update_topic_status(topic_selection, new_status):
                    """Update a topic's status"""
                    if not topic_selection:
                        return "❌ Please select a topic first"

                    from src.database import update_grammar_progress

                    # Extract topic ID from selection
                    topic_id = topic_selection.split(':')[0].strip()

                    update_grammar_progress(topic_id, new_status)

                    return f"✅ Updated {topic_id} to **{new_status}**"

                # Event handlers
                refresh_grammar_btn.click(
                    display_grammar_summary,
                    outputs=[grammar_summary]
                ).then(
                    display_grammar_topics,
                    inputs=[grammar_level_filter],
                    outputs=[grammar_topics_display, topic_selector]
                )

                grammar_level_filter.change(
                    display_grammar_topics,
                    inputs=[grammar_level_filter],
                    outputs=[grammar_topics_display, topic_selector]
                )

                update_topic_btn.click(
                    update_topic_status,
                    inputs=[topic_selector, topic_status],
                    outputs=[update_status_msg]
                ).then(
                    display_grammar_summary,
                    outputs=[grammar_summary]
                ).then(
                    display_grammar_topics,
                    inputs=[grammar_level_filter],
                    outputs=[grammar_topics_display, topic_selector]
                )

                # Unified CEFR score event handlers
                refresh_unified_btn.click(
                    display_unified_cefr_score,
                    outputs=[unified_score_display, vocab_dimension, grammar_dimension, speaking_dimension, content_dimension, gating_display]
                )

                # Word forms event handlers
                refresh_forms_btn.click(
                    display_word_forms_info,
                    outputs=[word_forms_info]
                )

                generate_forms_btn.click(
                    generate_word_forms_ui,
                    outputs=[generation_status]
                ).then(
                    display_word_forms_info,
                    outputs=[word_forms_info]
                )

                # Load initial displays
                app.load(display_unified_cefr_score, outputs=[unified_score_display, vocab_dimension, grammar_dimension, speaking_dimension, content_dimension, gating_display])
                app.load(get_stats_display, outputs=[stats_display])
                app.load(lambda: format_readiness_display("A1"), outputs=[dele_display])
                app.load(display_grammar_summary, outputs=[grammar_summary])
                app.load(lambda: display_grammar_topics("All Levels"), outputs=[grammar_topics_display, topic_selector])
                app.load(display_word_forms_info, outputs=[word_forms_info])

            # ============ Content Discovery Tab ============
            with gr.Tab("🔍 Discover"):
                gr.Markdown("""## Discover Content
Import Spanish content from YouTube videos, websites, files, or paste text directly. Analyze to find new vocabulary and track your comprehension.
                """)

                with gr.Row():
                    with gr.Column(scale=2):
                        # Source type selector
                        source_type = gr.Radio(
                            choices=["Paste Text", "YouTube URL", "Website URL", "Upload File"],
                            value="Paste Text",
                            label="Content Source",
                            interactive=True
                        )

                        # URL input (for YouTube and Website)
                        url_input = gr.Textbox(
                            label="URL",
                            placeholder="Enter YouTube or website URL",
                            visible=False
                        )

                        # File upload (for files)
                        file_input = gr.File(
                            label="Upload File (TXT, SRT, or PDF)",
                            file_types=[".txt", ".srt", ".pdf"],
                            visible=False
                        )

                        # Text input (for pasting)
                        content_input = gr.Textbox(
                            label="Spanish Text",
                            placeholder="Paste Spanish text here (from articles, books, subtitles, etc.)",
                            lines=8,
                            visible=True
                        )

                        with gr.Row():
                            analyze_btn = gr.Button("🔍 Analyze Content", variant="primary", scale=2)
                            clear_btn = gr.Button("🗑️ Clear", scale=1)

                    with gr.Column(scale=1):
                        analysis_summary = gr.Markdown(label="Analysis")

                # Preview of extracted content
                extracted_preview = gr.Textbox(
                    label="Extracted Content Preview",
                    lines=3,
                    interactive=False,
                    visible=False
                )

                with gr.Row():
                    with gr.Column():
                        new_words_display = gr.Markdown()

                with gr.Row():
                    priority_words_display = gr.Markdown()

                with gr.Row(visible=False) as save_row:
                    package_name = gr.Textbox(label="Package Name", placeholder="e.g., News Article, Movie Scene")
                    save_package_btn = gr.Button("💾 Save as Package", variant="secondary")

                save_status = gr.Markdown()

                # Hidden state to store the analyzed text
                analyzed_text_state = gr.State("")

                # Function to show/hide inputs based on source type
                def update_input_visibility(selected_source):
                    return {
                        url_input: gr.update(visible=selected_source in ["YouTube URL", "Website URL"]),
                        file_input: gr.update(visible=selected_source == "Upload File"),
                        content_input: gr.update(visible=selected_source == "Paste Text"),
                    }

                source_type.change(
                    update_input_visibility,
                    inputs=[source_type],
                    outputs=[url_input, file_input, content_input]
                )

                # Main analysis handler
                def analyze_from_source(source, url, file_obj, text):
                    results = extract_and_analyze_content(source, url, file_obj, text)
                    # Show preview only if we extracted from a source (not pasted text)
                    show_preview = source != "Paste Text" and len(results) > 5 and results[5]
                    return results[:5] + (gr.update(visible=show_preview, value=results[5] if show_preview else ""),)

                analyze_btn.click(
                    analyze_from_source,
                    inputs=[source_type, url_input, file_input, content_input],
                    outputs=[analysis_summary, new_words_display, priority_words_display, save_row, analyzed_text_state, extracted_preview]
                )

                def clear_all():
                    return (
                        "Paste Text",  # source_type
                        gr.update(value="", visible=False),  # url_input
                        gr.update(value=None, visible=False),  # file_input
                        gr.update(value="", visible=True),  # content_input
                        "",  # analysis_summary
                        "",  # new_words_display
                        "",  # priority_words_display
                        gr.update(visible=False),  # save_row
                        "",  # save_status
                        gr.update(visible=False, value=""),  # extracted_preview
                    )

                clear_btn.click(
                    clear_all,
                    outputs=[source_type, url_input, file_input, content_input, analysis_summary,
                             new_words_display, priority_words_display, save_row, save_status,
                             extracted_preview]
                )

                save_package_btn.click(
                    save_analysis_as_package,
                    inputs=[package_name, analyzed_text_state],
                    outputs=[save_status],
                    show_progress="full"
                )

                gr.Markdown("---")
                gr.Markdown("### Your Saved Packages")
                packages_display = gr.Markdown()

                with gr.Row():
                    package_selector = gr.Dropdown(
                        label="Select a package to add words",
                        choices=[],
                        interactive=True,
                        scale=3
                    )
                    add_words_btn = gr.Button("➕ Add Words to Vocabulary", variant="primary", scale=1)

                add_words_status = gr.Markdown()
                refresh_packages_btn = gr.Button("🔄 Refresh Packages")

                # Event handlers for packages
                refresh_packages_btn.click(get_packages_display, outputs=[packages_display])
                refresh_packages_btn.click(lambda: gr.update(choices=get_package_choices()), outputs=[package_selector])
                add_words_btn.click(
                    add_words_from_package,
                    inputs=[package_selector],
                    outputs=[add_words_status, package_selector]
                )

                # Also refresh after saving a package
                save_package_btn.click(get_packages_display, outputs=[packages_display])
                save_package_btn.click(lambda: gr.update(choices=get_package_choices()), outputs=[package_selector])

                # Load on startup
                app.load(get_packages_display, outputs=[packages_display])
                app.load(lambda: gr.update(choices=get_package_choices()), outputs=[package_selector])

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

            # ============ Links Tab ============
            with gr.Tab("🔗 Links"):
                gr.Markdown("## 📚 Spanish Learning Resources")
                gr.Markdown("Curated links to excellent Spanish learning materials that complement HablaConmigo.")

                # Resource 1: Small Town Spanish Teacher
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 120px; line-height: 1;">🐘</div>
                        </div>
                        """)
                    with gr.Column(scale=3):
                        gr.Markdown("""
### Small Town Spanish Teacher - Simple Stories

**Perfect for:** Content Discovery & Comprehensible Input

The stories start with a friendly elephant character and progress in difficulty. These are **ideal for copying into the Discover module** to:
- Build vocabulary from context
- Practice reading comprehension
- Find new words at your level
- Analyze authentic Spanish text

**How to use:**
1. Visit the page and find a story at your level
2. Copy the Spanish text
3. Go to HablaConmigo's **Discover** tab
4. Paste the text and click "Analyze Content"
5. Save as a package and add words to your vocabulary

[📖 Open Simple Stories →](https://smalltownspanishteacher.com/simple-stories-in-spanish-all-episodes/){:target="_blank"}
                        """)
                        gr.HTML('<a href="https://smalltownspanishteacher.com/simple-stories-in-spanish-all-episodes/" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">📖 Visit Simple Stories</a>')

                gr.Markdown("---")

                # Resource 2: Dreaming Spanish
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 120px; line-height: 1;">💭</div>
                            <div style="font-size: 40px; margin-top: 10px;">🇪🇸</div>
                        </div>
                        """)
                    with gr.Column(scale=3):
                        gr.Markdown("""
### Dreaming Spanish - Video Platform

**Perfect for:** Immersive Listening & Comprehensible Input

Hundreds of videos in **easy and intermediate Spanish** with visual context. The platform is designed for language acquisition through comprehensible input.

**Recommended practice:**
- Watch **15 minutes daily** for "learning while you dream" experience
- Start with Superbeginner videos (lots of visual support)
- Progress to Beginner, then Intermediate
- No subtitles needed - learn from context!

**Why it works:**
The method focuses on understanding meaning through context, not translation. Combined with HablaConmigo's active practice, this passive listening accelerates your comprehension.

[🎥 Browse Videos →](https://app.dreaming.com/spanish/browse){:target="_blank"}
                        """)
                        gr.HTML('<a href="https://app.dreaming.com/spanish/browse" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #7c3aed; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">🎥 Open Dreaming Spanish</a>')

                gr.Markdown("---")

                # Resource 3: Kwiziq Spanish
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 120px; line-height: 1;">📝</div>
                            <div style="font-size: 40px; margin-top: 10px;">✓</div>
                        </div>
                        """)
                    with gr.Column(scale=3):
                        gr.Markdown("""
### Kwiziq Spanish - Interactive Quizzes

**Perfect for:** Grammar Practice & Level Assessment (A0-A2)

Quiz-based platform specifically designed for beginner Spanish learners. Tests your knowledge and tracks weak areas with adaptive quizzes.

**What you get:**
- **Targeted quizzes** for A0, A1, and A2 levels (perfect match for HablaConmigo!)
- **Grammar-focused practice** with immediate feedback
- **Progress tracking** to see which topics you've mastered
- **Personalized study plan** based on your quiz results

**How to use:**
- Login with your Google credentials (quick and easy)
- Take quizzes to identify grammar gaps
- Use HablaConmigo to practice words from weak areas
- Combine with Discover module to reinforce tricky grammar in context

**Why it complements HablaConmigo:**
While HablaConmigo focuses on speaking and vocabulary, Kwiziq drills grammar rules. Together they give you both **practical fluency** (HablaConmigo) and **grammatical accuracy** (Kwiziq).

[📝 Take Quizzes →](https://spanish.kwiziq.com/my-languages/spanish){:target="_blank"}
                        """)
                        gr.HTML('<a href="https://spanish.kwiziq.com/my-languages/spanish" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #059669; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">📝 Open Kwiziq Spanish</a>')

                gr.Markdown("---")

                gr.Markdown("""
### 💡 How to Use These Resources Together

**Daily Routine Suggestion:**
1. **Morning (5 min):** Review due vocabulary in HablaConmigo
2. **Mid-day (15 min):** Watch one Dreaming Spanish video
3. **Afternoon (10 min):** Take a Kwiziq quiz on today's grammar topic
4. **Evening (10 min):** Read a Simple Story, discover new words in HablaConmigo
5. **Before bed (5 min):** Quick speaking practice or conversation

**Content Discovery Workflow:**
1. Find interesting content (stories, video transcripts, articles)
2. Copy Spanish text into HablaConmigo's Discover tab
3. Analyze to see which words you know vs. need to learn
4. Save as package and add new words to vocabulary
5. Practice those words with spaced repetition

**Complete Learning System:**

This combination gives you a **balanced approach**:
- 📖 **Reading input** (Simple Stories)
- 👂 **Listening input** (Dreaming Spanish videos)
- 📝 **Grammar practice** (Kwiziq quizzes)
- 🗣️ **Speaking output** (HablaConmigo)
- 💪 **Active recall** (HablaConmigo vocabulary drills)

**Why this works:**
- **Input first** (stories, videos) → builds comprehension
- **Grammar drills** (Kwiziq) → solidifies structure
- **Active practice** (HablaConmigo) → develops fluency
- **Spaced repetition** → ensures long-term retention

All three resources target **A0-A2 levels**, perfectly aligned with your learning journey!
                """)


    return app


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7860

    # Fix any vocabulary words with missing translations
    fixed = fix_missing_translations()
    if fixed > 0:
        print(f"Fixed {fixed} vocabulary words with missing translations")

    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        theme=gr.themes.Soft(
            primary_hue="violet",
            secondary_hue="slate",
            neutral_hue="gray"
        )
    )
