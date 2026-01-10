# Spanish Learning App Proposal
## "HablaConmigo" - AI-Powered Spanish Learning with Focus on Speaking & Listening

### Executive Summary

This proposal outlines a personalized Spanish learning application designed for a beginner working with colleagues from Madrid. The app focuses on **speaking and listening skills** alongside reading and writing, using modern AI technologies for pronunciation training and conversational practice.

---

## 1. Research Findings: Commercial App Features

### What Top Apps Offer

| Feature | Apps Using It | Description |
|---------|--------------|-------------|
| **Speech Recognition** | Rosetta Stone (TruAccent), Pimsleur, Rocket Spanish | Real-time pronunciation feedback |
| **Spaced Repetition** | Duolingo, Anki, Memrise | Vocabulary retention through timed review |
| **Native Audio** | Pimsleur, Memrise, LingoDeer | Authentic pronunciation from native speakers |
| **AI Conversations** | Pingo AI, Langua | Practice dialogues with AI tutors |
| **Pronunciation Scoring** | Speechling, Rosetta Stone | Phoneme/word/sentence level assessment |
| **Contextual Learning** | Babbel, Rocket Spanish | Learning through real-world scenarios |
| **Progress Tracking** | All major apps | Track streaks, levels, skills |

### Key Insights from Research
- **Pimsleur**: 83% of users improved oral proficiency by one level after 30 lessons
- **Babbel**: 73% became better speakers after 10+ hours of use
- Experts recommend **2-3 complementary tools** rather than one app
- **70% of learners** expected to use apps for language learning in 2025

---

## 2. Technical Components Needed

### A. Speech-to-Text (Listening/Transcription)

| Option | Type | Pros | Cons |
|--------|------|------|------|
| **OpenAI Whisper** | Local/Free | Excellent Spanish support, runs offline, MIT license | Requires GPU for real-time |
| **whisper-small-spanish** | Local/Free | Fine-tuned for Spanish, 20.68% WER | Smaller model |
| **Azure Speech Service** | Cloud API | Pronunciation assessment, es-ES locale | Costs money |
| **Vosk** | Local/Free | Lightweight, 20+ languages | Less accurate |

**Recommendation**: Start with **Whisper** locally for privacy and cost savings.

### B. Text-to-Speech (Native Audio Generation)

| Option | Type | Madrid Accent | Quality |
|--------|------|---------------|---------|
| **ElevenLabs** | Cloud API | Yes (es-ES) | Excellent, natural |
| **Azure TTS** | Cloud API | Yes (es-ES) | Very good |
| **Google Cloud TTS** | Cloud API | Yes (es-ES) | Very good |
| **Coqui TTS** | Local/Free | Limited | Good |
| **Edge TTS** | Free API | Yes (es-ES) | Good |

**Recommendation**: Use **ElevenLabs** (10k chars/month free) or **Edge TTS** (free) for Castilian Spanish voices.

### C. Pronunciation Assessment

| Option | Description | Pricing |
|--------|-------------|---------|
| **SpeechSuper API** | Phoneme/word/sentence scoring for Spanish | Pay per use |
| **Speechace API** | Castilian & Latin American Spanish, CEFR-aligned | Pay per use |
| **Azure Pronunciation Assessment** | 33 locales, accuracy/fluency scoring | Pay per use |
| **Custom (Whisper + LLM)** | Compare transcription to expected text | Free (local) |

**Recommendation**: Start with **custom Whisper-based assessment**, upgrade to **Speechace** for detailed phoneme feedback.

### D. LLM for Conversation & Teaching

| Option | Type | Best For |
|--------|------|----------|
| **Ollama + Llama 3** | Local/Free | Privacy, offline use, no costs |
| **Claude API** | Cloud | Best conversational quality, nuanced feedback |
| **OpenAI GPT-4** | Cloud | Strong Spanish, good for roleplay |

**Recommendation**: **Ollama** for daily practice (free), **Claude API** for complex conversations and grammar explanations.

---

## 3. Proposed App Architecture

```
+------------------------------------------------------------------+
|                     HablaConmigo App                              |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+    +-------------------+                   |
|  |   Speaking Mode   |    |  Listening Mode   |                   |
|  +-------------------+    +-------------------+                   |
|  | - Record voice    |    | - Play native     |                   |
|  | - Whisper STT     |    |   audio (TTS)     |                   |
|  | - Compare to      |    | - Dictation       |                   |
|  |   expected text   |    |   exercises       |                   |
|  | - Score pronunc.  |    | - Comprehension   |                   |
|  +-------------------+    |   questions       |                   |
|                           +-------------------+                   |
|                                                                   |
|  +-------------------+    +-------------------+                   |
|  |   Reading Mode    |    |   Writing Mode    |                   |
|  +-------------------+    +-------------------+                   |
|  | - Graded texts    |    | - Translation     |                   |
|  | - Vocab highlight |    |   exercises       |                   |
|  | - Click to hear   |    | - Grammar drills  |                   |
|  +-------------------+    | - Free writing    |                   |
|                           +-------------------+                   |
|                                                                   |
|  +-------------------+    +-------------------+                   |
|  | Conversation Mode |    |  Vocab & Review   |                   |
|  +-------------------+    +-------------------+                   |
|  | - AI roleplay     |    | - Flashcards      |                   |
|  | - Smalltalk       |    | - Spaced          |                   |
|  |   scenarios       |    |   repetition      |                   |
|  | - Madrid work     |    | - Progress        |                   |
|  |   situations      |    |   tracking        |                   |
|  +-------------------+    +-------------------+                   |
|                                                                   |
+------------------------------------------------------------------+
|                      Core Services                                |
+------------------------------------------------------------------+
|  Whisper STT | TTS (ElevenLabs/Edge) | Ollama/Claude | SQLite DB |
+------------------------------------------------------------------+
```

---

## 4. Feature Breakdown

### 4.1 Speaking Practice (Like Rosetta Stone's TruAccent)

**How it works:**
1. App shows a Spanish phrase with English translation
2. Native TTS plays the phrase (Madrid accent)
3. User records themselves speaking
4. Whisper transcribes the recording
5. System compares transcription to expected text
6. LLM provides detailed feedback on errors
7. Optional: Speechace API for phoneme-level scoring

**Example Flow:**
```
App: "Buenos días, ¿cómo estás?" (Good morning, how are you?)
     [Play Audio Button] 🔊

User: [Records] "Buenos dias, como estas"

Feedback:
✓ Good overall pronunciation!
⚠ Missing accent on "días" - try emphasizing the 'i'
⚠ "Estás" needs rising intonation for questions
Score: 78/100
[Try Again] [Next Phrase]
```

### 4.2 Listening Comprehension

**Exercises:**
- **Dictation**: Hear a phrase, type what you hear
- **Multiple Choice**: Listen and select correct meaning
- **Fill in Blanks**: Complete the sentence you hear
- **Speed Levels**: Slow, normal, fast playback

### 4.3 AI Conversation Partner

**Scenarios tailored for your Madrid workplace:**
- Morning greetings with colleagues
- Coffee break smalltalk
- Discussing weekend plans
- Project status updates (simple)
- Lunch ordering
- Basic meeting phrases

**Example Conversation:**
```
AI (as colleague): ¡Hola! ¿Qué tal el fin de semana?
User: [Speaks or types response]
AI: ¡Qué bien! Yo fui al Retiro a pasear. ¿Conoces el parque?
[Continue conversation...]

After conversation:
- Vocabulary used: 15 words
- New words learned: 3
- Grammar points: past tense (fui), questions
- Pronunciation feedback on recorded responses
```

### 4.4 Vocabulary System

**Spaced Repetition with Audio:**
- Each word includes native pronunciation
- Review includes speaking the word (not just recognition)
- Categories: Work, Greetings, Food, Weather, Numbers, etc.
- Progress tracking per category

### 4.5 Daily Smalltalk Practice

**Specifically for your use case:**
- Morning: 5-minute greeting practice
- Pre-meeting: Quick phrase review
- End of day: Conversation simulation

---

## 5. Technology Stack Recommendation

### Option A: Maximum Privacy (All Local)
```
- Frontend: Python + Gradio or Electron + React
- STT: Whisper (local)
- TTS: Coqui TTS or Edge TTS (free)
- LLM: Ollama (Llama 3.1 8B or Mistral)
- Database: SQLite
- Cost: $0
```

### Option B: Best Quality (Hybrid)
```
- Frontend: Python + Gradio or Web (React/Next.js)
- STT: Whisper (local) + Azure for pronunciation scoring
- TTS: ElevenLabs (10k free chars) or Azure
- LLM: Claude API for conversations, Ollama for drills
- Database: SQLite or PostgreSQL
- Cost: ~$10-30/month depending on usage
```

### Option C: Simple Start (Cloud-First)
```
- Frontend: Web app (Next.js)
- STT: Azure Speech Service
- TTS: Azure or ElevenLabs
- LLM: Claude API
- Database: PostgreSQL
- Cost: ~$20-50/month
```

**Recommendation: Start with Option A, add cloud services as needed.**

---

## 6. Implementation Phases

### Phase 1: Core Foundation
- Set up project structure (Python/Gradio)
- Integrate Whisper for speech-to-text
- Integrate Edge TTS for text-to-speech (es-ES voices)
- Basic phrase practice with recording/playback
- Simple pronunciation comparison

### Phase 2: Vocabulary & Spaced Repetition
- SQLite database for vocabulary
- Flashcard system with audio
- Spaced repetition algorithm (SM-2 or similar)
- Progress tracking

### Phase 3: AI Conversation Partner
- Integrate Ollama with Spanish-tuned prompts
- Conversation scenarios for workplace
- Conversation history and review
- Grammar feedback after conversations

### Phase 4: Advanced Pronunciation
- Integrate Speechace or Azure for phoneme scoring
- Visual feedback (waveform comparison)
- Targeted exercises for problem sounds

### Phase 5: Polish & Personalization
- Madrid-specific vocabulary and phrases
- Adaptive difficulty
- Weekly progress reports
- Export/backup data

---

## 7. Sample Lesson Structure

**Daily 15-minute session:**

| Time | Activity | Skills |
|------|----------|--------|
| 2 min | Vocabulary review (spaced rep) | Reading, Listening |
| 3 min | Pronunciation drills | Speaking |
| 5 min | New phrases for today | All skills |
| 5 min | AI conversation practice | Speaking, Listening |

---

## 8. Madrid-Specific Content

Since you work with people from Madrid, the app should include:

### Vocabulary
- **Castilian Spanish** pronunciation (distinción: c/z as "th")
- Madrid slang: "mola" (cool), "quedamos" (let's meet), "tío/tía" (buddy)
- Work phrases: "¿Tienes un momento?" "Quedamos a las tres"

### Cultural Context
- Greeting customs (two kisses for friends)
- Coffee culture (café con leche, cortado)
- Lunch timing (2-3 PM is common)
- Common conversation topics

---

## 9. Comparison: Our App vs Rosetta Stone

| Feature | Rosetta Stone | Our App |
|---------|---------------|---------|
| Speech Recognition | TruAccent (proprietary) | Whisper + LLM feedback |
| Pronunciation Scoring | Yes | Yes (basic) + upgradeable |
| Native Voices | Yes | Yes (TTS with es-ES) |
| AI Conversations | Limited | Full AI conversation partner |
| Customization | Generic Spanish | Madrid-specific content |
| Offline Mode | Paid feature | Yes (with Ollama) |
| Cost | $12-15/month | $0-30/month (your choice) |
| Workplace Scenarios | Generic | Custom for your needs |

---

## 10. Next Steps

1. **Confirm technology preferences:**
   - Local-first or cloud-first?
   - Preferred frontend (CLI, Desktop app, Web)?

2. **Set up development environment:**
   - Install Ollama
   - Install Whisper
   - Choose TTS provider

3. **Build MVP:**
   - Basic phrase practice with recording
   - Simple pronunciation feedback
   - 50 essential Madrid workplace phrases

4. **Iterate based on your real conversations:**
   - Add phrases you actually need
   - Focus on sounds you struggle with
   - Simulate real workplace scenarios

---

## Sources

- [Migaku - Best Spanish Learning Apps 2025](https://migaku.com/blog/spanish/best-spanish-learning-apps)
- [Pingo AI - Best Apps to Learn Spanish](https://mypingoai.com/blog/best-apps-to-learn-spanish)
- [SpeechSuper - Pronunciation Assessment API](https://www.speechsuper.com/)
- [Speechace - Spanish AI Speaking Assessment](https://www.speechace.com/comprehensive-support-for-spanish-and-french-ai-speaking-assessment/)
- [Microsoft Azure Speech Service](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
- [ElevenLabs - Spanish TTS](https://elevenlabs.io/text-to-speech/spanish)
- [Rosetta Stone TruAccent](https://www.rosettastone.com/features/truaccent-speech-recognition/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Ollama Voice Assistant](https://github.com/maudoin/ollama-voice)
- [Local Talking LLM](https://github.com/vndee/local-talking-llm)
