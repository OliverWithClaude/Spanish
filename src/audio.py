"""
Audio module for Spanish Learning App
Handles Speech-to-Text (Whisper) and Text-to-Speech (Edge TTS)
"""

import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add FFmpeg to PATH if not already available (Windows WinGet installation)
def _setup_ffmpeg():
    """Find and add FFmpeg to PATH for Whisper"""
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # FFmpeg not in PATH, try to find it
        possible_paths = [
            # WinGet installation path
            Path.home() / "AppData/Local/Microsoft/WinGet/Packages",
            # Common installation paths
            Path("C:/ffmpeg/bin"),
            Path("C:/Program Files/ffmpeg/bin"),
            Path("C:/Program Files (x86)/ffmpeg/bin"),
        ]

        for base_path in possible_paths:
            if base_path.exists():
                # Search for ffmpeg.exe
                for ffmpeg_exe in base_path.rglob("ffmpeg.exe"):
                    ffmpeg_dir = str(ffmpeg_exe.parent)
                    if ffmpeg_dir not in os.environ.get("PATH", ""):
                        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                        print(f"Added FFmpeg to PATH: {ffmpeg_dir}")
                    return True
    return True

_setup_ffmpeg()

import edge_tts
import whisper
import soundfile as sf
import numpy as np

# Whisper model (loaded lazily)
_whisper_model = None

def get_whisper_model(model_size: str = "base"):
    """Load Whisper model (cached)"""
    global _whisper_model
    if _whisper_model is None:
        print(f"Loading Whisper {model_size} model...")
        _whisper_model = whisper.load_model(model_size)
    return _whisper_model


def transcribe_audio(audio_path: str, language: str = "es") -> dict:
    """
    Transcribe audio file to text using Whisper

    Args:
        audio_path: Path to audio file
        language: Language code (default: Spanish)

    Returns:
        dict with 'text', 'segments', 'language', and 'success' flag
    """
    model = get_whisper_model()
    result = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        fp16=False,  # Better compatibility
        verbose=False,
    )

    text = result["text"].strip()
    success = True

    # Check if transcription looks like non-Spanish (basic heuristic)
    # If it contains Cyrillic or other non-Latin characters, it probably failed
    import re
    if re.search(r'[а-яА-Яёё\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text):
        success = False

    # If transcription is empty or very short, it might have failed
    if len(text) < 2:
        success = False

    return {
        "text": text,
        "segments": result.get("segments", []),
        "language": result.get("language", language),
        "success": success
    }


def transcribe_audio_from_array(audio_array: np.ndarray, sample_rate: int = 16000, language: str = "es") -> dict:
    """
    Transcribe audio from numpy array

    Args:
        audio_array: Audio data as numpy array
        sample_rate: Sample rate of audio
        language: Language code

    Returns:
        dict with transcription results
    """
    # Save to temp file (Whisper expects file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
        sf.write(temp_path, audio_array, sample_rate)

    try:
        result = transcribe_audio(temp_path, language)
    finally:
        os.unlink(temp_path)

    return result


# Edge TTS voices for Castilian Spanish (Madrid)
SPANISH_VOICES = {
    "male": "es-ES-AlvaroNeural",      # Male voice from Spain
    "female": "es-ES-ElviraNeural",    # Female voice from Spain
}


async def _generate_speech_async(text: str, voice: str, output_path: str) -> str:
    """Generate speech using Edge TTS (async)"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path


def text_to_speech(text: str, voice_gender: str = "female", output_path: str = None) -> str:
    """
    Convert text to speech using Edge TTS with Madrid Spanish voice

    Args:
        text: Spanish text to convert
        voice_gender: "male" or "female"
        output_path: Optional path for output file

    Returns:
        Path to generated audio file
    """
    voice = SPANISH_VOICES.get(voice_gender, SPANISH_VOICES["female"])

    if output_path is None:
        output_path = tempfile.mktemp(suffix=".mp3")

    # Handle potential nested event loop issues on Windows
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, use nest_asyncio or create new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _generate_speech_async(text, voice, output_path))
                future.result()
        else:
            loop.run_until_complete(_generate_speech_async(text, voice, output_path))
    except RuntimeError:
        # No event loop, create one
        asyncio.run(_generate_speech_async(text, voice, output_path))

    return output_path


async def _get_voices_async():
    """Get available voices"""
    voices = await edge_tts.list_voices()
    return voices


def list_spanish_voices():
    """List available Spanish voices from Edge TTS"""
    voices = asyncio.run(_get_voices_async())
    spanish_voices = [v for v in voices if v["Locale"].startswith("es-")]
    return spanish_voices


def compare_pronunciation(expected_text: str, spoken_text: str) -> dict:
    """
    Simple pronunciation comparison

    Args:
        expected_text: The text that should have been spoken
        spoken_text: What Whisper transcribed

    Returns:
        dict with comparison results
    """
    # Spanish number words to digits mapping
    NUMBER_MAP = {
        'cero': '0', 'uno': '1', 'una': '1', 'dos': '2', 'tres': '3',
        'cuatro': '4', 'cinco': '5', 'seis': '6', 'siete': '7',
        'ocho': '8', 'nueve': '9', 'diez': '10', 'once': '11',
        'doce': '12', 'trece': '13', 'catorce': '14', 'quince': '15',
        'dieciséis': '16', 'dieciseis': '16', 'diecisiete': '17',
        'dieciocho': '18', 'diecinueve': '19', 'veinte': '20',
        'veintiuno': '21', 'veintidós': '22', 'veintidos': '22',
        'treinta': '30', 'cuarenta': '40', 'cincuenta': '50',
        'sesenta': '60', 'setenta': '70', 'ochenta': '80',
        'noventa': '90', 'cien': '100', 'ciento': '100',
    }
    # Reverse mapping (digits to words)
    DIGIT_TO_WORD = {v: k for k, v in NUMBER_MAP.items()}

    def normalize_word(word):
        """Normalize a word, handling number equivalents"""
        word = word.lower().strip()
        # If it's a number word, return its digit equivalent for comparison
        if word in NUMBER_MAP:
            return NUMBER_MAP[word]
        # If it's a digit, keep it as is
        return word

    # Normalize texts for comparison
    expected_normalized = expected_text.lower().strip()
    spoken_normalized = spoken_text.lower().strip()

    # Remove punctuation for comparison
    import re
    expected_clean = re.sub(r'[^\w\s]', '', expected_normalized)
    spoken_clean = re.sub(r'[^\w\s]', '', spoken_normalized)

    # Word-level comparison
    expected_words = expected_clean.split()
    spoken_words = spoken_clean.split()

    # Calculate accuracy
    correct_words = 0
    word_results = []

    for i, expected_word in enumerate(expected_words):
        if i < len(spoken_words):
            spoken_word = spoken_words[i]
            # Compare normalized versions (handles numbers like "seis" vs "6")
            expected_norm = normalize_word(expected_word)
            spoken_norm = normalize_word(spoken_word)
            is_correct = expected_norm == spoken_norm
            if is_correct:
                correct_words += 1
            word_results.append({
                "expected": expected_word,
                "spoken": spoken_word,
                "correct": is_correct
            })
        else:
            word_results.append({
                "expected": expected_word,
                "spoken": None,
                "correct": False
            })

    # Check for extra words spoken
    for i in range(len(expected_words), len(spoken_words)):
        word_results.append({
            "expected": None,
            "spoken": spoken_words[i],
            "correct": False
        })

    total_words = max(len(expected_words), len(spoken_words))
    accuracy = (correct_words / total_words * 100) if total_words > 0 else 0

    return {
        "accuracy": round(accuracy, 1),
        "expected_text": expected_text,
        "spoken_text": spoken_text,
        "word_results": word_results,
        "correct_words": correct_words,
        "total_words": len(expected_words)
    }


if __name__ == "__main__":
    # Test TTS
    print("Testing Edge TTS...")
    audio_file = text_to_speech("Hola, buenos días. ¿Cómo estás?", "female")
    print(f"Generated audio: {audio_file}")

    # Test voice listing
    print("\nAvailable Spanish voices:")
    for voice in list_spanish_voices():
        print(f"  {voice['ShortName']}: {voice['Gender']}")
