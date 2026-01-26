# Changelog

All notable changes to HablaConmigo Spanish Learning App.

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
