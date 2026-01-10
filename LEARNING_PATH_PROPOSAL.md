# Learning Path & Progress System Proposal

## Research Summary

### CEFR Levels & Vocabulary Requirements

| Level | Description | Vocabulary | Hours to Achieve | Can Do |
|-------|-------------|------------|------------------|--------|
| **A1** | Beginner | 500-1,000 words | 40-60 hours | Basic phrases, introductions, simple questions |
| **A2** | Elementary | 1,000-2,500 words | 80-120 hours | Everyday expressions, simple tasks, describe background |
| **B1** | Intermediate | 2,000-3,250 words | 150-200 hours | Main points of clear speech, travel situations, simple text |
| **B2** | Upper-Intermediate | 4,000-5,000 words | 300-400 hours | Complex text, fluent conversation, clear detailed text |

*Source: [Universe of Memory](https://universeofmemory.com/how-many-words-you-should-know/), [Text Inspector CEFR Guide](https://textinspector.com/cefr-levels-faq-guide/)*

### How Professional Apps Structure Learning

**Duolingo's Approach:**
- Courses split into **Sections** aligned with CEFR levels
- Each section contains **Units** (topics)
- Each unit contains **Levels** (lessons)
- Spanish course: 230 units across 9 sections (A1 → B2)
- Spaced repetition sprinkled throughout the path
- Score out of 160 points tracking progress

*Source: [Duolingo Learning Path](https://duoplanet.com/duolingo-learning-path/)*

### Spaced Repetition Best Practices

Research shows a word needs to be:
1. **Successfully recalled 4+ times** → enters short-term memory
2. **Retained for 7+ days** → transfers to long-term memory
3. **Review intervals**: 1 day → 3 days → 1 week → 2 weeks → 1 month → 3 months

*Source: [Spaced Repetition Guide](https://www.heylama.com/blog/spaced-repetition)*

---

## Current App Issues

1. **No structured learning path** - Random phrases without progression
2. **Vocabulary runs out quickly** - Only ~35 words in database
3. **Progress tracking incomplete** - Statistics not reflecting actual progress
4. **No CEFR alignment** - Can't measure proficiency level
5. **No unlocking mechanism** - Everything available from start
6. **No AI coaching** - No guidance on what to learn next

---

## Proposed Learning Path Architecture

### 1. CEFR-Aligned Sections

```
SECTION 1: A1.1 - Survival Basics (Target: 250 words)
├── Unit 1: Greetings & Introductions
├── Unit 2: Numbers 1-20
├── Unit 3: Basic Questions (What, Where, Who)
├── Unit 4: Family & People
├── Unit 5: Time & Days
└── Unit 6: Checkpoint + Review

SECTION 2: A1.2 - Daily Life (Target: 500 words)
├── Unit 7: Food & Drinks
├── Unit 8: At the Restaurant
├── Unit 9: Shopping Basics
├── Unit 10: Weather & Seasons
├── Unit 11: Describing Things (Adjectives)
└── Unit 12: Checkpoint + Review

SECTION 3: A2.1 - Workplace Basics (Target: 750 words)
├── Unit 13: Office Vocabulary
├── Unit 14: Meetings & Schedules
├── Unit 15: Email & Communication
├── Unit 16: Asking for Help
├── Unit 17: Present Tense Verbs
└── Unit 18: Checkpoint + Review

SECTION 4: A2.2 - Social Conversations (Target: 1000 words)
├── Unit 19: Weekend & Hobbies
├── Unit 20: Making Plans
├── Unit 21: Past Tense (What happened)
├── Unit 22: Expressing Opinions
├── Unit 23: Madrid Culture & Slang
└── Unit 24: Checkpoint + Review

... continue to B1, B2
```

### 2. Unit Structure

Each unit contains:
- **10-20 vocabulary words** (with audio, examples)
- **5-10 phrases** for practice
- **3 conversation scenarios**
- **1 grammar point** (optional)
- **1 cultural note** (Madrid-specific)

### 3. Lesson Types per Unit

```
Unit X: [Topic Name]
├── Lesson 1: Introduction (Listen & Read)
├── Lesson 2: Vocabulary (Flashcards)
├── Lesson 3: Pronunciation Practice
├── Lesson 4: Listening Comprehension
├── Lesson 5: Conversation Practice
├── Lesson 6: Review & Quiz
└── [UNLOCK NEXT UNIT when 80% complete]
```

### 4. XP & Scoring System

| Activity | XP Earned |
|----------|-----------|
| Complete vocabulary flashcard | 5 XP |
| Pronunciation attempt (any) | 5 XP |
| Pronunciation 80%+ accuracy | 10 XP |
| Pronunciation 95%+ accuracy | 20 XP |
| Conversation exchange | 15 XP |
| Listening exercise correct | 10 XP |
| Daily streak bonus | 50 XP |
| Unit completion | 100 XP |
| Section completion | 500 XP |

**Level Thresholds:**
- Level 1: 0 XP (A1.1 Start)
- Level 5: 1,000 XP (A1.2 Unlocks)
- Level 10: 3,000 XP (A2.1 Unlocks)
- Level 15: 6,000 XP (A2.2 Unlocks)
- Level 20: 10,000 XP (B1.1 Unlocks)

### 5. AI Coach Features

**Daily Guidance:**
```
"¡Buenos días! 👋

Today's Focus: Unit 3 - Basic Questions
📊 Your Progress: 45% through A1.1

Recommended activities:
1. Review 5 vocabulary words due today
2. Practice asking '¿Dónde está...?' (Where is...)
3. 5-minute conversation with María

💪 You're on a 3-day streak! Keep it up!"
```

**Adaptive Recommendations:**
- Track weak areas (e.g., pronunciation of "rr")
- Suggest extra practice for struggling words
- Adjust difficulty based on performance
- Celebrate milestones

**Weekly Progress Report:**
```
📈 Week 3 Summary

Words Learned: 47 (+12 this week)
Words Mastered: 31 (reviewed 4+ times)
Practice Time: 45 minutes
Accuracy Trend: 72% → 78% ↑

🎯 Current Level: A1.1 (68% complete)
🔜 Next Milestone: Unlock A1.2 in ~2 weeks

Focus Areas:
- Numbers 11-20 need more practice
- Great improvement on greetings!
```

### 6. Improved Spaced Repetition

**Current Issue:** Words reviewed but marked as "done" too quickly

**Fix:** Implement proper SM-2 with these rules:
1. New word → review in 1 day
2. Correct once → review in 3 days
3. Correct twice → review in 1 week
4. Correct 3x → review in 2 weeks
5. Correct 4x → review in 1 month (LEARNED)
6. Any mistake → reset to step 1

**Word States:**
- 🆕 New (not seen)
- 📖 Learning (seen < 4 times)
- ✅ Learned (stable in long-term memory)
- 🔄 Due for Review
- ⚠️ Struggling (failed review)

### 7. Database Schema Updates

```sql
-- Sections (CEFR levels)
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name TEXT,  -- "A1.1 - Survival Basics"
    cefr_level TEXT,  -- "A1"
    order_num INTEGER,
    xp_required INTEGER,
    word_target INTEGER
);

-- Units (Topics within sections)
CREATE TABLE units (
    id INTEGER PRIMARY KEY,
    section_id INTEGER,
    name TEXT,  -- "Greetings & Introductions"
    order_num INTEGER,
    is_unlocked BOOLEAN DEFAULT FALSE
);

-- Lessons (Activities within units)
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY,
    unit_id INTEGER,
    type TEXT,  -- "vocabulary", "pronunciation", "conversation", "listening"
    order_num INTEGER,
    is_completed BOOLEAN DEFAULT FALSE
);

-- User Progress
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY,
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    current_section_id INTEGER DEFAULT 1,
    current_unit_id INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_practice_date DATE,
    words_learned INTEGER DEFAULT 0,
    words_mastered INTEGER DEFAULT 0
);

-- Vocabulary with unit association
ALTER TABLE vocabulary ADD COLUMN unit_id INTEGER;
ALTER TABLE vocabulary ADD COLUMN cefr_level TEXT;

-- Enhanced progress tracking
ALTER TABLE vocabulary_progress ADD COLUMN times_correct INTEGER DEFAULT 0;
ALTER TABLE vocabulary_progress ADD COLUMN times_incorrect INTEGER DEFAULT 0;
ALTER TABLE vocabulary_progress ADD COLUMN status TEXT DEFAULT 'new';
-- status: 'new', 'learning', 'learned', 'due', 'struggling'
```

---

## Implementation Phases

### Phase 1: Content Expansion (Priority: HIGH)
- Expand vocabulary from 35 to 500+ words
- Organize into A1.1 and A1.2 units
- Add more phrases per topic
- Tag all content with CEFR level and unit

### Phase 2: Progress System (Priority: HIGH)
- Fix spaced repetition algorithm
- Add XP scoring
- Track words learned vs mastered
- Show accurate statistics

### Phase 3: Learning Path UI (Priority: MEDIUM)
- Visual path showing sections/units
- Locked/unlocked states
- Progress indicators per unit
- Current position marker

### Phase 4: AI Coach (Priority: MEDIUM)
- Daily recommendations
- Weekly progress reports
- Adaptive difficulty
- Celebration of milestones

### Phase 5: Gamification (Priority: LOW)
- Streak tracking with rewards
- Badges/achievements
- Level-up animations
- Leaderboard (optional)

---

## Immediate Fixes Needed

1. **Vocabulary not resetting properly** - Words marked "done" should come back for review
2. **Need more content** - 35 words is not enough for any CEFR level
3. **Progress display** - Show actual words learned/mastered count
4. **Review queue** - Show how many words due today

---

## Sources

- [Duolingo Learning Path](https://duoplanet.com/duolingo-learning-path/)
- [CEFR Vocabulary Research](https://universeofmemory.com/how-many-words-you-should-know/)
- [Spaced Repetition Guide](https://www.heylama.com/blog/spaced-repetition)
- [Spanish A1 Syllabus](https://iifls.com/spanish-a1-syllabus/)
- [AI in Language Learning 2025](https://www.mdpi.com/2673-4591/107/1/7)
