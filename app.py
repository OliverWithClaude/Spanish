"""
HablaConmigo - Spanish Learning App
Main Gradio application
"""

import gradio as gr
import tempfile
import os
from pathlib import Path

from src.audio import (
    text_to_speech,
    transcribe_audio,
    compare_pronunciation,
    get_whisper_model,
    SPANISH_VOICES
)
from src.llm import (
    chat,
    get_pronunciation_feedback,
    explain_grammar,
    get_vocabulary_help,
    get_available_models,
    DEFAULT_MODEL
)
from src.database import (
    init_database,
    get_phrases,
    get_all_vocabulary,
    get_vocabulary_for_review,
    update_vocabulary_progress,
    record_pronunciation_attempt,
    get_statistics,
    start_session,
    end_session
)
from src.content import populate_database

# Initialize database and content
init_database()
populate_database()

# Preload Whisper model at startup to avoid timeout during first request
print("Preloading Whisper model (this may take a minute on first run)...")
get_whisper_model()
print("Whisper model loaded!")

# Global state
current_phrase = None
conversation_history = []
current_session_id = None
practice_stats = {"attempts": 0, "total_accuracy": 0}


# ============ Speaking Practice Tab ============

def get_random_phrase(category: str = "all", voice: str = "female"):
    """Get a random phrase for practice and automatically generate audio"""
    global current_phrase
    cat = None if category == "all" else category
    phrases = get_phrases(category=cat, limit=1)
    if phrases:
        current_phrase = phrases[0]
        spanish = current_phrase['spanish']
        english = current_phrase['english']
        notes = current_phrase.get('notes', '')
        # Auto-generate audio
        audio_path = text_to_speech(spanish, voice)
        return spanish, english, notes, audio_path
    return "No phrases found", "", "", None


def play_phrase_audio(spanish_text: str, voice: str = "female"):
    """Generate and return audio for the phrase"""
    if not spanish_text:
        return None
    audio_path = text_to_speech(spanish_text, voice)
    return audio_path


def evaluate_pronunciation(audio_file, expected_text: str):
    """Evaluate user's pronunciation"""
    global practice_stats

    if audio_file is None:
        return "Please record your voice first.", "", 0

    if not expected_text:
        return "No phrase to compare against.", "", 0

    try:
        # Transcribe the audio
        result = transcribe_audio(audio_file)
        spoken_text = result['text']

        # Compare pronunciation
        comparison = compare_pronunciation(expected_text, spoken_text)
        accuracy = comparison['accuracy']

        # Update stats
        practice_stats["attempts"] += 1
        practice_stats["total_accuracy"] += accuracy

        # Get detailed feedback from LLM
        feedback = get_pronunciation_feedback(expected_text, spoken_text, accuracy)

        # Record attempt in database
        if current_phrase:
            record_pronunciation_attempt(
                current_phrase['id'],
                expected_text,
                spoken_text,
                accuracy,
                feedback
            )

        # Format word-by-word results
        word_results = ""
        for wr in comparison['word_results']:
            if wr['correct']:
                word_results += f"✓ {wr['expected']}\n"
            elif wr['expected'] and wr['spoken']:
                word_results += f"✗ Expected: '{wr['expected']}' → You said: '{wr['spoken']}'\n"
            elif wr['expected']:
                word_results += f"✗ Missing: '{wr['expected']}'\n"
            else:
                word_results += f"? Extra word: '{wr['spoken']}'\n"

        return feedback, word_results, accuracy

    except Exception as e:
        return f"Error processing audio: {e}", "", 0


# ============ Conversation Tab ============

def chat_with_ai(user_message: str, history: list, voice: str = "female"):
    """Chat with AI conversation partner"""
    global conversation_history

    if not user_message.strip():
        return history, "", None

    # Add user message to history for LLM
    conversation_history.append({"role": "user", "content": user_message})

    # Use Maria (female) or Carlos (male) based on voice selection
    mode = "conversation_female" if voice == "female" else "conversation_male"

    # Get AI response
    response = chat(user_message, mode=mode, history=conversation_history[:-1])

    # Add AI response to history
    conversation_history.append({"role": "assistant", "content": response})

    # Update Gradio chat history (Gradio 6.0 format)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})

    # Generate audio for auto-play with matching voice
    audio_path = text_to_speech(response, voice)

    return history, "", audio_path


def speak_ai_response(history: list):
    """Convert last AI response to speech"""
    if history and len(history) > 0:
        # Gradio 6.0 format: list of dicts with 'role' and 'content'
        last_msg = history[-1]
        if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
            content = last_msg.get("content", "")
            # Handle case where content might be a complex object
            if hasattr(content, 'text'):
                content = content.text
            elif not isinstance(content, str):
                content = str(content)
            if content:
                audio_path = text_to_speech(content, "female")
                return audio_path
    return None


def clear_conversation():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return [], ""


def transcribe_voice_input(audio_file):
    """Transcribe voice input for conversation"""
    if audio_file is None:
        return ""
    try:
        result = transcribe_audio(audio_file)
        return result['text']
    except Exception as e:
        return f"Error: {e}"


# ============ Vocabulary Tab ============

# Store the current vocab English translation for reveal
current_vocab_english = ""

def get_vocab_for_review():
    """Get vocabulary items due for review - hide English initially"""
    global current_vocab_english
    vocab = get_vocabulary_for_review(limit=1)
    if vocab:
        item = vocab[0]
        current_vocab_english = item['english']
        # Return Spanish but hide English (show placeholder)
        return item['spanish'], "Click 'Reveal' to see translation", item['id'], ""
    current_vocab_english = ""
    return "No vocabulary due for review!", "", None, ""


def reveal_vocab_translation():
    """Reveal the English translation"""
    global current_vocab_english
    vocab = get_vocabulary_for_review(limit=1)
    if vocab:
        item = vocab[0]
        return item['english'], item.get('example_sentence', '')
    return current_vocab_english, ""


def play_vocab_audio(spanish_word: str):
    """Generate audio for vocabulary word"""
    if spanish_word and spanish_word != "No vocabulary due for review!":
        return text_to_speech(spanish_word, "female")
    return None


def submit_vocab_review(vocab_id: int, quality: int):
    """Submit vocabulary review result"""
    if vocab_id:
        update_vocabulary_progress(vocab_id, quality)
        return get_vocab_for_review()
    return "No vocabulary selected", "", None, ""


def get_vocab_help(word: str):
    """Get help with a vocabulary word"""
    if word:
        return get_vocabulary_help(word)
    return ""


# ============ Listening Tab ============

def generate_listening_exercise(category: str = "all"):
    """Generate a listening exercise"""
    cat = None if category == "all" else category
    phrases = get_phrases(category=cat, limit=1)
    if phrases:
        phrase = phrases[0]
        audio_path = text_to_speech(phrase['spanish'], "female")
        return audio_path, phrase['spanish'], phrase['english'], ""
    return None, "", "", ""


def check_listening_answer(user_answer: str, correct_answer: str):
    """Check user's listening comprehension answer"""
    if not user_answer or not correct_answer:
        return "Please type what you heard."

    comparison = compare_pronunciation(correct_answer, user_answer)

    if comparison['accuracy'] >= 90:
        return f"✓ Excellent! {comparison['accuracy']}% correct!\nYou wrote: {user_answer}"
    elif comparison['accuracy'] >= 70:
        return f"◐ Good! {comparison['accuracy']}% correct.\nYou wrote: {user_answer}\nCorrect: {correct_answer}"
    else:
        return f"✗ Keep practicing! {comparison['accuracy']}% correct.\nYou wrote: {user_answer}\nCorrect: {correct_answer}"


# ============ Grammar Tab ============

def explain_phrase_grammar(phrase: str):
    """Explain grammar in a phrase"""
    if phrase:
        return explain_grammar(phrase)
    return "Enter a Spanish phrase to analyze."


# ============ Statistics Tab ============

def get_stats_display():
    """Get formatted statistics"""
    stats = get_statistics()
    return f"""
## Your Learning Progress

| Metric | Value |
|--------|-------|
| Total Vocabulary | {stats['total_vocabulary']} words |
| Total Phrases | {stats['total_phrases']} phrases |
| Practice Sessions | {stats['total_sessions']} |
| Total Practice Time | {stats['total_practice_minutes']} minutes |
| Average Accuracy | {stats['average_accuracy']}% |
| Recent Accuracy (7 days) | {stats['recent_accuracy']}% |
| Vocabulary Due for Review | {stats['vocabulary_due']} words |

Keep practicing daily for best results!
"""


# ============ Build Gradio Interface ============

def create_app():
    """Create the Gradio application"""

    with gr.Blocks(
        title="HablaConmigo - Learn Spanish",
        theme=gr.themes.Soft(primary_hue="orange")
    ) as app:

        gr.Markdown("""
        # 🇪🇸 HablaConmigo - Learn Spanish
        ### Your AI-powered Spanish learning companion, focused on Madrid workplace conversations
        """)

        with gr.Tabs():

            # ============ Speaking Practice Tab ============
            with gr.Tab("🎤 Speaking Practice"):
                gr.Markdown("### Practice your pronunciation")

                with gr.Row():
                    category_select = gr.Dropdown(
                        choices=["all", "greetings", "workplace", "smalltalk", "numbers", "time", "slang"],
                        value="all",
                        label="Category"
                    )
                    new_phrase_btn = gr.Button("Get New Phrase", variant="primary")

                with gr.Row():
                    with gr.Column():
                        spanish_phrase = gr.Textbox(label="Spanish Phrase", interactive=False)
                        english_phrase = gr.Textbox(label="English Translation", interactive=False)
                        phrase_notes = gr.Textbox(label="Notes", interactive=False)

                    with gr.Column():
                        voice_select = gr.Radio(
                            choices=["female", "male"],
                            value="female",
                            label="Voice"
                        )
                        play_btn = gr.Button("🔊 Listen Again")
                        phrase_audio = gr.Audio(label="Native Pronunciation", type="filepath", autoplay=True)

                gr.Markdown("### Record Your Voice")
                with gr.Row():
                    user_recording = gr.Audio(
                        label="Your Recording",
                        sources=["microphone"],
                        type="filepath"
                    )
                    evaluate_btn = gr.Button("Evaluate My Pronunciation", variant="primary")

                with gr.Row():
                    accuracy_score = gr.Number(label="Accuracy Score", value=0)
                    word_comparison = gr.Textbox(label="Word-by-Word Analysis", lines=5)

                feedback_text = gr.Textbox(label="Detailed Feedback", lines=4)

                # Event handlers
                new_phrase_btn.click(
                    get_random_phrase,
                    inputs=[category_select, voice_select],
                    outputs=[spanish_phrase, english_phrase, phrase_notes, phrase_audio]
                )
                play_btn.click(
                    play_phrase_audio,
                    inputs=[spanish_phrase, voice_select],
                    outputs=[phrase_audio]
                )
                evaluate_btn.click(
                    evaluate_pronunciation,
                    inputs=[user_recording, spanish_phrase],
                    outputs=[feedback_text, word_comparison, accuracy_score]
                )

            # ============ Conversation Tab ============
            with gr.Tab("💬 Conversation"):
                gr.Markdown("""
                ### Practice conversation with your AI colleague from Madrid
                Type in Spanish (or English if stuck). They will respond in Spanish and gently correct mistakes.
                """)

                with gr.Row():
                    conv_voice_select = gr.Radio(
                        choices=["female", "male"],
                        value="female",
                        label="Conversation Partner",
                        info="Female = María, Male = Carlos"
                    )

                chatbot = gr.Chatbot(label="Conversation", height=400)

                with gr.Row():
                    with gr.Column(scale=4):
                        user_input = gr.Textbox(
                            label="Your message",
                            placeholder="Type here or use voice input below...",
                            lines=2
                        )
                    with gr.Column(scale=1):
                        send_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear Chat")

                with gr.Row():
                    voice_input = gr.Audio(
                        label="Or speak your message",
                        sources=["microphone"],
                        type="filepath"
                    )
                    transcribe_btn = gr.Button("Transcribe Voice")

                with gr.Row():
                    speak_response_btn = gr.Button("🔊 Hear Again")
                    response_audio = gr.Audio(label="AI Response Audio", type="filepath", autoplay=True)

                # Event handlers
                send_btn.click(
                    chat_with_ai,
                    inputs=[user_input, chatbot, conv_voice_select],
                    outputs=[chatbot, user_input, response_audio]
                )
                user_input.submit(
                    chat_with_ai,
                    inputs=[user_input, chatbot, conv_voice_select],
                    outputs=[chatbot, user_input, response_audio]
                )
                clear_btn.click(clear_conversation, outputs=[chatbot, user_input])
                transcribe_btn.click(
                    transcribe_voice_input,
                    inputs=[voice_input],
                    outputs=[user_input]
                )
                speak_response_btn.click(
                    speak_ai_response,
                    inputs=[chatbot],
                    outputs=[response_audio]
                )

            # ============ Listening Tab ============
            with gr.Tab("👂 Listening"):
                gr.Markdown("### Dictation Exercise - Listen and type what you hear")

                with gr.Row():
                    listen_category = gr.Dropdown(
                        choices=["all", "greetings", "workplace", "smalltalk"],
                        value="all",
                        label="Category"
                    )
                    new_listen_btn = gr.Button("New Exercise", variant="primary")

                listen_audio = gr.Audio(label="Listen carefully...", type="filepath")
                play_again_btn = gr.Button("🔊 Play Again")

                user_answer = gr.Textbox(
                    label="Type what you heard",
                    placeholder="Type the Spanish phrase here..."
                )
                check_btn = gr.Button("Check Answer", variant="primary")

                listen_result = gr.Textbox(label="Result", lines=3)

                with gr.Accordion("Show Answer", open=False):
                    correct_spanish = gr.Textbox(label="Spanish")
                    correct_english = gr.Textbox(label="English")

                # Event handlers
                new_listen_btn.click(
                    generate_listening_exercise,
                    inputs=[listen_category],
                    outputs=[listen_audio, correct_spanish, correct_english, user_answer]
                )
                check_btn.click(
                    check_listening_answer,
                    inputs=[user_answer, correct_spanish],
                    outputs=[listen_result]
                )

            # ============ Vocabulary Tab ============
            with gr.Tab("📚 Vocabulary"):
                gr.Markdown("### Spaced Repetition Vocabulary Review")

                with gr.Row():
                    get_vocab_btn = gr.Button("Get Word to Review", variant="primary")
                    vocab_audio_btn = gr.Button("🔊 Listen")
                    reveal_btn = gr.Button("👁 Reveal Translation")

                vocab_spanish = gr.Textbox(label="Spanish", interactive=False)
                vocab_english = gr.Textbox(label="English", interactive=False)
                vocab_example = gr.Textbox(label="Example", interactive=False)
                vocab_id = gr.Number(visible=False)
                vocab_audio = gr.Audio(label="Pronunciation", type="filepath", autoplay=True)

                gr.Markdown("### How well did you remember?")
                with gr.Row():
                    btn_again = gr.Button("Again (0)")
                    btn_hard = gr.Button("Hard (2)")
                    btn_good = gr.Button("Good (3)")
                    btn_easy = gr.Button("Easy (5)")

                gr.Markdown("---")
                gr.Markdown("### Look up a word")
                with gr.Row():
                    lookup_word = gr.Textbox(label="Enter Spanish word or phrase")
                    lookup_btn = gr.Button("Explain")
                lookup_result = gr.Textbox(label="Explanation", lines=5)

                # Event handlers
                get_vocab_btn.click(
                    get_vocab_for_review,
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example]
                )
                vocab_audio_btn.click(
                    play_vocab_audio,
                    inputs=[vocab_spanish],
                    outputs=[vocab_audio]
                )
                reveal_btn.click(
                    reveal_vocab_translation,
                    outputs=[vocab_english, vocab_example]
                )
                btn_again.click(
                    lambda vid: submit_vocab_review(vid, 0),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example]
                )
                btn_hard.click(
                    lambda vid: submit_vocab_review(vid, 2),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example]
                )
                btn_good.click(
                    lambda vid: submit_vocab_review(vid, 3),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example]
                )
                btn_easy.click(
                    lambda vid: submit_vocab_review(vid, 5),
                    inputs=[vocab_id],
                    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example]
                )
                lookup_btn.click(
                    get_vocab_help,
                    inputs=[lookup_word],
                    outputs=[lookup_result]
                )

            # ============ Grammar Tab ============
            with gr.Tab("📖 Grammar"):
                gr.Markdown("### Grammar Explanations")

                grammar_input = gr.Textbox(
                    label="Enter a Spanish phrase to analyze",
                    placeholder="e.g., 'Tengo que ir al supermercado'"
                )
                grammar_btn = gr.Button("Explain Grammar", variant="primary")
                grammar_output = gr.Textbox(label="Explanation", lines=10)

                grammar_btn.click(
                    explain_phrase_grammar,
                    inputs=[grammar_input],
                    outputs=[grammar_output]
                )

            # ============ Statistics Tab ============
            with gr.Tab("📊 Progress"):
                gr.Markdown("### Your Learning Statistics")
                stats_display = gr.Markdown()
                refresh_stats_btn = gr.Button("Refresh Statistics")

                refresh_stats_btn.click(get_stats_display, outputs=[stats_display])

                # Load stats on tab open
                app.load(get_stats_display, outputs=[stats_display])

        gr.Markdown("""
        ---
        *HablaConmigo* - Built with Whisper, Edge TTS, Ollama, and Gradio
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
