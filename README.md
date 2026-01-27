# HablaConmigo - Spanish Learning App

AI-powered Spanish learning application focused on **speaking and listening skills**, with content tailored for workplace conversations in Madrid.

## Features

### Learning Path (CEFR-Aligned)
- Structured curriculum from A1 to A2 levels
- **429 vocabulary words** and **204 phrases** across 15 units
- 3 sections: Survival Basics, Daily Life, Workplace Basics
- Progress tracking with XP and levels
- Unit unlock system based on progress

### AI Coach
- Daily personalized recommendations
- Track daily goals (XP, words reviewed, pronunciation practice)
- Streak tracking with visual indicators
- Smart suggestions based on your progress

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
- Enhanced spaced repetition (SM-2 algorithm with 4+ recall requirement)
- Word states: New, Learning, Learned, Struggling
- Auto-play pronunciation on each word
- Hidden translations for proper recall practice
- **Simplified binary rating**: Known or Again (removed Hard/Good for faster workflow)
- Compact button layout: Get Word | Known | Reveal | Again | Listen
- XP rewards for reviews
- **"Help me remember"** feature:
  - Shows an image from Unsplash (for concrete words like food, objects)
  - Generates a memorable example sentence using the word
  - Provides English translation of the sentence
  - Audio playback of the example sentence
- **Practice on Demand** buttons on Home tab:
  - Practice 20 Struggling Words - bypass spaced repetition to drill difficult words
  - Practice 20 Learning Words - review words currently being learned

### Grammar Help
- AI-powered grammar explanations
- Analyze any Spanish phrase

### Progress Tracking
- XP scoring system (500 XP per level)
- Daily streak tracking
- Words learning vs mastered counts
- Practice sessions and accuracy stats
- Vocabulary due for review

### Content Discovery
- **Import from YouTube** - Extract Spanish captions from any YouTube video
- **Import from Websites** - Extract text from Spanish articles and blogs
- **Import from Files** - Upload PDFs, text files, or paste Spanish text
- **Vocabulary Analysis** - See which words you know vs. unknown words
- **Grammar Readiness** - SpaCy-based detection of verb tenses and structures
- **Comprehension Score** - Combined metric of vocabulary + grammar readiness
- **Word Forms Matching** - Recognizes conjugated verbs, plurals, and agreements
- **Create Packages** - Save interesting content with new vocabulary to learn

### Grammar Progress Tracking
- **Kwiziq Brain Map Integration** - 43 grammar topics aligned with Kwiziq
- **CEFR Level Tracking** - Progress breakdown for A1, A2, B1 levels
- **Topic Dependencies** - Prerequisites mapped for structured learning
- **Status Levels** - Track from new → learning → learned → mastered

### Word Forms Generation
- **Vocabulary Multiplication Effect** - Generate conjugations, plurals, agreements
- **LLM-based Generation** - Creates forms based on your grammar knowledge
- **3-5x Comprehension Boost** - Recognize more words with same vocabulary
- **Smart Matching** - Content analysis includes word forms automatically

### Learning Resources (Links Tab)
- **Small Town Spanish Teacher** - Simple stories perfect for the Discover module
- **Dreaming Spanish** - Hundreds of videos in easy/intermediate Spanish
- **Kwiziq Spanish** - Interactive quizzes for grammar practice (A0-A2 levels)
- Suggested daily routines combining multiple resources
- Content discovery workflow guidance
- Complete learning system: Input + Grammar + Output

## Learning Content

| Section | Level | Units | Words |
|---------|-------|-------|-------|
| A1.1 - Survival Basics | A1 | 5 | ~140 |
| A1.2 - Daily Life | A1 | 5 | ~140 |
| A2.1 - Workplace Basics | A2 | 5 | ~150 |

**Units include:** Greetings, Numbers, Questions, Family, Time, Food, Restaurant, Shopping, Colors, Weather, Office, Meetings, Communication, Asking for Help, Common Verbs, plus Madrid Slang

## Tech Stack

- **Speech-to-Text**: OpenAI Whisper (runs locally)
- **Text-to-Speech**: Edge TTS (Castilian Spanish voices)
- **LLM**: Ollama (llama3.2 or other models)
- **Grammar Analysis**: SpaCy (Spanish NLP model)
- **UI**: Gradio
- **Database**: SQLite
- **Images**: Unsplash API (optional, for vocabulary memory aids)

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running
3. **FFmpeg** installed (for audio processing)
4. A microphone for speaking practice

## Installation

```bash
# Clone the repository
git clone https://github.com/OliverWithClaude/Spanish.git
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

# Download SpaCy Spanish model for grammar analysis
python -m spacy download es_core_news_sm

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

# Or specify a custom port
python app.py 7861
```

The app will start at **http://127.0.0.1:7860** (or your specified port)

## Usage Guide

### Home Tab
- View your AI Coach recommendations
- Check XP level and streak
- Learn 5 new words at a time
- View the full learning path

### Speaking Practice
1. Select a category and voice
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
1. Click **"Get Word"** - audio plays automatically
2. Try to recall the English meaning
3. If you know it: Click **"Known"** (gets next word automatically)
4. If unsure: Click **"Reveal"** to check, then **"Again"** to review later

## Project Structure

```
Spanish/
├── app.py                    # Main Gradio application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── CLAUDE.md                 # Development guidance for Claude Code
├── .env.example              # Environment variables template
├── PROPOSAL.md               # Original design proposal
├── LEARNING_PATH_PROPOSAL.md # Learning path design
├── data/                     # SQLite database (created on first run)
│   └── hablaconmigo.db
└── src/
    ├── __init__.py
    ├── audio.py              # Whisper STT & Edge TTS (auto-detects FFmpeg)
    ├── llm.py                # Ollama integration
    ├── database.py           # SQLite with learning path & XP system
    ├── content.py            # 429 vocabulary words, 204 phrases
    ├── images.py             # Unsplash API for vocabulary images
    ├── content_analysis.py   # Text analysis, tokenization, comprehension scoring
    ├── word_forms.py         # Word forms generation (conjugations, plurals)
    ├── grammar_patterns.py   # SpaCy-based grammar pattern detection
    ├── dele_tracker.py       # DELE exam readiness tracking
    └── frequency_data.py     # Spanish word frequency data
```

## Configuration

### Change LLM Model

Edit `src/llm.py` and change `DEFAULT_MODEL`:

```python
DEFAULT_MODEL = "llama3.2:latest"  # or any Ollama model
```

### Available Voices

- **Female**: es-ES-ElviraNeural (María)
- **Male**: es-ES-AlvaroNeural (Carlos)

### Unsplash API (Optional)

The "Help me remember" feature uses Unsplash for vocabulary images. To enable:

1. Create a free account at https://unsplash.com/join
2. Create an app at https://unsplash.com/oauth/applications
3. Copy your Access Key
4. Create a `.env` file in the project root:
   ```
   UNSPLASH_API_KEY=your_access_key_here
   ```

The feature works without the API key (sentences + audio still work, just no images).

## Advanced Features

### Word Forms Generation

The vocabulary multiplication effect automatically generates conjugated and inflected forms of your learned vocabulary:

1. Navigate to the **Progress** tab
2. Scroll to "Word Forms Multiplication Effect"
3. Click **"Generate Word Forms"**

**What it does:**
- Generates verb conjugations based on tenses you've learned (present, preterite, future, etc.)
- Creates plural forms of nouns
- Generates gender/number agreements for adjectives
- Stores all forms in the database for content matching

**Result:** A 3-5x multiplier effect where 50 base words become 150-250 recognizable forms.

**How it works:**
- Checks your grammar progress to determine which forms to generate
- Uses the LLM to generate conjugations/plurals/agreements
- Content analysis automatically matches text against both base vocabulary and generated forms

### Grammar Pattern Detection

When you analyze Spanish content (Discover tab), the app detects grammar patterns using SpaCy:

**Detected Patterns:**
- Verb tenses: Present, Preterite, Imperfect, Future, Conditional, Subjunctive
- Grammar structures: Reflexive verbs, Object pronouns, Passive voice

**Grammar Readiness Score:**
- Compares detected patterns against your Kwiziq progress
- Shows percentage of patterns you know vs. need to learn
- Provides recommendations: ✅ Perfect match | ⚠️ Moderate | ❌ Too advanced

**Example Output:**
```
Grammar Readiness: 75.0%

Grammar You Know:
- ✅ Present Tense (5 uses)
- ✅ Future Tense (2 uses)

Grammar to Learn:
- ❌ Preterite (3 uses)
- ❌ Present Subjunctive (1 use)

Recommendation: ⚠️ Good vocabulary match, but some grammar patterns are new.
```

### Content Discovery Workflow

1. **Find Spanish content** you're interested in (YouTube video, blog article, PDF)
2. **Import to Discover tab** - paste URL or text
3. **Review analysis:**
   - Vocabulary comprehension (% of words you know)
   - Grammar readiness (% of patterns you know)
   - Combined comprehension score
   - List of unknown words
4. **Create package** to save the content with new vocabulary
5. **Add words to vocabulary** - new words automatically added for learning

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
- The app auto-detects FFmpeg from WinGet installation on Windows
- If still failing, manually add FFmpeg to your system PATH

## License

MIT License - Personal use for learning Spanish.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Edge TTS](https://github.com/rany2/edge-tts) for text-to-speech
- [Ollama](https://ollama.ai/) for local LLM
- [Gradio](https://gradio.app/) for the UI framework
