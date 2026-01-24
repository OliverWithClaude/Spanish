"""
LLM module for Spanish Learning App
Handles conversation and feedback using Ollama

Multi-tier model strategy:
- FAST_MODEL: For high-frequency, conversational tasks (speed priority)
- ACCURATE_MODEL: For linguistic analysis, grammar, definitions (accuracy priority)
- TRANSLATE_MODEL: For Spanish↔English translation (translation-optimized)
- MEMORY_MODEL: For memorable sentence generation (creative + word inclusion)
"""

import ollama
from typing import Generator, Optional

# ============ Model Configuration ============
# Fast model for conversation and real-time interactions
FAST_MODEL = "llama3.2:latest"

# Accurate model for linguistic analysis and teaching
# Options: "qwen3:30b", "gemma3:27b", "deepseek-r1:8b"
ACCURATE_MODEL = "qwen3:30b"

# Translation-optimized model (Google's TranslateGemma, released Jan 2026)
# Specialized for translation across 55 languages with superior accuracy
# 4B model selected for optimal speed/quality balance (see TRANSLATEGEMMA_BENCHMARK_RESULTS.md)
# - 2.7x faster than 27B (287ms vs 763ms avg)
# - Only 1.4% quality reduction (4.17/5 vs 4.23/5)
# - Uses ~3.3GB VRAM vs 17GB for 27B
TRANSLATE_MODEL = "translategemma:4b"

# Specialized model for memory sentence generation
# gemma2:2b has 100% success rate including target word (vs 80% with llama3.2)
# and produces clean output without unwanted explanations
MEMORY_MODEL = "gemma2:2b"

# Legacy default (for backwards compatibility)
DEFAULT_MODEL = FAST_MODEL

# ============ Temperature Settings ============
# Lower = more deterministic, Higher = more creative
TEMPERATURE_SETTINGS = {
    "conversation": 0.8,      # Natural, varied responses
    "translation": 0.3,       # Consistent, accurate
    "grammar": 0.4,           # Clear, precise explanations
    "vocabulary": 0.4,        # Accurate definitions
    "word_analysis": 0.2,     # Very precise JSON output
    "memory_sentence": 0.9,   # Creative, memorable
    "suggestion": 0.6,        # Balanced
    "pronunciation": 0.5,     # Balanced feedback
}

# System prompts for different modes
SYSTEM_PROMPTS = {
    "conversation_female": """Eres una compañera de conversación amigable que ayuda a un principiante a practicar español.
Tu nombre es María y trabajas en una oficina en Madrid.

Reglas importantes:
1. Habla SOLO en español, usando vocabulario simple y frases cortas
2. Si el usuario comete errores, corrige suavemente y continúa la conversación
3. Usa español de España (Castilian), no latinoamericano
4. Mantén las respuestas cortas (1-3 frases)
5. Haz preguntas para mantener la conversación
6. Temas comunes: el tiempo, el trabajo, el fin de semana, la comida, planes

Ejemplo de corrección suave:
Usuario: "Yo soy tiene hambre"
Tú: "¡Ah, tienes hambre! Yo también. ¿Qué te gustaría comer?"
""",

    "conversation_male": """Eres un compañero de conversación amigable que ayuda a un principiante a practicar español.
Tu nombre es Carlos y trabajas en una oficina en Madrid.

Reglas importantes:
1. Habla SOLO en español, usando vocabulario simple y frases cortas
2. Si el usuario comete errores, corrige suavemente y continúa la conversación
3. Usa español de España (Castilian), no latinoamericano
4. Mantén las respuestas cortas (1-3 frases)
5. Haz preguntas para mantener la conversación
6. Temas comunes: el tiempo, el trabajo, el fin de semana, la comida, planes

Ejemplo de corrección suave:
Usuario: "Yo soy tiene hambre"
Tú: "¡Ah, tienes hambre! Yo también. ¿Qué te gustaría comer?"
""",

    # "conversation" is kept as alias to conversation_female for backwards compatibility
    # (will be set after dict definition)

    "pronunciation_feedback": """You are a Spanish pronunciation coach helping a beginner learner.
The learner is trying to say a Spanish phrase, and you will compare what they said to what they should have said.

Provide feedback in English that is:
1. Encouraging and positive first
2. Specific about what was good
3. Specific about what to improve (if anything)
4. Tips for Spanish pronunciation (especially Castilian Spanish sounds)

Keep feedback concise (3-5 sentences).
""",

    "grammar_explanation": """You are a Spanish grammar teacher explaining concepts to a beginner.
Explain in simple English with clear examples.
Focus on practical usage, not complex rules.
Use examples relevant to everyday conversations in a Madrid workplace.
Keep explanations short and clear.
""",

    "vocabulary_helper": """You are helping a Spanish learner understand vocabulary.
For each word or phrase:
1. Give the English translation
2. Provide a simple example sentence in Spanish
3. Note any special pronunciation tips for Castilian Spanish
4. Mention any related useful words

Be concise and practical.
""",

    "translate": """You are a translator. Translate the given Spanish text to English.
Provide ONLY the English translation, nothing else. No explanations, no notes.
Keep the same tone and style as the original.""",

    "suggest_response": """You are helping a beginner Spanish learner practice conversation.
Based on the conversation history, suggest ONE simple response the learner could say next.

Rules:
1. Keep it simple - A1/A2 level Spanish
2. Make it natural and relevant to the conversation
3. Use common vocabulary and short sentences
4. Provide ONLY the Spanish suggestion, nothing else - no explanations, no translations
5. The suggestion should be 1-2 short sentences maximum
""",

    "memory_sentence": """You are helping a Spanish learner memorize vocabulary through vivid, memorable sentences.
Given a Spanish word and its English meaning, create ONE simple sentence that uses that EXACT WORD.

ABSOLUTE REQUIREMENT - NO SYNONYMS ALLOWED:
- If given "realmente", ONLY use "realmente" - NEVER use "verdaderamente"
- If given "tampoco", ONLY use "tampoco" - NEVER use "ni", "tampoco no", or any other negative words
- If given "todavía", ONLY use "todavía" - NEVER use "aún"
- If given "también", ONLY use "también" - NEVER use "además"
- SYNONYMS ARE NOT ACCEPTABLE - The exact word provided must appear letter-for-letter in your sentence
- DO NOT include ANY synonyms in the sentence - if the target word is "tampoco", do not use "ni", "aún", "todavía", etc.
- Keep the sentence simple and ONLY use the target word, avoiding all related words with similar meanings

WRONG EXAMPLES (DO NOT DO THIS):
❌ Asked for "realmente", but used "verdaderamente" -> REJECTED (synonym substitution)
❌ Asked for "todavía", but used "aún" -> REJECTED (synonym substitution)
❌ Asked for "tampoco", but used "ni" -> REJECTED (synonym substitution)
❌ Asked for "tampoco", but wrote "Ni me gusta, tampoco" -> REJECTED (contains synonym "ni" alongside target word)

RIGHT EXAMPLES (THIS IS CORRECT):
✓ Asked for "realmente" -> "La película realmente me emocionó." (exact word used, no synonyms)
✓ Asked for "todavía" -> "Todavía no he comido." (exact word used, no synonyms)
✓ Asked for "tampoco" -> "Yo tampoco quiero café." (exact word used, no synonyms)

Requirements for your sentence:
1. MUST contain the EXACT target word - character-by-character match (this is NON-NEGOTIABLE)
2. Uses the word in a clear, visual context that's easy to picture
3. Is at A1/A2 level (simple vocabulary and grammar)
4. Uses Castilian Spanish (Spain)
5. Is short (5-10 words maximum)
6. Creates a memorable mental image

MANDATORY VERIFICATION STEP:
Before submitting your sentence, perform this check:
1. Identify the target word you were given
2. Search for that EXACT word in your sentence (every letter must match)
3. If the word doesn't appear EXACTLY as given, rewrite the sentence
4. If you used a synonym instead, START OVER with the correct word
5. CRITICAL: Scan your sentence for common synonyms of the target word - if found, REWRITE to remove them:
   - If target is "tampoco", check for "ni" and remove it
   - If target is "todavía", check for "aún" and remove it
   - If target is "realmente", check for "verdaderamente" and remove it
6. The sentence should ONLY contain the target word, with NO synonyms present

Format: Return ONLY the Spanish sentence, nothing else. No translation, no explanation.

Standard examples:
- Word: "silla" (chair) -> "La silla roja está en la cocina."
- Word: "perro" (dog) -> "El perro grande corre en el parque."
- Word: "café" (coffee) -> "Mi café caliente está en la mesa."
- Word: "tampoco" (neither/not either) -> "Yo tampoco quiero café ahora."
""",

    "word_analysis": """You are a Spanish language expert helping analyze words for a vocabulary learning app.

For each Spanish word given, provide the dictionary/base form and English translation.

SKIP these word types (mark skip: true):
- Proper nouns: names (María, Carlos, Eduardo, Félix), places (Madrid, España), brands
- Articles: el, la, los, las, un, una, unos, unas
- Pronouns: yo, tú, él, ella, nosotros, vosotros, ellos, me, te, se, lo, la, le, nos
- Conjunctions: y, o, pero, porque, cuando, que, si, aunque, como
- Prepositions: de, en, a, con, por, para, sin, sobre, entre, hasta
- Interjections and sounds: ah, oh, aaah, etc.

INCLUDE these (skip: false):
- Verbs → provide INFINITIVE form (sienta → sentar, miran → mirar, habla → hablar)
- Nouns → provide SINGULAR form (personas → persona, libros → libro)
- Adjectives → provide MASCULINE SINGULAR (muchas → mucho, altas → alto)
- Adverbs → keep as-is (muy, más, también, ahora)

CRITICAL RULES:
1. If a word is ALREADY in its base/dictionary form, keep it unchanged (poema → poema, NOT poesía)
2. Do NOT change a word to a DIFFERENT word - only remove inflections (plural→singular, conjugated→infinitive)
3. "poema" and "poesía" are DIFFERENT words - do not substitute one for the other
4. Only convert verb CONJUGATIONS to infinitives, not verb-like nouns

EXAMPLES:
- "sienta" → {"spanish": "sienta", "base_form": "sentar", "english": "to sit", "pos": "verb", "skip": false}
- "miran" → {"spanish": "miran", "base_form": "mirar", "english": "to look/watch", "pos": "verb", "skip": false}
- "poema" → {"spanish": "poema", "base_form": "poema", "english": "poem", "pos": "noun", "skip": false}
- "poemas" → {"spanish": "poemas", "base_form": "poema", "english": "poem", "pos": "noun", "skip": false}
- "personas" → {"spanish": "personas", "base_form": "persona", "english": "person", "pos": "noun", "skip": false}
- "Eduardo" → {"spanish": "Eduardo", "skip": true, "reason": "name"}
- "cuando" → {"spanish": "cuando", "skip": true, "reason": "conjunction"}

Respond with ONLY valid JSON, no other text:
{"words": [...]}
"""
}

# Add backwards-compatible alias for legacy "conversation" mode
SYSTEM_PROMPTS["conversation"] = SYSTEM_PROMPTS["conversation_female"]


def get_available_models() -> list:
    """Get list of available Ollama models"""
    try:
        response = ollama.list()
        return [model['name'] for model in response['models']]
    except Exception as e:
        print(f"Error getting models: {e}")
        return []


def _get_model_for_mode(mode: str) -> str:
    """Get the appropriate model for a given mode."""
    # Translation mode uses specialized translation model
    # Translation and word analysis use specialized translation model
    if mode in ("translate", "word_analysis"):
        return TRANSLATE_MODEL

    # Modes that require accuracy (use larger model)
    accurate_modes = {
        "grammar_explanation",
        "vocabulary_helper",
    }
    if mode in accurate_modes:
        return ACCURATE_MODEL
    return FAST_MODEL


def _get_temperature_for_mode(mode: str) -> float:
    """Get the appropriate temperature for a given mode."""
    mode_to_temp = {
        "conversation_female": TEMPERATURE_SETTINGS["conversation"],
        "conversation_male": TEMPERATURE_SETTINGS["conversation"],
        "conversation": TEMPERATURE_SETTINGS["conversation"],
        "translate": TEMPERATURE_SETTINGS["translation"],
        "grammar_explanation": TEMPERATURE_SETTINGS["grammar"],
        "vocabulary_helper": TEMPERATURE_SETTINGS["vocabulary"],
        "word_analysis": TEMPERATURE_SETTINGS["word_analysis"],
        "memory_sentence": TEMPERATURE_SETTINGS["memory_sentence"],
        "suggest_response": TEMPERATURE_SETTINGS["suggestion"],
        "pronunciation_feedback": TEMPERATURE_SETTINGS["pronunciation"],
    }
    return mode_to_temp.get(mode, 0.7)


def chat(
    message: str,
    mode: str = "conversation",
    history: list = None,
    model: str = None
) -> str:
    """
    Chat with the LLM

    Args:
        message: User's message
        mode: One of 'conversation', 'pronunciation_feedback', 'grammar_explanation', 'vocabulary_helper'
        history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        model: Ollama model to use (auto-selected based on mode if None)

    Returns:
        Assistant's response
    """
    # Auto-select model based on mode if not specified
    if model is None:
        model = _get_model_for_mode(mode)

    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["conversation_female"])
    temperature = _get_temperature_for_mode(mode)

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temperature,
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}. Make sure Ollama is running and the model '{model}' is installed."


def translate_to_english(spanish_text: str, model: str = None) -> str:
    """Translate Spanish text to English (uses ACCURATE_MODEL by default)"""
    return chat(spanish_text, mode="translate", model=model)


def suggest_response(history: list, model: str = None) -> str:
    """Suggest a response for the learner based on conversation history (uses FAST_MODEL)"""
    # Build a summary of recent conversation for context
    recent = history[-6:] if len(history) > 6 else history  # Last 3 exchanges
    context = "\n".join([
        f"{'User' if m['role'] == 'user' else 'María/Carlos'}: {m['content']}"
        for m in recent
    ])

    prompt = f"Conversation so far:\n{context}\n\nSuggest what the learner could say next:"
    return chat(prompt, mode="suggest_response", model=model)


def chat_stream(
    message: str,
    mode: str = "conversation",
    history: list = None,
    model: str = None
) -> Generator[str, None, None]:
    """
    Stream chat response from LLM

    Args:
        message: User's message
        mode: Conversation mode
        history: Previous messages
        model: Ollama model (auto-selected based on mode if None)

    Yields:
        Response chunks as they arrive
    """
    # Auto-select model based on mode if not specified
    if model is None:
        model = _get_model_for_mode(mode)

    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["conversation_female"])
    temperature = _get_temperature_for_mode(mode)

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})

    try:
        stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True,
            options={
                "temperature": temperature,
            }
        )
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        yield f"Error: {e}"


def get_pronunciation_feedback(expected: str, spoken: str, accuracy: float) -> str:
    """
    Get detailed pronunciation feedback from LLM

    Args:
        expected: The phrase that should have been said
        spoken: What Whisper transcribed
        accuracy: Accuracy percentage from comparison

    Returns:
        Feedback message
    """
    prompt = f"""The learner tried to say: "{expected}"
What they actually said (according to speech recognition): "{spoken}"
Accuracy score: {accuracy}%

Please provide helpful pronunciation feedback."""

    return chat(prompt, mode="pronunciation_feedback")


def explain_grammar(text: str, question: str = None) -> str:
    """
    Explain grammar in a Spanish text

    Args:
        text: Spanish text to analyze
        question: Optional specific question about the grammar

    Returns:
        Grammar explanation
    """
    if question:
        prompt = f'In this Spanish phrase: "{text}"\n\nQuestion: {question}'
    else:
        prompt = f'Please explain the grammar in this Spanish phrase: "{text}"'

    return chat(prompt, mode="grammar_explanation")


def get_vocabulary_help(word_or_phrase: str) -> str:
    """
    Get help with Spanish vocabulary

    Args:
        word_or_phrase: Spanish word or phrase to explain

    Returns:
        Vocabulary explanation
    """
    prompt = f'Please explain this Spanish word/phrase: "{word_or_phrase}"'
    return chat(prompt, mode="vocabulary_helper")


def generate_practice_sentence(topic: str, difficulty: str = "beginner") -> str:
    """
    Generate a practice sentence for a given topic

    Args:
        topic: Topic for the sentence (e.g., "greetings", "food", "work")
        difficulty: beginner, intermediate, advanced

    Returns:
        A Spanish sentence with English translation
    """
    prompt = f"""Generate ONE simple Spanish sentence about "{topic}" for a {difficulty} learner.
Format:
Spanish: [sentence]
English: [translation]
Tip: [pronunciation or usage tip]"""

    return chat(prompt, mode="vocabulary_helper")


def generate_memory_sentence(spanish: str, english: str, model: str = None) -> str:
    """
    Generate a memorable sentence using a vocabulary word.
    Uses MEMORY_MODEL by default (gemma2:2b - optimized for 100% word inclusion).

    Args:
        spanish: The Spanish word
        english: The English translation
        model: Ollama model to use (defaults to MEMORY_MODEL if None)

    Returns:
        A vivid Spanish sentence using the word
    """
    if model is None:
        model = MEMORY_MODEL  # Use specialized model for best quality

    # Build prompt with explicit word reminder
    prompt = f'Create a memorable sentence for: "{spanish}" (meaning: {english})\n\n'
    prompt += f'IMPORTANT: Your sentence must include the EXACT word "{spanish}" - not any synonym or related word.'

    return chat(prompt, mode="memory_sentence", model=model)


def analyze_words_with_llm(words: list, model: str = None, progress_callback=None) -> list:
    """
    Analyze a list of Spanish words using Ollama to get:
    - Base form (infinitive for verbs, singular for nouns)
    - English translation
    - Part of speech
    - Whether to skip (names, stop words)

    Uses ACCURATE_MODEL by default for linguistic precision.

    Args:
        words: List of Spanish words to analyze
        model: Ollama model to use (defaults to ACCURATE_MODEL)
        progress_callback: Optional callback(current, total, message) for progress updates

    Returns:
        List of dicts with analyzed word info
    """
    import json
    import unicodedata

    if not words:
        return []

    # Process in batches of 20 to avoid overwhelming the LLM
    batch_size = 20
    all_results = []
    total_batches = (len(words) + batch_size - 1) // batch_size

    for i in range(0, len(words), batch_size):
        batch = words[i:i + batch_size]
        words_str = ", ".join(batch)

        prompt = f"Analyze these Spanish words: {words_str}"

        try:
            response = chat(prompt, mode="word_analysis", model=model)

            # Try to parse JSON from response
            # Handle case where LLM might include extra text
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]

                # Handle potential encoding issues by ensuring proper UTF-8
                # This fixes issues where accented characters may be corrupted
                try:
                    # Normalize unicode characters to ensure consistency
                    json_str = unicodedata.normalize('NFC', json_str)
                    data = json.loads(json_str)
                    all_results.extend(data.get('words', []))
                except (json.JSONDecodeError, UnicodeDecodeError) as parse_error:
                    # If JSON parsing fails, try to extract word data using simpler fallback
                    # This handles cases where encoding corruption makes JSON invalid
                    print(f"Warning: JSON parse error, attempting fallback translation lookup")
                    print(f"  Error: {parse_error}")

                    # Use frequency_data as fallback for translations
                    from src.frequency_data import get_translation, get_frequency_rank
                    from src.content_analysis import lemmatize_spanish

                    for word in batch:
                        base = word.lower().strip()
                        translation = get_translation(base)
                        base_form = base

                        # If no translation in frequency data, try lemmatization
                        if not translation:
                            lemma = lemmatize_spanish(base)
                            if lemma != base:
                                base_form = lemma
                                translation = get_translation(lemma)

                        all_results.append({
                            'spanish': word,
                            'base_form': base_form,
                            'english': translation,
                            'pos': 'unknown',
                            'skip': False
                        })
            else:
                print(f"Warning: Could not find JSON in LLM response for batch")
                print(f"  Response preview: {response[:200]}...")
                print(f"  Using fast fallback to frequency_data instead of individual retries")
                # When batch fails, use frequency_data fallback immediately
                # This is much faster than individual LLM retries (seconds vs minutes)
                from src.frequency_data import get_translation
                from src.content_analysis import lemmatize_spanish
                for word in batch:
                    try:
                        # Retry this single word
                        single_response = chat(f"Analyze this Spanish word: {word}", mode="word_analysis", model=model)
                        single_json_start = single_response.find('{')
                        single_json_end = single_response.rfind('}') + 1

                        if single_json_start >= 0 and single_json_end > single_json_start:
                            single_json_str = single_response[single_json_start:single_json_end]
                            single_json_str = unicodedata.normalize('NFC', single_json_str)
                            single_data = json.loads(single_json_str)
                            word_results = single_data.get('words', [])
                            if word_results:
                                all_results.extend(word_results)
                                continue
                    except Exception as retry_error:
                        print(f"  Individual retry failed for '{word}': {retry_error}")

                    # If individual retry also failed, use frequency_data fallback
                    from src.frequency_data import get_translation
                    from src.content_analysis import lemmatize_spanish
                    base = word.lower().strip()
                    translation = get_translation(base)
                    base_form = base
                    if not translation:
                        lemma = lemmatize_spanish(base)
                        if lemma != base:
                            base_form = lemma
                            translation = get_translation(lemma)
                    all_results.append({
                        'spanish': word,
                        'base_form': base_form,
                        'english': translation,
                        'pos': 'unknown',
                        'skip': False
                    })

        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode error in word analysis: {e}")
            # Fallback to frequency_data with lemmatization
            from src.frequency_data import get_translation
            from src.content_analysis import lemmatize_spanish
            for word in batch:
                base = word.lower().strip()
                translation = get_translation(base)
                base_form = base
                if not translation:
                    lemma = lemmatize_spanish(base)
                    if lemma != base:
                        base_form = lemma
                        translation = get_translation(lemma)
                all_results.append({
                    'spanish': word,
                    'base_form': base_form,
                    'english': translation,
                    'pos': 'unknown',
                    'skip': False
                })
        except Exception as e:
            print(f"Error in word analysis: {e}")
            # Fallback to frequency_data with lemmatization
            from src.frequency_data import get_translation
            from src.content_analysis import lemmatize_spanish
            for word in batch:
                base = word.lower().strip()
                translation = get_translation(base)
                base_form = base
                if not translation:
                    lemma = lemmatize_spanish(base)
                    if lemma != base:
                        base_form = lemma
                        translation = get_translation(lemma)
                all_results.append({
                    'spanish': word,
                    'base_form': base_form,
                    'english': translation,
                    'pos': 'unknown',
                    'skip': False
                })

        # Report progress after each batch
        if progress_callback:
            batch_num = (i // batch_size) + 1
            progress_callback(batch_num, total_batches, f"Analyzing batch {batch_num} of {total_batches}")

    return all_results


if __name__ == "__main__":
    print("Available Ollama models:", get_available_models())

    print("\nTesting conversation...")
    response = chat("Hola, me llamo Juan. ¿Cómo te llamas?", mode="conversation")
    print(f"Response: {response}")

    print("\nTesting pronunciation feedback...")
    feedback = get_pronunciation_feedback(
        expected="Buenos días, ¿cómo estás?",
        spoken="Buenos dias, como estas",
        accuracy=75.0
    )
    print(f"Feedback: {feedback}")
