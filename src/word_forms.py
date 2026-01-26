"""
Word Forms Generation Module

Generates conjugated/inflected word forms from base vocabulary + grammar knowledge.
This creates the "multiplication effect": base vocabulary × grammar rules = word forms.

Example:
    - User knows verb "hablar" (1 word)
    - User knows present tense conjugation rules
    - System generates: hablo, hablas, habla, hablamos, habláis, hablan (6 words)
    - Multiplication: 1 base word → 6 recognized forms
"""

from src.llm import chat
from src.database import get_connection
from datetime import datetime
import json
import re


def generate_verb_conjugations_llm(infinitive: str, tense: str) -> list:
    """
    Generate all conjugations for a Spanish verb using LLM.

    Args:
        infinitive: Verb in infinitive form (e.g., "hablar")
        tense: Tense to conjugate (present, preterite, imperfect, future, conditional)

    Returns:
        List of dicts with person and conjugated form
    """
    prompt = f"""Generate all conjugated forms of the Spanish verb "{infinitive}" in {tense} tense.

Return ONLY valid JSON in this exact format:
{{
    "conjugations": [
        {{"person": "yo", "form": "..."}},
        {{"person": "tú", "form": "..."}},
        {{"person": "él/ella/usted", "form": "..."}},
        {{"person": "nosotros/nosotras", "form": "..."}},
        {{"person": "vosotros/vosotras", "form": "..."}},
        {{"person": "ellos/ellas/ustedes", "form": "..."}}
    ]
}}

Do not include any other text, only the JSON."""

    try:
        response = chat(prompt, mode="word_analysis", model="llama3.2:latest", temperature=0.2)

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("conjugations", [])
        else:
            print(f"WARNING: Could not extract JSON for {infinitive} ({tense})")
            return []
    except Exception as e:
        print(f"ERROR generating forms for {infinitive} ({tense}): {e}")
        return []


def generate_noun_forms_llm(noun: str) -> list:
    """
    Generate plural form for a Spanish noun using LLM.

    Args:
        noun: Noun in singular form

    Returns:
        List of dicts with form type and the form itself
    """
    prompt = f"""Generate the plural form of the Spanish noun "{noun}".

Return ONLY valid JSON:
{{
    "forms": [
        {{"type": "singular", "form": "{noun}"}},
        {{"type": "plural", "form": "..."}}
    ]
}}"""

    try:
        response = chat(prompt, mode="word_analysis", model="llama3.2:latest", temperature=0.2)

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("forms", [])
        else:
            return []
    except Exception as e:
        print(f"ERROR generating noun forms for {noun}: {e}")
        return []


def generate_adjective_forms_llm(adjective: str) -> list:
    """
    Generate all agreement forms for a Spanish adjective using LLM.

    Args:
        adjective: Adjective in base form (typically masculine singular)

    Returns:
        List of dicts with form type and the form itself
    """
    prompt = f"""Generate all gender/number agreement forms for the Spanish adjective "{adjective}".

Return ONLY valid JSON:
{{
    "forms": [
        {{"type": "masculine singular", "form": "..."}},
        {{"type": "feminine singular", "form": "..."}},
        {{"type": "masculine plural", "form": "..."}},
        {{"type": "feminine plural", "form": "..."}}
    ]
}}"""

    try:
        response = chat(prompt, mode="word_analysis", model="llama3.2:latest", temperature=0.2)

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("forms", [])
        else:
            return []
    except Exception as e:
        print(f"ERROR generating adjective forms for {adjective}: {e}")
        return []


def get_user_grammar_knowledge() -> dict:
    """
    Get user's grammar knowledge to determine which word forms to generate.

    Returns:
        Dict with grammar knowledge flags
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check which grammar topics user has mastered (learned or mastered status)
    cursor.execute("""
        SELECT gt.title, gup.status
        FROM grammar_topics gt
        LEFT JOIN grammar_user_progress gup ON gt.id = gup.grammar_topic_id
        WHERE gup.status IN ('learned', 'mastered')
        OR gt.cefr_level = 'A1'
    """)

    mastered_topics = {row[0].lower() for row in cursor.fetchall() if row[0]}
    conn.close()

    # Map grammar topics to generation flags
    # For now, assume basic A1 grammar knowledge for all users
    return {
        'present_tense': True,  # Assume A1 present tense knowledge
        'preterite_tense': any('preterite' in topic or 'pretérito' in topic for topic in mastered_topics),
        'imperfect_tense': any('imperfect' in topic for topic in mastered_topics),
        'future_tense': any('future' in topic or 'futuro' in topic for topic in mastered_topics),
        'conditional': any('conditional' in topic for topic in mastered_topics),
        'noun_plurals': True,  # Assume A1 knowledge
        'adjective_agreement': True  # Assume A1 knowledge
    }


def generate_word_forms_for_vocabulary(vocabulary_id: int, spanish_word: str, pos: str, grammar_knowledge: dict) -> list:
    """
    Generate all word forms for a vocabulary item based on user's grammar knowledge.

    Args:
        vocabulary_id: ID of base vocabulary word
        spanish_word: The Spanish word
        pos: Part of speech (verb, noun, adjective, etc.)
        grammar_knowledge: Dict of user's grammar knowledge

    Returns:
        List of word form dicts ready for database insertion
    """
    forms = []

    # Always include the base form
    forms.append({
        'base_word_id': vocabulary_id,
        'form': spanish_word,
        'form_type': 'base',
        'person': None,
        'number': None,
        'gender': None,
        'tense': None,
        'mood': None,
        'verified': 0
    })

    if pos == 'verb':
        # Generate conjugations for tenses user knows
        tenses_to_generate = []
        if grammar_knowledge.get('present_tense'):
            tenses_to_generate.append('present')
        if grammar_knowledge.get('preterite_tense'):
            tenses_to_generate.append('preterite')
        if grammar_knowledge.get('imperfect_tense'):
            tenses_to_generate.append('imperfect')
        if grammar_knowledge.get('future_tense'):
            tenses_to_generate.append('future')
        if grammar_knowledge.get('conditional'):
            tenses_to_generate.append('conditional')

        for tense in tenses_to_generate:
            conjugations = generate_verb_conjugations_llm(spanish_word, tense)
            for conj in conjugations:
                forms.append({
                    'base_word_id': vocabulary_id,
                    'form': conj.get('form', ''),
                    'form_type': 'verb_conjugation',
                    'person': conj.get('person', ''),
                    'number': None,
                    'gender': None,
                    'tense': tense,
                    'mood': 'indicative',
                    'verified': 0
                })

    elif pos == 'noun' and grammar_knowledge.get('noun_plurals'):
        # Generate plural form
        noun_forms = generate_noun_forms_llm(spanish_word)
        for nf in noun_forms:
            if nf.get('type') != 'singular':  # Skip singular (already added as base)
                forms.append({
                    'base_word_id': vocabulary_id,
                    'form': nf.get('form', ''),
                    'form_type': 'noun_plural',
                    'person': None,
                    'number': 'plural',
                    'gender': None,
                    'tense': None,
                    'mood': None,
                    'verified': 0
                })

    elif pos == 'adjective' and grammar_knowledge.get('adjective_agreement'):
        # Generate agreement forms
        adj_forms = generate_adjective_forms_llm(spanish_word)
        for af in adj_forms:
            form_type_str = af.get('type', '')
            forms.append({
                'base_word_id': vocabulary_id,
                'form': af.get('form', ''),
                'form_type': 'adjective_agreement',
                'person': None,
                'number': 'plural' if 'plural' in form_type_str else 'singular',
                'gender': 'feminine' if 'feminine' in form_type_str else 'masculine',
                'tense': None,
                'mood': None,
                'verified': 0
            })

    return forms


def save_word_forms(forms: list):
    """
    Save generated word forms to database.

    Args:
        forms: List of word form dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    for form in forms:
        # Skip if form is empty
        if not form.get('form'):
            continue

        # Check if form already exists
        cursor.execute("""
            SELECT id FROM word_forms
            WHERE base_word_id = ? AND form = ? AND form_type = ?
        """, (form['base_word_id'], form['form'], form['form_type']))

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO word_forms (
                    base_word_id, form, form_type, person, number, gender, tense, mood, verified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                form['base_word_id'],
                form['form'],
                form['form_type'],
                form['person'],
                form['number'],
                form['gender'],
                form['tense'],
                form['mood'],
                form['verified']
            ))

    conn.commit()
    conn.close()


def generate_all_word_forms(force_regenerate: bool = False) -> dict:
    """
    Generate word forms for all learned/learning vocabulary based on user's grammar knowledge.

    Args:
        force_regenerate: If True, delete and regenerate all forms

    Returns:
        Dict with generation stats
    """
    conn = get_connection()
    cursor = conn.cursor()

    if force_regenerate:
        # Delete existing generated forms
        cursor.execute("DELETE FROM word_forms")
        conn.commit()

    # Get user's grammar knowledge
    grammar_knowledge = get_user_grammar_knowledge()

    # Get learned and learning vocabulary
    cursor.execute("""
        SELECT v.id, v.spanish, vp.status
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status IN ('learned', 'learning', 'due')
    """)

    vocabulary = cursor.fetchall()
    conn.close()

    total_forms_generated = 0
    words_processed = 0

    for row in vocabulary:
        vocab_id, spanish_word, status = row

        # Determine part of speech (simple heuristic - check if ends in -ar, -er, -ir for verbs)
        if spanish_word.endswith(('ar', 'er', 'ir')):
            pos = 'verb'
        elif spanish_word.endswith('o'):  # Common adjective ending
            pos = 'adjective'
        else:
            pos = 'noun'  # Default to noun

        # Generate forms
        forms = generate_word_forms_for_vocabulary(vocab_id, spanish_word, pos, grammar_knowledge)

        # Save to database
        save_word_forms(forms)

        total_forms_generated += len(forms)
        words_processed += 1

        # Progress indicator
        if words_processed % 10 == 0:
            print(f"Processed {words_processed} words...")

    return {
        'words_processed': words_processed,
        'total_forms_generated': total_forms_generated,
        'average_multiplier': total_forms_generated / words_processed if words_processed > 0 else 0
    }


def get_word_forms_count() -> dict:
    """
    Get count of generated word forms.

    Returns:
        Dict with counts
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(DISTINCT base_word_id) FROM word_forms")
    base_words_with_forms = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM word_forms")
    total_forms = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM word_forms WHERE form_type != 'base'")
    generated_forms = cursor.fetchone()[0] or 0

    conn.close()

    return {
        'base_words_with_forms': base_words_with_forms,
        'total_forms': total_forms,
        'generated_forms': generated_forms,
        'multiplier': total_forms / base_words_with_forms if base_words_with_forms > 0 else 0
    }


def get_all_word_forms() -> set:
    """
    Get all word forms as a set for content matching.

    Returns:
        Set of all word form strings
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT form FROM word_forms")
    forms = {row[0] for row in cursor.fetchall()}

    conn.close()
    return forms
