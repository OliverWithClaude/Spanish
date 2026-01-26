-- ============================================================================
-- Spanish Grammar Tracking Schema for HablaConmigo
-- ============================================================================
-- Purpose: Implement grammar taxonomy with dependency tracking, morphological
--          rules, user progress (SM-2), and word forms generation
-- Version: 1.0
-- Date: 2026-01-25
-- ============================================================================

-- ============================================================================
-- 1. GRAMMAR TOPICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS grammar_topics (
    id TEXT PRIMARY KEY,  -- e.g., 'A1_V_001', 'B1_V_050'
    title TEXT NOT NULL,  -- e.g., 'Regular -ar verbs (present)'
    cefr_level TEXT NOT NULL CHECK(cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    cefr_sublevel TEXT,  -- e.g., 'A1.1', 'A1.2'
    category TEXT NOT NULL CHECK(category IN (
        'verbs', 'nouns', 'adjectives', 'articles', 'pronouns',
        'adverbs', 'prepositions', 'conjunctions', 'idioms', 'syntax'
    )),
    subcategory TEXT,  -- e.g., 'present_tense', 'past_tenses', 'subjunctive'

    -- Morphological information
    morphological_rule TEXT,  -- Human-readable transformation rule
    applies_to_pos TEXT,  -- Comma-separated: 'verb_ar,verb_er' or 'adjective'
    multiplier INTEGER DEFAULT 1,  -- How many forms does this generate? (e.g., 6 for verb conjugation)

    -- Metadata
    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
    frequency TEXT CHECK(frequency IN ('very_high', 'high', 'medium', 'low')),
    high_priority BOOLEAN DEFAULT 0,  -- High-frequency irregular verbs, etc.

    -- Description and examples
    description TEXT,  -- Longer explanation
    examples_json TEXT,  -- JSON with examples: {"hablar": ["hablo", "hablas", ...]}
    usage_contexts_json TEXT,  -- JSON with usage contexts
    notes TEXT,  -- Teaching notes, acquisition research findings

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_grammar_topics_cefr ON grammar_topics(cefr_level);
CREATE INDEX idx_grammar_topics_category ON grammar_topics(category);
CREATE INDEX idx_grammar_topics_frequency ON grammar_topics(frequency);
CREATE INDEX idx_grammar_topics_priority ON grammar_topics(high_priority);

-- ============================================================================
-- 2. GRAMMAR DEPENDENCIES (Prerequisite Graph)
-- ============================================================================

CREATE TABLE IF NOT EXISTS grammar_dependencies (
    topic_id TEXT NOT NULL,
    prerequisite_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'required' CHECK(dependency_type IN ('required', 'recommended', 'related')),

    -- Metadata
    rationale TEXT,  -- Why is this a prerequisite?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (topic_id, prerequisite_id),
    FOREIGN KEY (topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES grammar_topics(id) ON DELETE CASCADE,

    -- Prevent self-dependency
    CHECK (topic_id != prerequisite_id)
);

-- Indexes
CREATE INDEX idx_grammar_deps_topic ON grammar_dependencies(topic_id);
CREATE INDEX idx_grammar_deps_prereq ON grammar_dependencies(prerequisite_id);
CREATE INDEX idx_grammar_deps_type ON grammar_dependencies(dependency_type);

-- ============================================================================
-- 3. MORPHOLOGICAL TRANSFORMATION RULES
-- ============================================================================

CREATE TABLE IF NOT EXISTS morphology_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grammar_topic_id TEXT NOT NULL,

    -- Rule identification
    rule_name TEXT NOT NULL,  -- e.g., 'present_ar_conjugation', 'noun_plural_vowel'
    rule_type TEXT NOT NULL CHECK(rule_type IN (
        'verb_conjugation', 'noun_plural', 'adjective_agreement',
        'diminutive', 'superlative', 'participle', 'gerund'
    )),

    -- Transformation details
    input_pattern TEXT,  -- Regex or pattern to match (e.g., '.*ar$')
    output_template TEXT,  -- Template for transformation (e.g., '{stem}o', '{stem}as')
    person TEXT,  -- For verbs: '1s', '2s', '3s', '1p', '2p', '3p'
    gender TEXT,  -- For nouns/adjectives: 'masculine', 'feminine', 'neutral'
    number TEXT,  -- 'singular', 'plural'

    -- Conditions
    applies_to_words TEXT,  -- JSON list of specific words (for irregulars)
    exceptions TEXT,  -- JSON list of words that DON'T follow this rule

    -- Implementation
    python_function TEXT,  -- Optional: Python function name for complex rules

    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_morphology_topic ON morphology_rules(grammar_topic_id);
CREATE INDEX idx_morphology_type ON morphology_rules(rule_type);

-- ============================================================================
-- 4. USER GRAMMAR PROGRESS (SM-2 Spaced Repetition)
-- ============================================================================

CREATE TABLE IF NOT EXISTS grammar_user_progress (
    user_id INTEGER NOT NULL DEFAULT 1,  -- For now, single user
    grammar_topic_id TEXT NOT NULL,

    -- SM-2 spaced repetition fields
    status TEXT DEFAULT 'new' CHECK(status IN ('new', 'learning', 'learned', 'mastered')),
    easiness_factor REAL DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    last_reviewed DATE,
    next_review DATE,

    -- Usage tracking
    times_encountered INTEGER DEFAULT 0,  -- How many times seen in content/practice
    times_practiced INTEGER DEFAULT 0,  -- How many times explicitly practiced
    times_correct INTEGER DEFAULT 0,
    times_incorrect INTEGER DEFAULT 0,

    -- Proficiency scoring
    proficiency_score REAL DEFAULT 0.0 CHECK(proficiency_score >= 0 AND proficiency_score <= 100),

    -- Timestamps
    first_encountered TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, grammar_topic_id),
    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX idx_grammar_progress_user ON grammar_user_progress(user_id);
CREATE INDEX idx_grammar_progress_status ON grammar_user_progress(user_id, status);
CREATE INDEX idx_grammar_progress_next_review ON grammar_user_progress(user_id, next_review);
CREATE INDEX idx_grammar_progress_proficiency ON grammar_user_progress(user_id, proficiency_score);

-- ============================================================================
-- 5. GRAMMAR COVERAGE (Lightweight Tracking)
-- ============================================================================
-- Track which grammar topics user has encountered (separate from mastery)

CREATE TABLE IF NOT EXISTS grammar_coverage (
    user_id INTEGER NOT NULL DEFAULT 1,
    grammar_topic_id TEXT NOT NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_seen INTEGER DEFAULT 1,
    source TEXT,  -- 'vocabulary', 'conversation', 'content_package', 'explicit_study'

    PRIMARY KEY (user_id, grammar_topic_id),
    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE
);

CREATE INDEX idx_grammar_coverage_user ON grammar_coverage(user_id);
CREATE INDEX idx_grammar_coverage_topic ON grammar_coverage(grammar_topic_id);

-- ============================================================================
-- 6. WORD FORMS (Generated from Vocabulary × Grammar)
-- ============================================================================
-- Links vocabulary words to their grammatical forms

CREATE TABLE IF NOT EXISTS word_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vocabulary_word_id INTEGER NOT NULL,  -- From existing vocabulary table
    grammar_topic_id TEXT NOT NULL,

    -- Form details
    form TEXT NOT NULL,  -- The actual generated form (e.g., 'hablo', 'hablas')
    person TEXT,  -- For verbs: '1s', '2s', etc.
    gender TEXT,  -- For nouns/adjectives
    number TEXT,  -- 'singular', 'plural'
    tense TEXT,  -- For verbs: 'present', 'preterite', etc.
    mood TEXT,  -- For verbs: 'indicative', 'subjunctive', 'imperative'

    -- Metadata
    is_irregular BOOLEAN DEFAULT 0,
    morphology_rule_id INTEGER,  -- Which rule generated this?

    -- Tracking
    times_recognized INTEGER DEFAULT 0,  -- How many times user recognized this form
    last_seen TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE,
    FOREIGN KEY (morphology_rule_id) REFERENCES morphology_rules(id) ON DELETE SET NULL,
    UNIQUE (vocabulary_word_id, grammar_topic_id, form)
);

-- Indexes
CREATE INDEX idx_word_forms_vocab ON word_forms(vocabulary_word_id);
CREATE INDEX idx_word_forms_grammar ON word_forms(grammar_topic_id);
CREATE INDEX idx_word_forms_form ON word_forms(form);  -- For reverse lookup

-- ============================================================================
-- 7. GRAMMAR PRACTICE LOG
-- ============================================================================
-- Track explicit grammar practice sessions

CREATE TABLE IF NOT EXISTS grammar_practice_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    grammar_topic_id TEXT NOT NULL,
    session_id INTEGER,  -- Links to practice_sessions table if exists

    -- Practice details
    practice_type TEXT CHECK(practice_type IN (
        'recognition', 'production', 'transformation', 'fill_blank', 'multiple_choice', 'conjugation'
    )),
    prompt TEXT,  -- What was the question/prompt?
    user_response TEXT,  -- What did user say/write?
    correct_answer TEXT,  -- What was the correct answer?
    is_correct BOOLEAN,

    -- Context
    source_content TEXT,  -- Where did this practice come from?
    difficulty_perceived TEXT CHECK(difficulty_perceived IN ('easy', 'medium', 'hard', 'unknown')),

    -- Timestamps
    practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_grammar_practice_user ON grammar_practice_log(user_id);
CREATE INDEX idx_grammar_practice_topic ON grammar_practice_log(grammar_topic_id);
CREATE INDEX idx_grammar_practice_date ON grammar_practice_log(practiced_at);

-- ============================================================================
-- 8. GRAMMAR EXPLANATIONS
-- ============================================================================
-- Store user-friendly explanations, tips, and examples

CREATE TABLE IF NOT EXISTS grammar_explanations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grammar_topic_id TEXT NOT NULL,

    -- Content
    explanation_es TEXT,  -- Explanation in Spanish
    explanation_en TEXT,  -- Explanation in English
    when_to_use TEXT,  -- Usage guidelines
    common_mistakes TEXT,  -- Common errors to avoid

    -- Examples
    examples_json TEXT,  -- JSON array of example sentences with translations

    -- Media
    diagram_url TEXT,  -- Link to visual diagram (for dependency trees, etc.)
    video_url TEXT,  -- Link to explanation video

    -- Metadata
    target_level TEXT,  -- 'beginner', 'intermediate', 'advanced'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (grammar_topic_id) REFERENCES grammar_topics(id) ON DELETE CASCADE
);

-- ============================================================================
-- 9. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Grammar topics ready to learn (prerequisites met)
CREATE VIEW IF NOT EXISTS grammar_unlockable AS
SELECT
    gt.id,
    gt.title,
    gt.cefr_level,
    gt.category,
    gt.difficulty,
    gt.frequency
FROM grammar_topics gt
WHERE gt.id NOT IN (
    -- Already mastered
    SELECT grammar_topic_id
    FROM grammar_user_progress
    WHERE status IN ('learned', 'mastered')
)
AND NOT EXISTS (
    -- Has unfulfilled required prerequisites
    SELECT 1
    FROM grammar_dependencies gd
    WHERE gd.topic_id = gt.id
    AND gd.dependency_type = 'required'
    AND gd.prerequisite_id NOT IN (
        SELECT grammar_topic_id
        FROM grammar_user_progress
        WHERE status IN ('learned', 'mastered')
    )
);

-- View: Grammar topics due for review (SM-2)
CREATE VIEW IF NOT EXISTS grammar_due_for_review AS
SELECT
    gup.grammar_topic_id,
    gt.title,
    gt.cefr_level,
    gup.status,
    gup.next_review,
    gup.proficiency_score
FROM grammar_user_progress gup
JOIN grammar_topics gt ON gup.grammar_topic_id = gt.id
WHERE gup.next_review <= DATE('now')
AND gup.status IN ('learning', 'learned')
ORDER BY gup.next_review ASC, gup.proficiency_score ASC;

-- View: Grammar coverage by CEFR level
CREATE VIEW IF NOT EXISTS grammar_coverage_by_level AS
SELECT
    gt.cefr_level,
    COUNT(DISTINCT gt.id) AS total_topics,
    COUNT(DISTINCT CASE WHEN gup.status IN ('learned', 'mastered') THEN gt.id END) AS mastered_topics,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN gup.status IN ('learned', 'mastered') THEN gt.id END) / COUNT(DISTINCT gt.id), 2) AS coverage_percent
FROM grammar_topics gt
LEFT JOIN grammar_user_progress gup ON gt.id = gup.grammar_topic_id
GROUP BY gt.cefr_level
ORDER BY
    CASE gt.cefr_level
        WHEN 'A1' THEN 1
        WHEN 'A2' THEN 2
        WHEN 'B1' THEN 3
        WHEN 'B2' THEN 4
        WHEN 'C1' THEN 5
        WHEN 'C2' THEN 6
    END;

-- View: High-priority topics not yet mastered
CREATE VIEW IF NOT EXISTS grammar_high_priority_pending AS
SELECT
    gt.id,
    gt.title,
    gt.cefr_level,
    gt.category,
    gt.frequency,
    COALESCE(gup.status, 'new') AS status
FROM grammar_topics gt
LEFT JOIN grammar_user_progress gup ON gt.id = gup.grammar_topic_id
WHERE gt.high_priority = 1
AND (gup.status IS NULL OR gup.status NOT IN ('learned', 'mastered'))
ORDER BY
    CASE gt.cefr_level
        WHEN 'A1' THEN 1
        WHEN 'A2' THEN 2
        WHEN 'B1' THEN 3
    END,
    CASE gt.frequency
        WHEN 'very_high' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;

-- ============================================================================
-- 10. STORED PROCEDURES / FUNCTIONS (SQL Logic)
-- ============================================================================

-- Function to update grammar progress with SM-2 algorithm
-- (Implementation in Python; this is pseudocode)
--
-- update_grammar_progress(user_id, topic_id, quality_rating):
--     1. Retrieve current SM-2 values
--     2. Calculate new easiness_factor based on quality (0-5)
--     3. Calculate new interval and next_review date
--     4. Update proficiency_score
--     5. Update status if thresholds met
--     6. INSERT or UPDATE grammar_user_progress

-- Function to generate word forms for vocabulary word
--
-- generate_word_forms(vocab_word_id):
--     1. Get word, POS, and user's mastered grammar
--     2. Query morphology_rules WHERE applies_to_pos matches
--     3. For each rule, apply transformation
--     4. INSERT INTO word_forms
--     5. Return count of forms generated

-- Function to calculate grammar CEFR score
--
-- calculate_grammar_cefr_score(user_id, target_level):
--     1. Get all topics for target_level
--     2. Count mastered topics
--     3. Weight by topic importance (high_priority, frequency)
--     4. Return weighted percentage

-- ============================================================================
-- 11. SAMPLE DATA INSERTION
-- ============================================================================

-- Insert sample grammar topics (from taxonomy JSON)
INSERT INTO grammar_topics (id, title, cefr_level, cefr_sublevel, category, subcategory, morphological_rule, applies_to_pos, multiplier, difficulty, frequency, high_priority, examples_json) VALUES
    ('A1_V_001', 'Regular -ar verbs (present)', 'A1', 'A1.1', 'verbs', 'present_tense', 'Remove -ar, add: -o, -as, -a, -amos, -áis, -an', 'verb_ar', 6, 'easy', 'very_high', 0, '{"hablar": ["hablo", "hablas", "habla", "hablamos", "habláis", "hablan"]}'),
    ('A1_V_002', 'Regular -er verbs (present)', 'A1', 'A1.1', 'verbs', 'present_tense', 'Remove -er, add: -o, -es, -e, -emos, -éis, -en', 'verb_er', 6, 'easy', 'very_high', 0, '{"comer": ["como", "comes", "come", "comemos", "coméis", "comen"]}'),
    ('A1_V_010', 'Irregular verb: ser (present)', 'A1', 'A1.1', 'verbs', 'present_tense', 'Completely irregular - must memorize', 'verb_ser', 6, 'medium', 'very_high', 1, '{"ser": ["soy", "eres", "es", "somos", "sois", "son"]}'),
    ('A1_N_001', 'Noun gender (masculine/feminine)', 'A1', 'A1.1', 'nouns', 'gender', 'Recognize -o (masculine), -a (feminine) patterns', 'noun', 1, 'medium', 'very_high', 0, NULL),
    ('A1_N_002', 'Noun plurals', 'A1', 'A1.1', 'nouns', 'number', 'Vowel+s, Consonant+es, z→ces', 'noun', 2, 'easy', 'very_high', 0, '{"libro": ["libro", "libros"], "profesor": ["profesor", "profesores"]}'),
    ('B1_V_050', 'Present subjunctive - regular verbs', 'B1', 'B1.1', 'verbs', 'subjunctive', 'Take yo-form of present indicative, drop -o, add opposite endings', 'verb_ar,verb_er,verb_ir', 6, 'hard', 'very_high', 0, '{"hablar": ["hable", "hables", "hable", "hablemos", "habléis", "hablen"]}');

-- Insert sample dependencies
INSERT INTO grammar_dependencies (topic_id, prerequisite_id, dependency_type, rationale) VALUES
    ('A1_N_002', 'A1_N_001', 'required', 'Must understand gender before plurals (to maintain gender in plural forms)'),
    ('B1_V_050', 'A1_V_001', 'required', 'Subjunctive formation uses present indicative yo-form as stem'),
    ('B1_V_050', 'A1_V_002', 'required', 'Subjunctive formation uses present indicative yo-form as stem'),
    ('B1_V_050', 'A1_V_010', 'recommended', 'Ser has irregular subjunctive; knowing present helps');

-- Insert sample morphology rules
INSERT INTO morphology_rules (grammar_topic_id, rule_name, rule_type, input_pattern, output_template, person, gender, number) VALUES
    ('A1_V_001', 'present_ar_1s', 'verb_conjugation', '.*ar$', '{stem}o', '1s', NULL, 'singular'),
    ('A1_V_001', 'present_ar_2s', 'verb_conjugation', '.*ar$', '{stem}as', '2s', NULL, 'singular'),
    ('A1_V_001', 'present_ar_3s', 'verb_conjugation', '.*ar$', '{stem}a', '3s', NULL, 'singular'),
    ('A1_V_001', 'present_ar_1p', 'verb_conjugation', '.*ar$', '{stem}amos', '1p', NULL, 'plural'),
    ('A1_V_001', 'present_ar_2p', 'verb_conjugation', '.*ar$', '{stem}áis', '2p', NULL, 'plural'),
    ('A1_V_001', 'present_ar_3p', 'verb_conjugation', '.*ar$', '{stem}an', '3p', NULL, 'plural'),
    ('A1_N_002', 'noun_plural_vowel', 'noun_plural', '[aeiou]$', '{word}s', NULL, NULL, 'plural'),
    ('A1_N_002', 'noun_plural_consonant', 'noun_plural', '[^aeiou]$', '{word}es', NULL, NULL, 'plural');

-- ============================================================================
-- 12. TRIGGERS
-- ============================================================================

-- Trigger: Update updated_at timestamp on grammar_user_progress
CREATE TRIGGER IF NOT EXISTS update_grammar_progress_timestamp
AFTER UPDATE ON grammar_user_progress
BEGIN
    UPDATE grammar_user_progress
    SET updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id AND grammar_topic_id = NEW.grammar_topic_id;
END;

-- Trigger: Prevent circular dependencies
-- (Complex; requires recursive CTE; implement in application layer)

-- ============================================================================
-- IMPLEMENTATION NOTES
-- ============================================================================
/*
 * 1. INITIAL DATA POPULATION
 *    - Import all 248 topics from SPANISH_GRAMMAR_TAXONOMY.json
 *    - Import dependencies from dependency graph
 *    - Import morphology rules from MORPHOLOGICAL_RULES.md
 *
 * 2. INTEGRATION WITH EXISTING TABLES
 *    - Add grammar_topic_id to vocabulary table (optional FK)
 *    - Add grammar_topics_detected to content_packages table (JSON)
 *    - Link pronunciation_attempts to grammar topics for verb practice
 *
 * 3. SM-2 ALGORITHM IMPLEMENTATION
 *    - Implement in src/database.py similar to vocabulary_progress
 *    - Quality ratings: 5 (perfect) → 0 (total blackout)
 *    - Update interval, easiness_factor, next_review date
 *
 * 4. WORD FORMS GENERATION
 *    - Run batch job to generate forms for all existing vocabulary
 *    - Generate forms when new vocabulary is added
 *    - Update when user masters new grammar topic (unlock new forms)
 *
 * 5. GRAMMAR COVERAGE TRACKING
 *    - Auto-detect grammar in conversation responses
 *    - Auto-detect grammar in imported content
 *    - Update grammar_coverage table
 *
 * 6. CEFR SCORING
 *    - Combine vocabulary_score (40%) + grammar_score (60%)
 *    - Grammar score = weighted average of topic mastery by level
 *    - Gating: Can't reach B1 without subjunctive mastery
 *
 * 7. UI INTEGRATION
 *    - New tab: "Grammar" with dependency tree visualization
 *    - Content analysis shows required grammar alongside vocabulary
 *    - Progress dashboard shows grammar coverage %
 *    - Unlock notifications when prerequisites met
 */

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
