# Changelog

All notable changes to HablaConmigo Spanish Learning App.

## [2026-01-26] - Enhanced CEFR Scoring System

### Added

**Unified Multi-Dimensional CEFR Proficiency Score**
- Complete proficiency scoring system combining 4 dimensions with weighted contributions
- Overall CEFR level display: "You are A2 (A2.1) at 33.5%"
- Dimension breakdown showing scores for vocabulary, grammar, speaking, and content
- Visual dashboard in Progress tab with progress bars and statistics
- Level gating system requiring 80% mastery before unlocking next level

**Scoring Dimensions**:
- **Vocabulary (30% weight)**: Based on SM-2 spaced repetition progress
  - Learned/Due: 1.0x, Learning: 0.5x, Struggling: 0.25x, New: 0.0x
- **Grammar (35% weight)**: Based on grammar topics tracked
  - Mastered: 1.0x, Learned: 0.7x, Learning: 0.3x, New: 0.0x
- **Speaking (20% weight)**: Based on recent 50 pronunciation attempts
  - Average accuracy percentage with stricter thresholds
- **Content (15% weight)**: Based on content packages mastered
  - Mastered (80%+ words known): 1.0x, Partial (40-80%): 0.5x

**Backend Functions** (added to `src/database.py`):
- `calculate_vocabulary_score()` - Vocabulary proficiency (0-100%)
- `calculate_grammar_score()` - Grammar proficiency (0-100%)
- `calculate_speaking_score()` - Speaking proficiency (0-100%)
- `calculate_content_score()` - Content mastery (0-100%)
- `calculate_unified_cefr_score()` - Overall unified proficiency score
- `check_level_gating()` - Check A2/B1 unlock requirements

**UI Components** (added to Progress tab):
- Unified proficiency score display (overall CEFR level + percentage)
- Four dimension cards showing individual scores and statistics
- Level unlocking accordion showing gating requirements
- Refresh button to update all scores
- Auto-load on tab open

**CEFR Level Mapping**:
- A1: 0-25% (sublevels: A1.1, A1.2)
- A2: 25-50% (sublevels: A2.1, A2.2)
- B1: 50-70% (sublevels: B1.1, B1.2)
- B2: 70-85% (sublevels: B2.1, B2.2)
- C1: 85-95% (sublevels: C1.1, C1.2)
- C2: 95-100%

**Level Gating Requirements**:
- A2 unlock: 80% of A1 vocabulary + 80% of A1 grammar
- B1 unlock: 80% of A2 vocabulary + 80% of A2 grammar
- Purpose: Ensures solid foundation before advancing

**Documentation**:
- `PHASE_5_COMPLETE.md` - Complete implementation guide with formulas
- `test_unified_cefr.py` - Test suite showing scoring calculations

### Benefits

**User Benefits**:
1. Clear answer to "What's my Spanish level?"
2. Visibility into strengths and weaknesses across dimensions
3. Motivation with clear path to next level
4. Balanced progress tracking (not just vocabulary)

**Strategic Benefits**:
1. Prevents knowledge gaps through gating requirements
2. Multi-dimensional assessment (aligns with real CEFR exams)
3. Actionable feedback on what to improve
4. Proper weighting (grammar 35%, vocabulary 30%, speaking 20%, content 15%)

### Example Output

```
Overall: A2 (A2.1) - 33.5%

Dimensions:
- Vocabulary: 65.5% (B1) - 553 learned, 158 learning
- Grammar: 4.7% (A1) - 1 mastered, 1 learned, 1 learning
- Speaking: 45.9% (A2) - 216 attempts, 45.9% avg
- Content: 20.0% (A1) - 0 mastered packages

Gating:
- A1: Unlocked (Vocab: 77.3%, Grammar: 9.5%)
- A2: Locked - Need 80% A1 grammar (currently 9.5%)
- B1: Locked - Need 80% A2 vocab + grammar
```

### Files Modified
- `src/database.py` - Added 6 proficiency scoring functions
- `app.py` - Added unified score UI section to Progress tab
- `CHANGELOG.md` - Updated with Phase 5 changes

### Files Created
- `test_unified_cefr.py` - Test suite for unified scoring
- `PHASE_5_COMPLETE.md` - Complete documentation

### Testing
- All scoring functions tested and verified
- UI displays correctly with real user data
- Gating logic working as expected
- Formula validated: (vocab×0.30 + grammar×0.35 + speaking×0.20 + content×0.15)

---

## [2026-01-26] - Grammar Progress Tracking

### Added

**Grammar Progress Tracking System**
- Complete grammar taxonomy with 43 topics across A1-B1 CEFR levels
- Grammar progress tracking in Progress tab aligned with Kwiziq brain map
- 4-level status system: new → learning → learned → mastered
- Progress summary with breakdown by CEFR level and category
- Topic filtering by CEFR level (A1, A2, B1)
- Prerequisite dependency tracking (47 dependencies mapped)
- Database schema for grammar tracking (`grammar_topics`, `grammar_user_progress`, etc.)
- Setup script (`setup_grammar_database.py`) to initialize grammar database
- Test suite (`test_grammar_ui.py`) for grammar progress functions
- Backend functions in `src/database.py`:
  - `get_grammar_topics()` - Retrieve grammar topics with filtering
  - `get_user_grammar_progress()` - Get user's progress on topics
  - `update_grammar_progress()` - Update mastery status
  - `get_grammar_progress_summary()` - Statistics by level and category
  - `get_grammar_topics_with_progress()` - Topics merged with user progress

**Documentation**
- `PHASE_3_COMPLETE.md` - Complete implementation guide
- `SPANISH_GRAMMAR_TAXONOMY.json` - Grammar taxonomy with dependencies
- `IMPLEMENTATION_SCHEMA.sql` - Database schema
- `GRAMMAR_DEPENDENCY_GRAPH.md` - Visual dependency maps
- `MORPHOLOGICAL_RULES.md` - Word transformation patterns
- Updated `CLAUDE.md` with grammar tracking features

**Word Forms Generation (Partial)**
- `generate_word_forms.py` - LLM-based conjugation/declension engine
- Successfully tested with adjectives (8x multiplier verified)
- Verb matching to grammar rules implemented
- Full vocabulary generation deferred for future optimization

### Fixed

**Content Analysis**
- Fixed LLM word analysis prompt to require base/infinitive forms for English translations
- Added explicit rules: "For verbs: use 'to [verb]'" (not conjugated forms like "they maintain")
- Corrected existing vocabulary entries:
  - `mantener`: "they maintain" → "to maintain"
  - `acabar`: "I finish" → "to finish"
- Added examples showing correct infinitive format to prevent future issues

**UI**
- Fixed Gradio deprecation warning: `col_count` → `column_count` in Dataframe component

### Technical Details

**Database Changes**
- 7 new grammar-related tables created
- 43 grammar topics imported with prerequisite relationships
- Proficiency scoring: 0% (new) → 30% (learning) → 70% (learned) → 100% (mastered)

**Architecture**
- Grammar progress integrated into existing Progress tab
- Real-time updates with automatic refresh after status changes
- Filterable topics table with status indicators (✅ 📝 📖 ⭕)

### Files Modified
- `src/database.py` - Added 6 grammar progress functions
- `app.py` - Added Grammar Progress UI section to Progress tab
- `src/llm.py` - Fixed word_analysis prompt for base form translations

### Files Created
- `setup_grammar_database.py` - Database initialization script
- `generate_word_forms.py` - Word forms generation engine
- `test_grammar_ui.py` - Test suite
- `PHASE_3_COMPLETE.md` - Implementation documentation
- `SPANISH_GRAMMAR_TAXONOMY.json` - Complete taxonomy
- `IMPLEMENTATION_SCHEMA.sql` - Database schema
- `GRAMMAR_DEPENDENCY_GRAPH.md` - Dependency visualization
- `MORPHOLOGICAL_RULES.md` - Transformation patterns
- `CHANGELOG.md` - This file

### Testing
- All grammar progress functions tested and verified
- Status updates working correctly
- Progress summaries calculating accurately
- Topic filtering functioning properly

### Known Limitations
- Grammar taxonomy contains 43 topics (sample set from full 248-topic research)
- Word forms generation not yet run on full vocabulary (970 words)
- Manual status updates required (no automatic detection from Kwiziq yet)

### Future Enhancements
- Automated word forms generation for all 970 vocabulary words
- Grammar pattern detection in imported content
- Unified multi-dimensional CEFR scoring (vocabulary + grammar + speaking + content)
- Grammar practice exercises generation
- Kwiziq browser extension for automated progress sync
- Spaced repetition for grammar topics

---

## [Previous Changes]

See git history for changes prior to 2026-01-26.
