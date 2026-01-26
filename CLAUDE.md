# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HablaConmigo is an AI-powered Spanish learning app focused on speaking and listening skills with Madrid workplace context. It uses Whisper (speech-to-text), Edge TTS (text-to-speech), Ollama (local LLM), and SQLite in a Gradio web UI.

## Commands

```bash
# Run the app (requires Ollama running separately)
python app.py

# Run on custom port
python app.py 7861

# Install dependencies
pip install -r requirements.txt

# Pull required LLM model
ollama pull llama3.2
```

**Prerequisite**: Ollama must be running (`ollama serve` in separate terminal).

## Architecture

### Module Responsibilities

| File | Purpose |
|------|---------|
| `app.py` | Main Gradio UI with 9 tabs, global state, session tracking |
| `src/audio.py` | Whisper transcription + Edge TTS generation |
| `src/llm.py` | Ollama chat integration + system prompts for different personas |
| `src/database.py` | SQLite schema, SM-2 spaced repetition, XP/progress tracking |
| `src/content.py` | 429 vocabulary words + 204 phrases (CEFR A1-A2) |
| `src/images.py` | Unsplash API integration for vocabulary images |
| `src/dele_tracker.py` | DELE exam readiness tracking and vocabulary gap analysis |
| `src/content_analysis.py` | Text analysis, tokenization, vocabulary comparison |
| `src/frequency_data.py` | Spanish word frequency data (~5000 words) |

### Key Data Flows

**Speaking Practice**: `get_random_phrase()` → `text_to_speech()` → user records → `transcribe_audio()` → `compare_pronunciation()` → `get_pronunciation_feedback()` → `record_pronunciation_attempt()` → `add_xp()`

**Vocabulary Review**: `get_vocabulary_for_review()` (SM-2 query) → show word → user rates recall → `update_vocabulary_progress()` (SM-2 update) → `record_practice_activity()`

**Conversation**: User message → `chat()` with conversation history → AI response → `text_to_speech()` → append to `conversation_history`

**DELE Readiness**: `calculate_dele_readiness(level)` → compares user vocabulary against DELE topic requirements → weighted scoring (learned=1.0, learning=0.5) → displays progress in Progress tab

**Content Discovery**: Paste text → `analyze_content()` → tokenize/lemmatize → compare against user vocabulary → create package → `add_package_words_to_vocabulary()`

**Grammar Progress Tracking**: User marks Kwiziq topics as learned → `update_grammar_progress()` → stores status (new/learning/learned/mastered) → `get_grammar_progress_summary()` → displays progress by CEFR level and category in Progress tab

### State Management

Global variables in `app.py` track session state:
- `current_phrase` - active phrase for speaking practice
- `conversation_history` - chat context for AI partners
- `practice_stats` - session timing with 3-minute gap detection

### Database Tables

Core tables: `sections`, `units`, `vocabulary`, `vocabulary_progress` (SM-2), `phrases`, `practice_sessions`, `pronunciation_attempts`, `conversations`, `user_progress`, `xp_log`, `settings`

DELE tables: `dele_topics`, `dele_topic_vocabulary`, `dele_core_vocabulary`

Content Discovery tables: `content_packages`, `package_vocabulary`, `input_tracking`

Grammar Tracking tables: `grammar_topics`, `grammar_dependencies`, `grammar_user_progress`, `word_forms`, `morphology_rules`, `grammar_coverage`, `grammar_practice_log`

XP thresholds: Level 1 = 0 XP, Level 5 = 1,000 XP (A1.2 unlock), Level 10 = 3,000 XP (A2.1 unlock)

### Audio Processing Notes

- Whisper lazy-loads on first use (~30 seconds)
- Edge TTS uses async with event loop handling for Gradio
- FFmpeg auto-detected from WinGet paths on Windows
- Voices: María (ElviraNeural) and Carlos (AlvaroNeural)

### LLM Personas

System prompts in `src/llm.py` define:
- `conversation_female/male` - María/Carlos personas
- `pronunciation_feedback` - coaching mode (English output)
- `grammar_explanation` - teaching mode
- `vocabulary_helper` - definitions
- `translate` - Spanish→English
- `suggest_response` - context-aware suggestions
- `memory_sentence` - generates vivid sentences for vocabulary memorization

## Configuration

### LLM Model Configuration

Four-tier model strategy in `src/llm.py`:
- `FAST_MODEL` (llama3.2:latest): Conversation, pronunciation feedback, suggestions
- `ACCURATE_MODEL` (qwen3:30b): Grammar explanations, vocabulary definitions (teaching mode)
- `TRANSLATE_MODEL` (translategemma:4b): Spanish↔English translation + word analysis (Google's TranslateGemma, Jan 2026)
- `MEMORY_MODEL` (gemma2:2b): Memory sentence generation (optimized for 100% word inclusion)

**Note:** Word analysis was moved from ACCURATE_MODEL to TRANSLATE_MODEL for better performance (5-10x faster) and more reliable JSON output.

Temperature settings per task type are defined in `TEMPERATURE_SETTINGS` dict.

**Translation Model:** TranslateGemma 4B is a specialized translation model from Google, optimized for 55 languages. Benchmark testing (see `TRANSLATEGEMMA_BENCHMARK_RESULTS.md`) showed it provides optimal speed/quality balance:
- **Speed:** 287ms average (2.7x faster than 27B model)
- **Quality:** 4.17/5 (only 1.4% lower than 27B)
- **VRAM:** 3.3GB (vs 17GB for 27B), leaving more memory for other models
- **Use cases:** Excels at simple sentences, conversations, and complex content

**Performance Note:** The "Help me remember" feature uses MEMORY_MODEL for generation (~500ms) and TRANSLATE_MODEL for translation (~377ms), achieving ~877ms total response time (well under 2s target) with excellent quality.

### Other Settings

- Voices are hardcoded in `src/audio.py` `SPANISH_VOICES` dict
- Database auto-creates on first run in `data/hablaconmigo.db`

## Unsplash API Setup (Optional)

The "Help me remember" feature in the Vocabulary tab uses Unsplash for images. To enable it:

1. **Create a free Unsplash account** at https://unsplash.com/join

2. **Create an application** at https://unsplash.com/oauth/applications
   - Click "New Application"
   - Accept the API guidelines
   - Give your app a name (e.g., "HablaConmigo")

3. **Copy your Access Key** from the application page

4. **Create a `.env` file** in the project root (copy from `.env.example`):
   ```
   UNSPLASH_API_KEY=your_access_key_here
   ```

The `.env` file is automatically loaded when the app starts and is gitignored for security.

**Note**: The free tier allows 50 requests/hour. Without the API key, the "Help me remember" feature still works but without images.

## DELE Exam Tracker

The Progress tab includes DELE exam readiness tracking for A1 and A2 levels.

### How Readiness is Calculated

- **Vocabulary Coverage**: Compares user's practiced words against DELE topic keywords
- **Topic Completion**: Percentage of topics with 80%+ coverage
- **Core Verbs**: Coverage of essential verbs for each level

### Word Weighting

Words are weighted by learning status:
- `learned` / `due`: 1.0 (full credit)
- `learning`: 0.5 (half credit)
- `new` / `struggling`: 0.0 (not counted)

### DELE A1 Topics (174 words)

Greetings, Personal Info, Numbers, Time & Dates, Family, Colors, Basic Verbs, Basic Food & Drink

### Add Missing Words

The "Add Missing Words" button adds all DELE vocabulary not yet in your database. Words are added with status `new` - practice them in the Vocabulary tab to increase your readiness score.

## Grammar Progress Tracking (Kwiziq Brain Map)

The Progress tab includes a grammar tracking system aligned with Kwiziq's brain map structure, allowing you to track grammar topics you've mastered.

### Features

- **43 Grammar Topics** imported across A1-B1 CEFR levels
- **Progress Summary** showing breakdown by status (new/learning/learned/mastered)
- **CEFR Level Breakdown** with progress bars for A1, A2, B1
- **Category Breakdown** by grammar type (verbs, nouns, adjectives, pronouns, articles, syntax)
- **Topic Dependencies** mapped (prerequisites that must be learned first)

### Database Setup

Run the setup script to initialize grammar topics:
```bash
python setup_grammar_database.py
```

This imports 43 topics from `SPANISH_GRAMMAR_TAXONOMY.json` into the database.

### Usage

1. Navigate to the **Progress** tab in the app
2. Scroll down to the "Grammar Progress (Kwiziq Brain Map)" section
3. View your current progress summary
4. Filter topics by CEFR level (A1, A2, B1, or All)
5. Select a topic from the dropdown
6. Set its status: new → learning → learned → mastered
7. Click "Update Status"

### Status Levels

- **new** (0% proficiency) - Haven't learned yet
- **learning** (30% proficiency) - Currently studying
- **learned** (70% proficiency) - Practiced and familiar
- **mastered** (100% proficiency) - Fully mastered

### Integration with Kwiziq

Check your progress on Kwiziq.com and manually update corresponding topics in HablaConmigo to maintain synchronized tracking.

### Related Files

- `SPANISH_GRAMMAR_TAXONOMY.json` - Complete taxonomy with 43 topics and dependencies
- `IMPLEMENTATION_SCHEMA.sql` - Database schema for grammar tables
- `setup_grammar_database.py` - Script to import topics into database
- `test_grammar_ui.py` - Test suite for grammar progress functions
- `PHASE_3_COMPLETE.md` - Full implementation documentation

## Testing Notes

No automated tests exist. Manual testing required:
1. Verify Ollama is running before app startup
2. Test microphone permissions in browser
3. First Whisper transcription is slow (model loading)
