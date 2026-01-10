# HablaConmigo - Spanish Learning App

AI-powered Spanish learning application focused on **speaking and listening skills**, with content tailored for workplace conversations in Madrid.

## Features

### Speaking Practice
- Get random Spanish phrases from various categories
- Listen to native pronunciation (Castilian Spanish - Madrid accent)
- Record yourself speaking
- Get AI-powered pronunciation feedback with accuracy scoring
- Word-by-word analysis of your pronunciation

### Conversation Mode
- Practice with AI conversation partners: **María** (female) or **Carlos** (male)
- Natural dialogue in Spanish with gentle corrections
- Auto-play AI responses for listening practice
- Voice input support - speak your messages
- Context-aware conversations about work, weather, weekends, food

### Listening Exercises
- Dictation practice with native Spanish audio
- Type what you hear and check your accuracy
- Multiple categories: greetings, workplace, smalltalk

### Vocabulary Review
- Spaced repetition flashcard system (SM-2 algorithm)
- Hidden translations for proper recall practice
- Audio pronunciation for each word
- Rate your recall: Again / Hard / Good / Easy

### Grammar Help
- AI-powered grammar explanations
- Analyze any Spanish phrase

### Progress Tracking
- Track practice sessions and time
- Monitor accuracy improvements
- See vocabulary due for review

## Tech Stack

- **Speech-to-Text**: OpenAI Whisper (runs locally)
- **Text-to-Speech**: Edge TTS (Castilian Spanish voices)
- **LLM**: Ollama (llama3.2 or other models)
- **UI**: Gradio
- **Database**: SQLite

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running
3. **FFmpeg** installed (for audio processing)
4. A microphone for speaking practice

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Spanish.git
cd Spanish

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running with a model
ollama pull llama3.2
```

### Installing FFmpeg

**Windows (using winget):**
```bash
winget install FFmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Running the App

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run the app
python app.py
```

The app will start at **http://127.0.0.1:7860**

## Usage Guide

### Speaking Practice
1. Select a category (greetings, workplace, smalltalk, etc.)
2. Click **"Get New Phrase"** - audio plays automatically
3. Listen to the native pronunciation
4. Record yourself saying the phrase
5. Click **"Evaluate My Pronunciation"** for feedback

### Conversation Mode
1. Choose your conversation partner (María or Carlos)
2. Type a message in Spanish (or English if stuck)
3. The AI responds in Spanish and auto-plays the audio
4. Use voice input to speak your messages directly

### Vocabulary Review
1. Click **"Get Word to Review"** - shows Spanish only
2. Try to recall the English meaning
3. Click **"Reveal Translation"** to check
4. Rate how well you remembered

## Content Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Greetings | Basic greetings and farewells | Buenos días, Hasta luego |
| Workplace | Office and meeting phrases | ¿Tienes un momento?, Quedamos a las tres |
| Smalltalk | Coffee break conversations | ¿Qué tal el fin de semana? |
| Numbers | 1-1000 | uno, dos, cien, mil |
| Time | Days and time expressions | lunes, mañana, la semana que viene |
| Slang | Madrid-specific expressions | ¡Mola!, Tío/Tía, Ir de cañas |

## Configuration

### Change LLM Model

Edit `src/llm.py` and change `DEFAULT_MODEL`:

```python
DEFAULT_MODEL = "llama3.2:latest"  # or any Ollama model
```

### Available Voices

- **Female**: es-ES-ElviraNeural (María)
- **Male**: es-ES-AlvaroNeural (Carlos)

## Project Structure

```
Spanish/
├── app.py              # Main Gradio application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── PROPOSAL.md        # Original design proposal
├── data/              # SQLite database (created on first run)
│   └── hablaconmigo.db
└── src/
    ├── __init__.py
    ├── audio.py       # Whisper STT & Edge TTS
    ├── llm.py         # Ollama integration
    ├── database.py    # SQLite database operations
    └── content.py     # Initial Spanish content (100+ phrases)
```

## Troubleshooting

### "Ollama not running"
Make sure Ollama is running:
```bash
ollama serve
```

### Audio not working
- Check microphone permissions in your browser
- Ensure FFmpeg is installed and in PATH
- Use Chrome or Firefox for best compatibility

### Slow first response
- Whisper model loads on first use (~30 seconds)
- Subsequent transcriptions are faster

### "File not found" error on pronunciation
- FFmpeg is not installed or not in PATH
- Install FFmpeg and restart the app

## License

MIT License - Personal use for learning Spanish.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Edge TTS](https://github.com/rany2/edge-tts) for text-to-speech
- [Ollama](https://ollama.ai/) for local LLM
- [Gradio](https://gradio.app/) for the UI framework
