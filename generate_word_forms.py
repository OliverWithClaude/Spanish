"""
Word Forms Generation - Phase 2
Generates conjugated/declined forms for vocabulary based on grammar rules
"""
import sqlite3
import json
import re
from typing import List, Dict, Tuple
from src.llm import chat

# Paths
DB_PATH = "data/hablaconmigo.db"

# System prompt for POS tagging
POS_TAGGING_PROMPT = """You are a Spanish linguistics expert. Analyze the given Spanish word and identify:
1. Part of speech (verb, noun, adjective, adverb, pronoun, etc.)
2. For verbs: the verb ending (-ar, -er, -ir) and infinitive form
3. For nouns: gender (masculine/feminine) and whether it's singular or plural
4. For adjectives: base form (masculine singular)

Respond ONLY with a JSON object in this format:
{{
  "pos": "verb|noun|adjective|pronoun|adverb|other",
  "infinitive": "base form",
  "verb_type": "ar|er|ir|irregular",
  "gender": "masculine|feminine|both",
  "notes": "any relevant notes"
}}

Word: {word}
Context (English): {english}"""

FORM_GENERATION_PROMPT = """You are a Spanish conjugation expert. Generate all forms for this word based on the grammar rule.

Word: {word} ({pos})
Grammar rule: {rule}
Applies to: {applies_to}

Generate ALL forms that this grammar rule produces. Return ONLY a JSON array of strings. No explanation.

Examples:
- hablar + present tense = hablo, hablas, habla, hablamos, hablais, hablan
- gato + plural = gatos
- rojo + agreement = rojo, roja, rojos, rojas

Return the forms as a JSON array:"""

def identify_pos(conn, word_id: int, spanish: str, english: str) -> Dict:
    """Identify part of speech for a word using LLM or rule-based detection"""
    print(f"  Analyzing: {spanish} ({english})")

    # Quick rule-based detection for verbs
    if spanish.endswith('ar'):
        print(f"    Detected: -ar verb")
        return {"pos": "verb", "infinitive": spanish, "verb_type": "ar"}
    elif spanish.endswith('er'):
        print(f"    Detected: -er verb")
        return {"pos": "verb", "infinitive": spanish, "verb_type": "er"}
    elif spanish.endswith('ir'):
        print(f"    Detected: -ir verb")
        return {"pos": "verb", "infinitive": spanish, "verb_type": "ir"}

    # Use LLM for other cases
    prompt = POS_TAGGING_PROMPT.format(word=spanish, english=english)

    try:
        response = chat(prompt, mode="vocabulary_helper")
        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            pos_data = json.loads(json_match.group())
            print(f"    LLM detected: {pos_data.get('pos', 'unknown')}")
            return pos_data
        else:
            print(f"    [WARNING] Could not parse POS response for {spanish}")
            return {"pos": "other", "infinitive": spanish, "notes": "auto-detected"}
    except Exception as e:
        print(f"    [ERROR] POS identification failed: {e}")
        return {"pos": "other", "infinitive": spanish, "notes": "error"}

def generate_forms(conn, word_id: int, spanish: str, pos_data: Dict, grammar_topics: List[Dict]) -> List[Tuple[str, str]]:
    """Generate word forms based on applicable grammar rules

    Returns: List of tuples (form, grammar_topic_id)
    """
    forms = [(spanish, None)]  # Always include the base form

    pos = pos_data.get('pos', 'other')
    verb_type = pos_data.get('verb_type', '')

    # Find applicable grammar topics
    applicable_topics = []

    for topic in grammar_topics:
        applies_to_pos = topic['applies_to_pos']
        if not applies_to_pos:
            continue


        # Check if this topic applies to this word
        if pos == 'verb':
            # Check verb type
            if verb_type and f'verb_{verb_type}' in applies_to_pos:
                applicable_topics.append(topic)
            elif 'verb' in applies_to_pos and not any(x in applies_to_pos for x in ['verb_ar', 'verb_er', 'verb_ir']):
                applicable_topics.append(topic)
        elif pos == 'noun' and 'noun' in applies_to_pos:
            applicable_topics.append(topic)
        elif pos == 'adjective' and 'adjective' in applies_to_pos:
            applicable_topics.append(topic)

    if not applicable_topics:
        print(f"    No applicable grammar rules for {spanish} ({pos})")
        return forms

    print(f"    Found {len(applicable_topics)} applicable grammar rules")

    # Generate forms using LLM for each applicable topic
    for topic in applicable_topics[:3]:  # Limit to first 3 to avoid too many LLM calls
        try:
            prompt = FORM_GENERATION_PROMPT.format(
                word=spanish,
                pos=pos,
                rule=topic['morphological_rule'] or topic['title'],
                applies_to=topic['applies_to_pos']
            )

            response = chat(prompt, mode="vocabulary_helper")

            # Extract JSON array from response
            json_match = re.search(r'\[([^\]]+)\]', response, re.DOTALL)
            if json_match:
                generated_forms = json.loads('[' + json_match.group(1) + ']')
                for form in generated_forms:
                    forms.append((form, topic['id']))
                print(f"      Generated {len(generated_forms)} forms from {topic['id']}")
        except Exception as e:
            print(f"      [ERROR] Form generation failed for {topic['id']}: {e}")

    return forms

def process_vocabulary_batch(conn, offset: int = 0, limit: int = 50):
    """Process a batch of vocabulary words"""
    cursor = conn.cursor()

    # Get grammar topics with morphological rules
    cursor.execute("""
        SELECT id, title, morphological_rule, applies_to_pos, multiplier
        FROM grammar_topics
        WHERE morphological_rule IS NOT NULL AND morphological_rule != ''
        ORDER BY cefr_level, id
    """)

    grammar_topics = []
    for row in cursor.fetchall():
        grammar_topics.append({
            'id': row[0],
            'title': row[1],
            'morphological_rule': row[2],
            'applies_to_pos': row[3].split(',') if row[3] else [],
            'multiplier': row[4]
        })

    print(f"\n[*] Found {len(grammar_topics)} grammar topics with morphological rules")

    # Get vocabulary batch
    cursor.execute("""
        SELECT id, spanish, english, category
        FROM vocabulary
        ORDER BY id
        LIMIT ? OFFSET ?
    """, (limit, offset))

    vocab_words = cursor.fetchall()
    print(f"[*] Processing {len(vocab_words)} vocabulary words (offset: {offset})\n")

    total_forms_generated = 0

    for word_id, spanish, english, category in vocab_words:
        print(f"\n[{word_id}] {spanish}")

        # Step 1: Identify POS
        pos_data = identify_pos(conn, word_id, spanish, english)

        # Step 2: Generate forms
        forms = generate_forms(conn, word_id, spanish, pos_data, grammar_topics)

        # Step 3: Store in database
        for form, topic_id in forms:
            cursor.execute("""
                INSERT OR IGNORE INTO word_forms (
                    vocabulary_word_id, grammar_topic_id, form
                ) VALUES (?, ?, ?)
            """, (word_id, topic_id, form))

        total_forms_generated += len(forms)
        print(f"    [OK] Stored {len(forms)} forms")

        conn.commit()

    return total_forms_generated

def verify_generation(conn):
    """Verify word forms generation"""
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("  WORD FORMS GENERATION VERIFICATION")
    print("="*70)

    # Total forms
    cursor.execute("SELECT COUNT(*) FROM word_forms")
    total_forms = cursor.fetchone()[0]

    # Unique words with forms
    cursor.execute("SELECT COUNT(DISTINCT vocabulary_word_id) FROM word_forms")
    words_with_forms = cursor.fetchone()[0]

    # Total vocabulary
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total_vocab = cursor.fetchone()[0]

    print(f"\n  Total vocabulary: {total_vocab} words")
    print(f"  Words with generated forms: {words_with_forms}")
    print(f"  Total word forms: {total_forms}")

    if words_with_forms > 0:
        multiplier = total_forms / words_with_forms
        print(f"  Average multiplier: {multiplier:.2f}x")

    # Show examples
    print("\n  Sample word forms:\n")
    cursor.execute("""
        SELECT v.spanish, v.english, GROUP_CONCAT(wf.form, ', ') as forms
        FROM vocabulary v
        JOIN word_forms wf ON v.id = wf.vocabulary_word_id
        GROUP BY v.id
        LIMIT 5
    """)

    for spanish, english, forms in cursor.fetchall():
        forms_list = forms.split(', ')
        print(f"    {spanish} ({english}): {len(forms_list)} forms")
        print(f"      {forms[:100]}{'...' if len(forms) > 100 else ''}")

def main():
    """Main execution"""
    print("="*70)
    print("  WORD FORMS GENERATION - PHASE 2")
    print("="*70)
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Process vocabulary in batches
        print("[*] Starting word forms generation...")
        print("    Note: This will make LLM calls and may take a while")
        print()

        # Start with verb batch for testing
        total_forms = process_vocabulary_batch(conn, offset=353, limit=10)

        print(f"\n[SUCCESS] Generated {total_forms} word forms")

        # Verify
        verify_generation(conn)

        print("\n" + "="*70)
        print("  [SUCCESS] PHASE 2 BATCH COMPLETE")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Review generated forms for accuracy")
        print("  2. Process remaining vocabulary (960 words)")
        print("  3. Proceed to Phase 3: User Progress Tracking")
        print()

    except Exception as e:
        print(f"\n[ERROR] Error during generation: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

if __name__ == "__main__":
    main()
