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
