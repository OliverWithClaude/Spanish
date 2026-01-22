"""
LLM module for Spanish Learning App
Handles conversation and feedback using Ollama
"""

import ollama
from typing import Generator

# Default model - can be changed based on what's installed
DEFAULT_MODEL = "llama3.2:latest"

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

    "conversation": """Eres una compañera de conversación amigable que ayuda a un principiante a practicar español.
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
Given a Spanish word and its English meaning, create ONE simple sentence that:

1. Uses the word in a clear, visual context that's easy to picture
2. Is at A1/A2 level (simple vocabulary and grammar)
3. Uses Castilian Spanish (Spain)
4. Is short (5-10 words maximum)
5. Creates a memorable mental image

Format: Return ONLY the Spanish sentence, nothing else. No translation, no explanation.

Examples:
- Word: "silla" (chair) -> "La silla roja está en la cocina."
- Word: "perro" (dog) -> "El perro grande corre en el parque."
- Word: "café" (coffee) -> "Mi café caliente está en la mesa."
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


def get_available_models() -> list:
    """Get list of available Ollama models"""
    try:
        response = ollama.list()
        return [model['name'] for model in response['models']]
    except Exception as e:
        print(f"Error getting models: {e}")
        return []


def chat(
    message: str,
    mode: str = "conversation",
    history: list = None,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Chat with the LLM

    Args:
        message: User's message
        mode: One of 'conversation', 'pronunciation_feedback', 'grammar_explanation', 'vocabulary_helper'
        history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        model: Ollama model to use

    Returns:
        Assistant's response
    """
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["conversation"])

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})

    try:
        response = ollama.chat(
            model=model,
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}. Make sure Ollama is running and the model '{model}' is installed."


def translate_to_english(spanish_text: str, model: str = DEFAULT_MODEL) -> str:
    """Translate Spanish text to English"""
    return chat(spanish_text, mode="translate", model=model)


def suggest_response(history: list, model: str = DEFAULT_MODEL) -> str:
    """Suggest a response for the learner based on conversation history"""
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
    model: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    """
    Stream chat response from LLM

    Args:
        message: User's message
        mode: Conversation mode
        history: Previous messages
        model: Ollama model

    Yields:
        Response chunks as they arrive
    """
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["conversation"])

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})

    try:
        stream = ollama.chat(
            model=model,
            messages=messages,
            stream=True
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


def generate_memory_sentence(spanish: str, english: str, model: str = DEFAULT_MODEL) -> str:
    """
    Generate a memorable sentence using a vocabulary word.

    Args:
        spanish: The Spanish word
        english: The English translation
        model: Ollama model to use

    Returns:
        A vivid Spanish sentence using the word
    """
    prompt = f'Create a memorable sentence for: "{spanish}" (meaning: {english})'
    return chat(prompt, mode="memory_sentence", model=model)


def analyze_words_with_llm(words: list, model: str = DEFAULT_MODEL) -> list:
    """
    Analyze a list of Spanish words using Ollama to get:
    - Base form (infinitive for verbs, singular for nouns)
    - English translation
    - Part of speech
    - Whether to skip (names, stop words)

    Args:
        words: List of Spanish words to analyze
        model: Ollama model to use

    Returns:
        List of dicts with analyzed word info
    """
    import json

    if not words:
        return []

    # Process in batches of 20 to avoid overwhelming the LLM
    batch_size = 20
    all_results = []

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
                data = json.loads(json_str)
                all_results.extend(data.get('words', []))
            else:
                print(f"Warning: Could not parse LLM response for word analysis")
                # Fallback: return words without analysis
                for word in batch:
                    all_results.append({
                        'spanish': word,
                        'base_form': word,
                        'english': None,
                        'pos': 'unknown',
                        'skip': False
                    })

        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode error in word analysis: {e}")
            # Fallback
            for word in batch:
                all_results.append({
                    'spanish': word,
                    'base_form': word,
                    'english': None,
                    'pos': 'unknown',
                    'skip': False
                })
        except Exception as e:
            print(f"Error in word analysis: {e}")
            # Fallback
            for word in batch:
                all_results.append({
                    'spanish': word,
                    'base_form': word,
                    'english': None,
                    'pos': 'unknown',
                    'skip': False
                })

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
