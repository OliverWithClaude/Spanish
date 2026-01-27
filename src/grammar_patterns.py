"""
Grammar Pattern Detection Module

Detects verb tenses and grammar structures in Spanish text using SpaCy.
Compares detected patterns against user's grammar knowledge to assess readiness.
"""

import spacy
from typing import Dict, List, Set
from collections import Counter

# Load Spanish model (lazy loading)
_nlp = None

def get_nlp():
    """Lazy load SpaCy Spanish model"""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("es_core_news_sm")
    return _nlp


def detect_verb_tenses(text: str) -> Dict[str, int]:
    """
    Detect verb tenses in Spanish text using SpaCy morphological analysis.

    Args:
        text: Spanish text to analyze

    Returns:
        Dict with tense names and their occurrence counts
    """
    nlp = get_nlp()
    doc = nlp(text)

    tense_counts = Counter()

    for token in doc:
        if token.pos_ == "VERB" or token.pos_ == "AUX":
            # Extract morphological features
            morph = str(token.morph)

            # Detect tenses based on morphological features
            if "Tense=Pres" in morph:
                if "Mood=Sub" in morph:
                    tense_counts['present_subjunctive'] += 1
                elif "Mood=Imp" in morph:
                    tense_counts['imperative'] += 1
                else:
                    tense_counts['present'] += 1

            elif "Tense=Past" in morph:
                # Past tense could be preterite or imperfect
                # Check for imperfect indicators
                if "VerbForm=Fin" in morph and token.text.endswith(('aba', 'ía', 'aban', 'ían')):
                    tense_counts['imperfect'] += 1
                else:
                    tense_counts['preterite'] += 1

            elif "Tense=Fut" in morph:
                tense_counts['future'] += 1

            elif "Mood=Cnd" in morph:
                tense_counts['conditional'] += 1

            elif "Tense=Imp" in morph:
                tense_counts['imperfect'] += 1

    return dict(tense_counts)


def detect_grammar_structures(text: str) -> Dict[str, int]:
    """
    Detect various grammar structures beyond verb tenses.

    Args:
        text: Spanish text to analyze

    Returns:
        Dict with structure names and occurrence counts
    """
    nlp = get_nlp()
    doc = nlp(text)

    structures = Counter()

    for token in doc:
        # Detect reflexive verbs (me, te, se, nos, os, se)
        if token.text.lower() in ['me', 'te', 'se', 'nos', 'os'] and token.dep_ == 'expl':
            structures['reflexive_verbs'] += 1

        # Detect object pronouns (lo, la, le, los, las, les)
        if token.text.lower() in ['lo', 'la', 'le', 'los', 'las', 'les'] and token.pos_ == 'PRON':
            structures['object_pronouns'] += 1

        # Detect passive constructions (ser + past participle)
        if token.lemma_ == 'ser' and token.head.pos_ == 'VERB':
            structures['passive_voice'] += 1

    return dict(structures)


def analyze_grammar_patterns(text: str) -> Dict:
    """
    Comprehensive grammar pattern analysis.

    Args:
        text: Spanish text to analyze

    Returns:
        Dict with complete grammar analysis
    """
    tenses = detect_verb_tenses(text)
    structures = detect_grammar_structures(text)

    # Count total verbs
    nlp = get_nlp()
    doc = nlp(text)
    total_verbs = sum(1 for token in doc if token.pos_ in ['VERB', 'AUX'])

    return {
        'verb_tenses': tenses,
        'structures': structures,
        'total_verbs': total_verbs,
        'tenses_detected': list(tenses.keys())
    }


def get_user_grammar_knowledge() -> Set[str]:
    """
    Get set of grammar patterns user has learned.

    Returns:
        Set of grammar pattern identifiers
    """
    from src.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    # Get grammar topics user has mastered
    cursor.execute("""
        SELECT gt.title, gt.category, gup.status
        FROM grammar_topics gt
        LEFT JOIN grammar_user_progress gup ON gt.id = gup.grammar_topic_id
        WHERE gup.status IN ('learned', 'mastered')
        OR gt.cefr_level = 'A1'
    """)

    rows = cursor.fetchall()
    conn.close()

    known_patterns = set()

    # Map grammar topics to pattern identifiers
    for row in rows:
        if not row[0]:
            continue

        title = row[0].lower()
        category = (row[1] or '').lower()

        # Map to our tense identifiers
        if 'present' in title and 'subjunctive' not in title:
            known_patterns.add('present')
        if 'preterite' in title or 'pretérito' in title:
            known_patterns.add('preterite')
        if 'imperfect' in title or 'imperfecto' in title:
            known_patterns.add('imperfect')
        if 'future' in title or 'futuro' in title:
            known_patterns.add('future')
        if 'conditional' in title:
            known_patterns.add('conditional')
        if 'subjunctive' in title or 'subjuntivo' in title:
            known_patterns.add('present_subjunctive')
        if 'imperative' in title or 'imperativo' in title:
            known_patterns.add('imperative')
        if 'reflexive' in title or category == 'verbs' and 'reflexive' in category:
            known_patterns.add('reflexive_verbs')
        if 'object' in title and 'pronoun' in title:
            known_patterns.add('object_pronouns')
        if 'passive' in title:
            known_patterns.add('passive_voice')

    # Always assume A1 knowledge
    known_patterns.add('present')

    return known_patterns


def compare_grammar_with_user(text: str) -> Dict:
    """
    Compare detected grammar patterns with user's knowledge.

    Args:
        text: Spanish text to analyze

    Returns:
        Dict with matched/unmatched patterns
    """
    # Detect patterns in text
    analysis = analyze_grammar_patterns(text)
    detected_tenses = set(analysis['verb_tenses'].keys())
    detected_structures = set(analysis['structures'].keys())
    all_detected = detected_tenses | detected_structures

    # Get user's knowledge
    known_patterns = get_user_grammar_knowledge()

    # Compare
    matched_patterns = all_detected & known_patterns
    unknown_patterns = all_detected - known_patterns

    # Build detailed results
    matched_details = []
    for pattern in matched_patterns:
        count = analysis['verb_tenses'].get(pattern, 0) + analysis['structures'].get(pattern, 0)
        matched_details.append({
            'pattern': pattern,
            'display_name': _pattern_display_name(pattern),
            'count': count,
            'known': True
        })

    unknown_details = []
    for pattern in unknown_patterns:
        count = analysis['verb_tenses'].get(pattern, 0) + analysis['structures'].get(pattern, 0)
        unknown_details.append({
            'pattern': pattern,
            'display_name': _pattern_display_name(pattern),
            'count': count,
            'known': False
        })

    # Calculate grammar readiness percentage
    if all_detected:
        grammar_readiness = len(matched_patterns) / len(all_detected) * 100
    else:
        grammar_readiness = 100.0  # No grammar detected = no barrier

    return {
        'grammar_readiness': grammar_readiness,
        'matched_patterns': matched_details,
        'unknown_patterns': unknown_details,
        'total_patterns_detected': len(all_detected),
        'patterns_known': len(matched_patterns),
        'total_verbs': analysis['total_verbs']
    }


def _pattern_display_name(pattern: str) -> str:
    """Convert pattern identifier to human-readable name"""
    display_names = {
        'present': 'Present Tense',
        'preterite': 'Preterite (Past)',
        'imperfect': 'Imperfect (Past)',
        'future': 'Future Tense',
        'conditional': 'Conditional',
        'present_subjunctive': 'Present Subjunctive',
        'imperative': 'Imperative (Commands)',
        'reflexive_verbs': 'Reflexive Verbs',
        'object_pronouns': 'Object Pronouns',
        'passive_voice': 'Passive Voice'
    }
    return display_names.get(pattern, pattern.replace('_', ' ').title())


def get_grammar_recommendation(grammar_result: Dict, vocab_comprehension: float) -> str:
    """
    Generate recommendation based on grammar readiness.

    Args:
        grammar_result: Result from compare_grammar_with_user()
        vocab_comprehension: Vocabulary comprehension percentage

    Returns:
        Recommendation string
    """
    grammar_readiness = grammar_result['grammar_readiness']
    unknown_patterns = grammar_result['unknown_patterns']

    if grammar_readiness >= 90:
        if vocab_comprehension >= 80:
            return "✅ **Perfect match!** This text matches both your vocabulary and grammar knowledge."
        else:
            return "✅ Grammar matches your level, but vocabulary may be challenging."

    elif grammar_readiness >= 70:
        if vocab_comprehension >= 80:
            return "⚠️ Good vocabulary match, but some grammar patterns are new."
        else:
            return "⚠️ Moderate match. Both vocabulary and grammar are somewhat challenging."

    else:
        if unknown_patterns:
            pattern_names = [p['display_name'] for p in unknown_patterns[:3]]
            patterns_str = ', '.join(pattern_names)
            if len(unknown_patterns) > 3:
                patterns_str += f" (+{len(unknown_patterns)-3} more)"
            return f"❌ **Challenging grammar.** This text uses: {patterns_str}. Consider learning these topics first."
        else:
            return "❌ This text may be too advanced for your current grammar level."
