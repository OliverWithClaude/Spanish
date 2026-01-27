# Implementation Plan - Remaining Features

This document outlines the remaining features to be implemented in HablaConmigo, prioritized by value and effort.

## Completed Features ✅

- [x] **Word Forms Generation** (P0) - Vocabulary multiplication effect (3-5x)
- [x] **Grammar Pattern Detection** (P1) - SpaCy-based tense/structure detection
- [x] **Content Discovery** - Import from YouTube, websites, PDFs
- [x] **Kwiziq Grammar Tracking** - Manual progress tracking for 43 topics
- [x] **DELE Exam Tracker** - A1/A2 readiness assessment
- [x] **Enhanced Spaced Repetition** - SM-2 algorithm with 4+ recall requirement
- [x] **Help Me Remember** - Images + memorable sentences for vocabulary

## Priority 1: Essential Features

### 1. Automated Kwiziq Sync (P1)
**Estimated Effort:** 5-7 days
**Status:** Not started

**Goal:** Automatically sync grammar progress from Kwiziq.com instead of manual entry.

**Implementation:**
1. **Browser Extension or Scraper:**
   - Create a Chrome extension or Puppeteer script to extract brain map data
   - Parse Kwiziq's progress page to get topic completion %
   - Map Kwiziq topic IDs to our database IDs

2. **Import Functionality:**
   - Add "Import from Kwiziq" button in Progress tab
   - Parse JSON/HTML export from Kwiziq
   - Map completion % to our status levels:
     - 0-25% → new
     - 26-60% → learning
     - 61-90% → learned
     - 91-100% → mastered

3. **Sync Mechanism:**
   - Option to sync automatically on app startup
   - Store last sync timestamp
   - Show "Sync now" button with last sync time

**Technical Challenges:**
- Kwiziq doesn't have a public API
- May need to use browser automation (Selenium/Puppeteer)
- Mapping Kwiziq topics to our taxonomy
- Handling authentication/cookies

**Value:** High - eliminates manual data entry, keeps progress accurate

**Files to Create/Modify:**
- `src/kwiziq_sync.py` - Core sync logic
- `sync_kwiziq.py` - Standalone script for testing
- `app.py` - Add UI controls in Progress tab
- `KWIZIQ_MAPPING.json` - Topic ID mapping

**Alternative Approach (Easier):**
- Provide a bookmarklet that captures Kwiziq brain map HTML
- Parse locally without scraping
- Lower effort but requires manual trigger

---

## Priority 2: Quality of Life Improvements

### 2. Grammar Exercise Generator (P2)
**Estimated Effort:** 3-4 days
**Status:** Not started

**Goal:** Generate practice exercises for specific grammar topics.

**Implementation:**
1. **Exercise Types:**
   - Fill in the blank (verb conjugations)
   - Multiple choice (correct tense)
   - Sentence transformation (present → past)
   - Error correction

2. **Generation Logic:**
   - Select target grammar topic from user's "learning" list
   - Use LLM to generate exercises with known vocabulary
   - Store exercises with correct answers
   - Track user's accuracy per topic

3. **UI Integration:**
   - New "Grammar Practice" tab
   - Select topic from dropdown
   - Generate 10 exercises
   - Show immediate feedback
   - Update grammar_progress.practice_count

4. **Smart Difficulty:**
   - Use only vocabulary the user knows
   - Start with simple sentences
   - Increase complexity as accuracy improves

**Value:** Medium-High - fills gap between passive learning and active practice

**Files to Create/Modify:**
- `src/grammar_exercises.py` - Exercise generation
- `app.py` - Add Grammar Practice tab
- `src/database.py` - Add `grammar_exercises` table

---

### 3. Historical Progress Tracking (P2)
**Estimated Effort:** 2 days
**Status:** Not started

**Goal:** Visualize progress over time with charts and graphs.

**Implementation:**
1. **Data to Track:**
   - Daily XP gained
   - Vocabulary progress (new/learning/learned counts)
   - Grammar topics mastered
   - Speaking practice sessions
   - Streak history

2. **Visualization:**
   - Line chart: XP over time
   - Stacked area chart: Vocabulary status breakdown
   - Bar chart: Daily activity (words reviewed, phrases practiced)
   - Heatmap: Practice consistency calendar

3. **Time Ranges:**
   - Last 7 days
   - Last 30 days
   - Last 90 days
   - All time

4. **Technical Stack:**
   - Use Plotly for interactive charts
   - Add charts to Progress tab
   - Query historical data from existing tables

**Value:** Medium - motivates users, shows progress trends

**Files to Create/Modify:**
- `src/progress_charts.py` - Chart generation
- `app.py` - Add charts to Progress tab
- May need to add `daily_stats` table for aggregated data

---

## Priority 3: Advanced Features

### 4. Content Recommendation Engine (P3)
**Estimated Effort:** 3-4 days
**Status:** Not started

**Goal:** Suggest YouTube videos, articles, and podcasts matched to user level.

**Implementation:**
1. **Recommendation Algorithm:**
   - Calculate user's comprehensive level (vocab + grammar)
   - Query content sources with appropriate difficulty
   - Filter by interest tags (if user preferences stored)

2. **Content Sources:**
   - Dreaming Spanish videos (API or scraping)
   - Small Town Spanish Teacher stories
   - News in Slow Spanish
   - Spanish podcasts

3. **Matching Logic:**
   - Estimate content difficulty:
     - Count unique words
     - Detect grammar patterns
     - Use frequency data
   - Compare with user's vocabulary coverage
   - Recommend content with 70-85% comprehension

4. **UI Integration:**
   - Add "Recommended for You" section in Links tab
   - Show 5-10 recommendations
   - Display estimated comprehension %
   - "Import to Discover" button

**Value:** Medium - helps users find level-appropriate content

**Files to Create/Modify:**
- `src/content_recommendations.py` - Recommendation engine
- `src/content_sources.py` - Scrapers for content sources
- `app.py` - Add recommendations section

---

### 5. Advanced Word Forms (P3)
**Estimated Effort:** 2-3 days
**Status:** Not started

**Goal:** Enhance word forms generation with:
- Irregular verb conjugations (ser, ir, estar, tener, etc.)
- Compound tenses (present perfect, pluperfect)
- Progressive forms (estoy hablando)
- Diminutives/augmentatives (-ito, -ísimo)

**Implementation:**
1. **Irregular Verb Database:**
   - Create `irregular_verbs.json` with common patterns
   - Store irregular forms manually for top 50 verbs
   - Use as fallback before LLM generation

2. **Compound Tenses:**
   - Detect auxiliary verb knowledge (haber, estar)
   - Generate "he hablado", "estaba comiendo", etc.
   - Combine auxiliary + participle

3. **Validation:**
   - Cross-check generated forms with frequency data
   - Flag suspicious forms for manual review
   - Store confidence scores

**Value:** Low-Medium - incremental improvement, but most value already achieved

**Files to Create/Modify:**
- `src/word_forms.py` - Enhance generation logic
- `irregular_verbs.json` - Irregular verb data
- `src/database.py` - Add confidence score field

---

## Priority 4: Experimental Features

### 6. Conversation Scenarios (P4)
**Estimated Effort:** 2-3 days
**Status:** Not started

**Goal:** Pre-scripted conversation scenarios for specific situations.

**Implementation:**
- Define scenarios: ordering food, booking hotel, asking directions
- Multi-turn conversations with branching paths
- Record user's responses
- AI evaluation of appropriateness

**Value:** Low - niche feature, Conversation tab already provides freeform practice

---

### 7. Pronunciation Analytics (P4)
**Estimated Effort:** 3-4 days
**Status:** Not started

**Goal:** Track pronunciation accuracy over time per phoneme.

**Implementation:**
- Store phoneme-level transcription from Whisper
- Track accuracy per sound (r/rr, b/v, etc.)
- Identify weak areas
- Generate targeted practice phrases

**Value:** Low-Medium - interesting but complex, requires phoneme alignment

---

## Implementation Order Recommendation

### Next 2 Weeks (High Priority)
1. **Automated Kwiziq Sync** (P1) - High value, eliminates manual work
   - Start with bookmarklet approach (easier)
   - Upgrade to full automation later if needed

### Following 2 Weeks (Quality of Life)
2. **Grammar Exercise Generator** (P2) - Complements grammar tracking
3. **Historical Progress Tracking** (P2) - Motivational, relatively easy

### Future Considerations (Lower Priority)
4. **Content Recommendation Engine** (P3) - Nice to have
5. **Advanced Word Forms** (P3) - Diminishing returns
6. **Experimental Features** (P4) - Only if time permits

---

## Technical Debt & Refactoring

### Areas for Improvement:
1. **Test Coverage:**
   - Add unit tests for core functions
   - Create integration tests for UI flows
   - Add CI/CD pipeline

2. **Error Handling:**
   - Improve error messages in UI
   - Add retry logic for Ollama failures
   - Log errors to file for debugging

3. **Performance:**
   - Cache frequent database queries
   - Optimize word forms matching (set operations)
   - Lazy-load SpaCy model

4. **Code Organization:**
   - Split `app.py` into smaller modules (tabs/)
   - Create `src/utils.py` for shared helpers
   - Add type hints throughout

---

## Estimated Timeline

- **P1 Features:** 1-2 weeks
- **P2 Features:** 2-3 weeks
- **P3 Features:** 1-2 weeks
- **Total:** ~4-7 weeks for all planned features

## Next Steps

1. Review this plan with stakeholders
2. Prioritize based on user feedback
3. Start with Automated Kwiziq Sync (highest value)
4. Iterate based on user testing

---

**Last Updated:** 2026-01-27
