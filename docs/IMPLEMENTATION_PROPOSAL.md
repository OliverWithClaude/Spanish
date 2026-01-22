# HablaConmigo Implementation Proposal: Content Discovery & DELE Preparation Features

> **Version**: 1.0
> **Date**: January 2026
> **Status**: Proposal

---

## Executive Summary

This proposal outlines a comprehensive enhancement to HablaConmigo that adds:

1. **Content Discovery System** - Find and analyze Spanish content from YouTube, websites, and podcasts
2. **Vocabulary Gap Analysis** - Compare external content against learned vocabulary
3. **DELE Exam Preparation** - Track readiness for official Spanish certification
4. **Lesson-Based Learning** - Restructure content into smaller, story-based lessons

These features transform HablaConmigo from a vocabulary trainer into a complete learning ecosystem that bridges the gap between structured learning and real-world content consumption.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Proposed Solution](#proposed-solution)
3. [Feature Specifications](#feature-specifications)
4. [Technical Architecture](#technical-architecture)
5. [Database Schema Changes](#database-schema-changes)
6. [Implementation Phases](#implementation-phases)
7. [Dependencies](#dependencies)
8. [Success Metrics](#success-metrics)

---

## Problem Statement

### Current Limitations

1. **Static Content**: Vocabulary is hardcoded in `src/content.py` with no way to add new words through the UI
2. **No Content Import**: Users cannot analyze external Spanish content against their vocabulary
3. **No Exam Alignment**: No mapping between learned vocabulary and official CEFR/DELE requirements
4. **Large Units**: Current units (~29 words each) are too large for optimal learning sessions
5. **No Story Context**: Vocabulary is learned in isolation without compelling narrative context

### User Needs

| Need | Current State | Desired State |
|------|--------------|---------------|
| Add new vocabulary | Edit source code | Import from any content source |
| Track exam readiness | Manual estimation | Automated gap analysis |
| Find appropriate content | Random searching | Smart recommendations based on level |
| Learn in context | Isolated word lists | Story-based lessons with audio |
| Measure progress | Word count only | CEFR-aligned milestones |

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HablaConmigo Enhanced                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Content   │  │  Vocabulary │  │    DELE     │  │   Lesson    │   │
│  │  Discovery  │  │     Gap     │  │   Tracker   │  │   Builder   │   │
│  │             │  │   Analysis  │  │             │  │             │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │                │          │
│         └────────────────┴────────────────┴────────────────┘          │
│                                    │                                   │
│                          ┌─────────┴─────────┐                        │
│                          │  Content Analysis │                        │
│                          │      Engine       │                        │
│                          └─────────┬─────────┘                        │
│                                    │                                   │
│  ┌─────────────────────────────────┴─────────────────────────────┐    │
│  │                      Data Layer                                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │
│  │  │Vocabulary│  │ Lessons  │  │ Packages │  │Frequency │      │    │
│  │  │ Progress │  │          │  │          │  │  Lists   │      │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Feature Specifications

### Feature 1: Content Discovery Tab

#### Purpose
Allow users to discover and analyze Spanish content from multiple sources, identifying vocabulary gaps and creating custom learning packages.

#### User Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔍 DISCOVER CONTENT                                        [Tab 10]    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─── Source Selection ─────────────────────────────────────────────┐  │
│  │  ○ Paste Text    ○ YouTube URL    ○ Website URL    ○ Upload File │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Input ────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  [Input area changes based on source selection]                  │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  [🔍 Analyze Content]                                                   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  📊 ANALYSIS RESULTS                                                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                         │
│  Source: [Title/URL]                                                    │
│  Words: 847 total | 234 unique                                          │
│                                                                         │
│  ┌─── Comprehension Breakdown ──────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  ✅ Known words:      189 (81%)  ████████████████░░░░             │  │
│  │  📖 Learning:          12 (5%)   █░░░░░░░░░░░░░░░░░░░             │  │
│  │  🆕 New words:         33 (14%)  ███░░░░░░░░░░░░░░░░░             │  │
│  │                                                                   │  │
│  │  📈 Readiness: 86% - Good match for your level!                  │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── New Words (33) ───────────────────────────────────────────────┐  │
│  │  ⭐ aventura (adventure) - High frequency, A1                     │  │
│  │  ⭐ encontrar (to find) - High frequency, A1                      │  │
│  │     perdido (lost) - Medium frequency, A2                         │  │
│  │     camino (way/path) - Medium frequency, A2                      │  │
│  │     ... [Show all 33]                                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Package Name: [_________________________]                              │
│                                                                         │
│  [➕ Create Vocabulary Package]   [💾 Save Analysis]   [🗑️ Clear]       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Functionality

| Action | Description |
|--------|-------------|
| Paste Text | Analyze any Spanish text directly |
| YouTube URL | Extract transcript and analyze vocabulary |
| Website URL | Scrape page content and analyze |
| Upload File | Accept .txt, .pdf, .srt subtitle files |
| Analyze | Process content, compare against user's vocabulary |
| Create Package | Save new words as a vocabulary package for learning |

---

### Feature 2: Vocabulary Gap Analysis Engine

#### Purpose
Core analysis engine that compares any Spanish text against the user's learned vocabulary.

#### Algorithm

```python
def analyze_content(text: str, user_id: int = 1) -> ContentAnalysis:
    """
    Analyze Spanish text against user's vocabulary.

    Returns:
        ContentAnalysis object with:
        - total_words: Total word count
        - unique_words: Unique word count
        - known_words: Words user has learned
        - learning_words: Words user is currently learning
        - new_words: Words not in user's vocabulary
        - comprehension_pct: Percentage of words user knows
        - new_words_details: List of new words with frequency/CEFR data
    """

    # 1. Tokenize and clean text
    tokens = tokenize_spanish(text)

    # 2. Lemmatize to base forms
    lemmas = [lemmatize(token) for token in tokens]
    unique_lemmas = set(lemmas)

    # 3. Get user's vocabulary status
    learned = get_vocabulary_by_status(user_id, 'learned')
    learning = get_vocabulary_by_status(user_id, 'learning')
    all_known = learned | learning

    # 4. Categorize words
    known = unique_lemmas & learned
    in_progress = unique_lemmas & learning
    new = unique_lemmas - all_known

    # 5. Enrich new words with metadata
    new_words_details = []
    for word in new:
        new_words_details.append({
            'spanish': word,
            'english': translate(word),
            'frequency_rank': get_frequency_rank(word),
            'cefr_level': estimate_cefr(word),
            'in_dele_a2': is_in_dele_list(word, 'A2')
        })

    # 6. Sort by frequency (most useful first)
    new_words_details.sort(key=lambda x: x['frequency_rank'])

    # 7. Calculate comprehension
    comprehension = len(known) / len(unique_lemmas) * 100 if unique_lemmas else 0

    return ContentAnalysis(
        total_words=len(tokens),
        unique_words=len(unique_lemmas),
        known_words=known,
        learning_words=in_progress,
        new_words=new,
        comprehension_pct=comprehension,
        new_words_details=new_words_details
    )
```

#### Word Frequency Data

Include a frequency list based on:
- RAE CREA corpus (Real Academia Española)
- Wiktionary frequency lists
- OpenSubtitles Spanish corpus

```python
# Frequency tiers
FREQUENCY_TIERS = {
    'very_high': (1, 500),      # Top 500 words - essential
    'high': (501, 1500),        # Next 1000 - common
    'medium': (1501, 3000),     # A2-B1 level
    'low': (3001, 5000),        # B1-B2 level
    'rare': (5001, float('inf')) # Advanced
}
```

---

### Feature 3: DELE Exam Readiness Tracker

#### Purpose
Track user's progress toward DELE A1, A2, B1 certification requirements.

#### User Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🎯 DELE READINESS                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Target Exam: [DELE A2 ▼]                                               │
│                                                                         │
│  ┌─── Overall Progress ─────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  A2 Readiness: 67%  ██████████████████░░░░░░░░░░                 │  │
│  │                                                                   │  │
│  │  Estimated preparation needed: 4-6 weeks                          │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Vocabulary Coverage ──────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  Core A2 Words (1000)                                             │  │
│  │  ████████████████░░░░░░░░░░░░░░  623/1000 (62%)                  │  │
│  │                                                                   │  │
│  │  A2 Verbs (50 essential)                                          │  │
│  │  ████████████████████████░░░░░░  38/50 (76%)                     │  │
│  │                                                                   │  │
│  │  A2 Topics Coverage                                               │  │
│  │  ██████████████████████░░░░░░░░  14/20 topics (70%)              │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Skill Assessment ─────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  📖 Reading:    ⭐⭐⭐⭐☆  Strong                                 │  │
│  │  👂 Listening:  ⭐⭐⭐☆☆  Moderate - increase native audio        │  │
│  │  ✍️ Writing:    ⭐⭐⭐☆☆  Moderate - practice message writing     │  │
│  │  🗣️ Speaking:   ⭐⭐☆☆☆  Needs focus - use Conversation tab      │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Missing A2 Topics ────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  ❌ Health & Body (0/25 words)                                    │  │
│  │  ❌ Travel & Transport (3/30 words)                               │  │
│  │  ❌ Past Tense Verbs - Pretérito (5/20 verbs)                     │  │
│  │  ⚠️ Hobbies & Leisure (12/25 words)                               │  │
│  │  ⚠️ Describing People (15/25 words)                               │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  [📝 Take Practice Quiz]  [📊 Full Gap Report]  [📚 Study Missing]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### DELE Topic Mapping

```python
DELE_A2_TOPICS = {
    'personal_info': {
        'name': 'Personal Information',
        'required_words': 30,
        'example_words': ['nombre', 'edad', 'profesión', 'nacionalidad']
    },
    'family': {
        'name': 'Family & Relationships',
        'required_words': 25,
        'example_words': ['padre', 'madre', 'hermano', 'casado']
    },
    'home': {
        'name': 'Home & Housing',
        'required_words': 30,
        'example_words': ['casa', 'habitación', 'cocina', 'mueble']
    },
    'daily_routine': {
        'name': 'Daily Routine',
        'required_words': 25,
        'example_words': ['levantarse', 'desayunar', 'trabajar', 'dormir']
    },
    'food_drink': {
        'name': 'Food & Drink',
        'required_words': 40,
        'example_words': ['comer', 'beber', 'agua', 'pan']
    },
    'shopping': {
        'name': 'Shopping',
        'required_words': 25,
        'example_words': ['comprar', 'precio', 'tienda', 'dinero']
    },
    'health': {
        'name': 'Health & Body',
        'required_words': 25,
        'example_words': ['médico', 'enfermo', 'cabeza', 'dolor']
    },
    'travel': {
        'name': 'Travel & Transport',
        'required_words': 30,
        'example_words': ['viajar', 'tren', 'avión', 'hotel']
    },
    'weather': {
        'name': 'Weather & Seasons',
        'required_words': 20,
        'example_words': ['tiempo', 'lluvia', 'sol', 'frío']
    },
    'work': {
        'name': 'Work & Profession',
        'required_words': 30,
        'example_words': ['trabajo', 'oficina', 'reunión', 'jefe']
    },
    # ... additional topics
}
```

---

### Feature 4: Lesson System

#### Purpose
Restructure large units into smaller, story-based lessons with 5-8 words each.

#### Lesson Structure

```python
@dataclass
class Lesson:
    id: int
    unit_id: int
    title: str                    # "María's First Day"
    story_spanish: str            # Full story in Spanish
    story_english: str            # English translation
    vocabulary: List[str]         # Target vocabulary (5-8 words)
    audio_url: Optional[str]      # External audio link (Spotify, etc.)
    comprehension_questions: List[dict]  # Questions about the story
    exercises: List[str]          # Exercise types to include
    duration_minutes: int         # Estimated completion time
    xp_reward: int               # XP for completion
```

#### Lesson Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📖 LESSON: María's First Day                            Unit 11 • 1/5  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─── Step 1: Listen & Read ────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  María llega a la [oficina] temprano. Es su primer [día] de      │  │
│  │  [trabajo]. Ella está nerviosa pero [contenta]. Su [jefe]        │  │
│  │  la saluda: "¡Buenos días, María! Bienvenida al [equipo]."       │  │
│  │                                                                   │  │
│  │  [🔊 Play Audio]  [🔄 Show/Hide Translation]                      │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Target Vocabulary: oficina, día, trabajo, contenta, jefe, equipo      │
│                                                                         │
│  ┌─── Step 2: Vocabulary Check ─────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  oficina = ?    [office]  [work]  [door]  [meeting]             │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─── Step 3: Comprehension ────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  ¿Cómo se siente María?                                          │  │
│  │  ○ Triste    ○ Nerviosa pero contenta    ○ Enfadada             │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Progress: ████████░░ Step 2 of 4                                       │
│                                                                         │
│  [← Previous]                                        [Next →]           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### New Modules

```
src/
├── content_analysis.py      # NEW: Text analysis and vocabulary comparison
├── content_sources.py       # NEW: YouTube, website, file content extraction
├── frequency_data.py        # NEW: Word frequency lookups
├── dele_tracker.py          # NEW: DELE exam readiness calculations
├── lessons.py               # NEW: Lesson management and flow
├── audio.py                 # EXISTING
├── database.py              # EXISTING (extended)
├── llm.py                   # EXISTING (extended for story generation)
├── content.py               # EXISTING
└── images.py                # EXISTING
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `content_analysis.py` | Tokenization, lemmatization, gap analysis |
| `content_sources.py` | Extract text from YouTube, websites, files |
| `frequency_data.py` | Word frequency lookups, CEFR estimation |
| `dele_tracker.py` | Track progress against DELE requirements |
| `lessons.py` | Lesson creation, flow management, exercises |

---

## Database Schema Changes

### New Tables

```sql
-- Vocabulary frequency reference data
CREATE TABLE word_frequency (
    id INTEGER PRIMARY KEY,
    spanish TEXT UNIQUE NOT NULL,
    frequency_rank INTEGER,           -- 1 = most common
    cefr_level TEXT,                  -- A1, A2, B1, B2, C1, C2
    in_dele_a1 BOOLEAN DEFAULT FALSE,
    in_dele_a2 BOOLEAN DEFAULT FALSE,
    in_dele_b1 BOOLEAN DEFAULT FALSE,
    pos TEXT,                         -- Part of speech
    english TEXT
);

-- User-imported content packages
CREATE TABLE content_packages (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,               -- "María's Adventure"
    source_type TEXT,                 -- youtube, website, text, file
    source_url TEXT,                  -- Original URL if applicable
    source_text TEXT,                 -- Full extracted text
    analysis_json TEXT,               -- Cached analysis results
    total_words INTEGER,
    unique_words INTEGER,
    new_words_count INTEGER,
    comprehension_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Words within a content package
CREATE TABLE package_vocabulary (
    id INTEGER PRIMARY KEY,
    package_id INTEGER NOT NULL,
    spanish TEXT NOT NULL,
    english TEXT,
    frequency_rank INTEGER,
    cefr_level TEXT,
    context_sentence TEXT,            -- Sentence from original content
    added_to_vocabulary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (package_id) REFERENCES content_packages(id)
);

-- Lessons (sub-divisions of units)
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    title_english TEXT,
    story_spanish TEXT,
    story_english TEXT,
    audio_url TEXT,                   -- External audio link
    order_num INTEGER DEFAULT 1,
    duration_minutes INTEGER DEFAULT 10,
    xp_reward INTEGER DEFAULT 50,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);

-- Vocabulary within lessons
CREATE TABLE lesson_vocabulary (
    id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL,
    vocabulary_id INTEGER NOT NULL,
    context_sentence TEXT,            -- How word is used in lesson story
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
);

-- Comprehension questions for lessons
CREATE TABLE lesson_questions (
    id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL,
    question_spanish TEXT NOT NULL,
    question_english TEXT,
    correct_answer TEXT NOT NULL,
    wrong_answers TEXT,               -- JSON array of wrong options
    question_type TEXT DEFAULT 'multiple_choice',
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);

-- DELE topic requirements
CREATE TABLE dele_topics (
    id INTEGER PRIMARY KEY,
    level TEXT NOT NULL,              -- A1, A2, B1, B2
    topic_key TEXT NOT NULL,          -- 'family', 'health', etc.
    topic_name TEXT NOT NULL,
    required_words INTEGER,
    description TEXT
);

-- Mapping vocabulary to DELE topics
CREATE TABLE dele_topic_vocabulary (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    vocabulary_id INTEGER NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES dele_topics(id),
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
);

-- User's listening/input hours tracking
CREATE TABLE input_tracking (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    source_type TEXT,                 -- youtube, podcast, conversation
    source_name TEXT,                 -- Video/podcast title
    duration_minutes INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_word_frequency_spanish ON word_frequency(spanish);
CREATE INDEX idx_word_frequency_rank ON word_frequency(frequency_rank);
CREATE INDEX idx_package_vocabulary_package ON package_vocabulary(package_id);
CREATE INDEX idx_lesson_vocabulary_lesson ON lesson_vocabulary(lesson_id);
CREATE INDEX idx_dele_topic_vocab ON dele_topic_vocabulary(topic_id);
```

---

## Implementation Phases

### Phase 1: Core Analysis Engine (Week 1-2)

#### Deliverables
- [ ] `src/content_analysis.py` module
- [ ] `src/frequency_data.py` with embedded frequency list
- [ ] Basic text analysis functions
- [ ] Database schema additions

#### Tasks

1. **Create frequency data module**
   ```python
   # src/frequency_data.py
   - load_frequency_list() -> Dict[str, int]
   - get_frequency_rank(word: str) -> int
   - estimate_cefr_level(word: str) -> str
   - is_in_dele_list(word: str, level: str) -> bool
   ```

2. **Create content analysis module**
   ```python
   # src/content_analysis.py
   - tokenize_spanish(text: str) -> List[str]
   - lemmatize_spanish(word: str) -> str
   - analyze_content(text: str, user_id: int) -> ContentAnalysis
   - get_vocabulary_by_status(user_id: int, status: str) -> Set[str]
   ```

3. **Database updates**
   - Add `word_frequency` table
   - Populate with top 5000 Spanish words
   - Add `content_packages` and `package_vocabulary` tables

#### Testing
- Unit tests for tokenization and lemmatization
- Integration test: analyze sample text, verify word categorization

---

### Phase 2: Content Sources (Week 3-4)

#### Deliverables
- [ ] `src/content_sources.py` module
- [ ] YouTube transcript extraction
- [ ] Website content scraping
- [ ] File upload handling

#### Tasks

1. **YouTube integration**
   ```python
   # src/content_sources.py
   - extract_youtube_transcript(url: str) -> str
   - get_youtube_metadata(url: str) -> dict
   ```

2. **Website scraping**
   ```python
   - fetch_website_content(url: str) -> str
   - clean_html_to_text(html: str) -> str
   ```

3. **File handling**
   ```python
   - extract_text_from_file(file_path: str) -> str
   - parse_srt_subtitles(content: str) -> str
   ```

#### Dependencies
- `youtube-transcript-api` for YouTube transcripts
- `beautifulsoup4` for HTML parsing
- `PyPDF2` for PDF extraction (optional)

---

### Phase 3: UI Integration (Week 5-6)

#### Deliverables
- [ ] New "Discover Content" Gradio tab
- [ ] Analysis results display
- [ ] Package creation workflow

#### Tasks

1. **Create Discover Content tab in `app.py`**
   - Source selection (text/YouTube/website/file)
   - Input area
   - Analysis results display
   - Package creation form

2. **Results visualization**
   - Comprehension percentage bar
   - Known/learning/new word breakdown
   - New words list with frequency data

3. **Package management**
   - Save packages to database
   - Add package words to vocabulary
   - Track package completion

---

### Phase 4: DELE Tracker (Week 7-8)

#### Deliverables
- [ ] `src/dele_tracker.py` module
- [ ] DELE Readiness UI section
- [ ] Topic coverage tracking

#### Tasks

1. **DELE data setup**
   - Populate `dele_topics` table with A1/A2/B1 topics
   - Map existing vocabulary to DELE topics
   - Import official DELE word lists (from Plan Curricular)

2. **Readiness calculations**
   ```python
   # src/dele_tracker.py
   - calculate_dele_readiness(user_id: int, level: str) -> DeleReadiness
   - get_missing_topics(user_id: int, level: str) -> List[Topic]
   - get_topic_coverage(user_id: int, topic: str) -> float
   ```

3. **UI additions**
   - Add DELE readiness section to Progress tab
   - Show topic coverage breakdown
   - Recommend next learning priorities

---

### Phase 5: Lesson System (Week 9-10)

#### Deliverables
- [ ] `src/lessons.py` module
- [ ] Lesson database tables
- [ ] Lesson flow UI

#### Tasks

1. **Restructure existing units into lessons**
   - Split each unit (~29 words) into 4-5 lessons (6-7 words each)
   - Create story templates for each lesson
   - Use Ollama to generate contextual stories

2. **Lesson flow implementation**
   - Story presentation with audio
   - Vocabulary highlight and practice
   - Comprehension questions
   - Completion tracking

3. **Story generation with Ollama**
   ```python
   def generate_lesson_story(vocabulary: List[str], context: str) -> str:
       """Generate a short story using target vocabulary."""
       prompt = f"""
       Create a short Spanish story (50-80 words) for A1-A2 learners.
       The story must naturally include these words: {', '.join(vocabulary)}
       Context: {context}

       Requirements:
       - Simple present tense primarily
       - Short sentences (5-10 words)
       - Clear, everyday situations
       """
       return chat(prompt, system_prompt="lesson_story_generator")
   ```

---

### Phase 6: Polish & Integration (Week 11-12)

#### Deliverables
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation

#### Tasks

1. **Testing**
   - End-to-end workflow tests
   - Edge cases (no transcript, blocked websites)
   - Performance with large texts

2. **Optimization**
   - Cache frequent lookups
   - Lazy load frequency data
   - Batch database operations

3. **Documentation**
   - Update CLAUDE.md with new features
   - User guide for content discovery
   - API documentation for new modules

---

## Dependencies

### New Python Packages

```txt
# Content extraction
youtube-transcript-api>=0.6.0    # YouTube transcripts
beautifulsoup4>=4.12.0           # HTML parsing
requests>=2.31.0                 # HTTP requests (already installed)

# Text processing
spacy>=3.7.0                     # Spanish NLP (optional, for better lemmatization)
# OR use simpler rule-based approach

# Optional
PyPDF2>=3.0.0                    # PDF text extraction
```

### External Data

1. **Frequency List**: Spanish word frequency from RAE CREA or Wiktionary
2. **DELE Vocabulary**: From Plan Curricular del Instituto Cervantes
3. **Stop Words**: Spanish stop words for filtering

---

## Success Metrics

### User Engagement
| Metric | Target |
|--------|--------|
| Content packages created per user | 5+ per month |
| Vocabulary added from packages | 50+ words per month |
| DELE tracker views | Weekly check-ins |

### Learning Outcomes
| Metric | Target |
|--------|--------|
| Vocabulary growth rate | 20% increase with new features |
| Content comprehension improvement | Measurable over time |
| DELE readiness progression | Track toward 100% |

### Technical Performance
| Metric | Target |
|--------|--------|
| Content analysis time | <5 seconds for average text |
| YouTube transcript extraction | <10 seconds |
| Database query performance | <100ms for all operations |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube blocks transcript access | High | Fallback to manual paste, consider alternatives |
| Website scraping blocked | Medium | Handle gracefully, prompt manual paste |
| Large texts slow analysis | Medium | Implement chunking, progress indicator |
| Inaccurate lemmatization | Medium | Use frequency matching as fallback |
| Storage growth | Low | Limit package history, cleanup old data |

---

## Future Enhancements (Post-MVP)

1. **AI Content Recommendations**
   - Suggest YouTube channels based on current level
   - Recommend podcasts matching skill gaps

2. **Collaborative Features**
   - Share content packages with other users
   - Community-curated content lists

3. **Spaced Repetition Integration**
   - Automatically schedule package words for review
   - Prioritize DELE-critical vocabulary

4. **Mobile Companion**
   - Offline vocabulary review
   - Listen to lesson audio on the go

5. **Progress Analytics**
   - Learning velocity tracking
   - Predicted time to next DELE level

---

## Appendix A: Sample Frequency Data Format

```python
# Top 100 Spanish words (sample)
FREQUENCY_DATA = {
    "de": {"rank": 1, "cefr": "A1", "pos": "prep", "en": "of/from"},
    "la": {"rank": 2, "cefr": "A1", "pos": "art", "en": "the (f)"},
    "que": {"rank": 3, "cefr": "A1", "pos": "conj", "en": "that/which"},
    "el": {"rank": 4, "cefr": "A1", "pos": "art", "en": "the (m)"},
    "en": {"rank": 5, "cefr": "A1", "pos": "prep", "en": "in/on"},
    "y": {"rank": 6, "cefr": "A1", "pos": "conj", "en": "and"},
    "a": {"rank": 7, "cefr": "A1", "pos": "prep", "en": "to/at"},
    "los": {"rank": 8, "cefr": "A1", "pos": "art", "en": "the (m.pl)"},
    "se": {"rank": 9, "cefr": "A1", "pos": "pron", "en": "oneself"},
    "del": {"rank": 10, "cefr": "A1", "pos": "prep", "en": "of the"},
    # ... continue to 5000+
}
```

---

## Appendix B: DELE A2 Topic List

```python
DELE_A2_REQUIRED_TOPICS = [
    "Personal identification",
    "House, home, environment",
    "Daily life",
    "Free time, entertainment",
    "Travel",
    "Relations with other people",
    "Health and body care",
    "Education",
    "Shopping",
    "Food and drink",
    "Services",
    "Places",
    "Language",
    "Weather",
    "Work and profession",
]
```

---

**Document Status**: Ready for Review
**Next Steps**: Approve and begin Phase 1 implementation
