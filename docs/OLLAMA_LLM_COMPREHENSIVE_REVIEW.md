# Comprehensive Ollama LLM Review - HablaConmigo Spanish Learning App

**Review Date:** 2026-01-22
**Current Model:** llama3.2:latest (2.0 GB)
**Available Models on System:** deepseek-r1:8b, gpt-oss:120b, gemma3:latest, qwen3:30b, llama3.2:latest, llama2:latest, gemma3:27b

---

## Executive Summary

The HablaConmigo app uses Ollama for 8 distinct LLM integration points across conversation, teaching, translation, and vocabulary analysis functions. All integrations currently use a single model (llama3.2:latest) with well-designed system prompts tailored for A1-A2 CEFR Spanish learners in a Madrid workplace context.

**Key Findings:**
- ✅ **Well-structured prompt architecture** with clear separation of concerns
- ✅ **Appropriate model choice** (llama3.2) for general-purpose tasks
- ⚠️ **Optimization opportunity**: Different tasks could benefit from different models
- ⚠️ **Performance consideration**: Word analysis batching could be improved
- ✅ **Good error handling** with fallback mechanisms

---

## System Prompts Inventory

All system prompts are defined in `src/llm.py` in the `SYSTEM_PROMPTS` dictionary.

### 1. Conversation Partners (Spanish Output)

#### `conversation_female` - María Persona
- **Purpose**: Friendly female conversation partner for speaking practice
- **Output Language**: Spanish only
- **Key Features**:
  - Madrid office worker persona
  - Gentle error correction embedded in conversation
  - Castilian Spanish (Spain) - not Latin American
  - Short responses (1-3 sentences)
  - Asks follow-up questions
  - Topics: weather, work, weekends, food, plans
- **Used By**: Conversation tab (app.py:241, 244)
- **Model Used**: llama3.2:latest
- **Example Correction Pattern**:
  - User: "Yo soy tiene hambre"
  - María: "¡Ah, tienes hambre! Yo también. ¿Qué te gustaría comer?"

#### `conversation_male` - Carlos Persona
- **Purpose**: Friendly male conversation partner (identical to María but male persona)
- **Output Language**: Spanish only
- **Differences**: Name is Carlos, otherwise identical to conversation_female
- **Used By**: Conversation tab when "male" voice selected (app.py:241-244)
- **Model Used**: llama3.2:latest

#### `conversation` (Legacy)
- **Purpose**: Default conversation mode (identical to conversation_female)
- **Status**: Appears to be legacy/fallback for conversation_female
- **Used By**: Fallback in chat() function (llm.py:190)
- **Note**: Could potentially be deprecated in favor of explicit female/male modes

---

### 2. Teaching & Feedback Modes (English Output)

#### `pronunciation_feedback` - Coaching Mode
- **Purpose**: Provide pronunciation assessment after speech recognition
- **Output Language**: English
- **Key Features**:
  - Encouraging and positive first
  - Specific about what was good
  - Specific about what to improve
  - Tips for Castilian Spanish sounds
  - Concise (3-5 sentences)
- **Used By**: Speaking Practice tab (app.py:195, llm.py:266-284)
- **Input**: Expected phrase, spoken phrase (from Whisper), accuracy %
- **Model Used**: llama3.2:latest
- **Frequency**: Every speaking practice attempt

#### `grammar_explanation` - Teaching Mode
- **Purpose**: Explain Spanish grammar concepts to beginners
- **Output Language**: English
- **Key Features**:
  - Simple English explanations
  - Clear examples
  - Practical usage focus (not complex rules)
  - Madrid workplace context
  - Short and clear
- **Used By**: Grammar tab (app.py:633-635, llm.py:287-303)
- **Model Used**: llama3.2:latest
- **Usage Pattern**: On-demand when user asks about grammar

#### `vocabulary_helper` - Word/Phrase Definitions
- **Purpose**: Help learners understand Spanish vocabulary
- **Output Language**: English
- **Key Features**:
  - English translation
  - Simple example sentence in Spanish
  - Castilian pronunciation tips
  - Related useful words
  - Concise and practical
- **Used By**:
  - Vocabulary tab lookup (app.py:495-499, llm.py:306-317)
  - Practice sentence generation (llm.py:320-337)
- **Model Used**: llama3.2:latest
- **Usage Pattern**: On-demand vocabulary lookups

---

### 3. Translation & Helper Functions (Specialized Output)

#### `translate` - Spanish→English Translation
- **Purpose**: Direct translation of Spanish text to English
- **Output Language**: English
- **Key Features**:
  - ONLY the translation, nothing else
  - No explanations, no notes
  - Preserve tone and style
  - Minimal output format
- **Used By**:
  - Conversation tab "Translate" button (app.py:284-319, llm.py:209-211)
  - Memory sentence translation (app.py:542)
- **Model Used**: llama3.2:latest
- **Usage Pattern**: On-demand translation of AI responses and memory aids
- **Note**: Very strict output format requirement

#### `suggest_response` - Context-Aware Response Suggestions
- **Purpose**: Suggest what the learner could say next in conversation
- **Output Language**: Spanish only
- **Key Features**:
  - A1/A2 level vocabulary
  - Natural and relevant to conversation
  - Common vocabulary, short sentences
  - ONLY the Spanish suggestion (no translation/explanation)
  - 1-2 short sentences maximum
- **Used By**: Conversation tab "Suggest" button (app.py:322-333, llm.py:214-224)
- **Input**: Last 6 messages from conversation history
- **Model Used**: llama3.2:latest
- **Usage Pattern**: On-demand when learner needs help responding

#### `memory_sentence` - Memorable Vocabulary Sentences
- **Purpose**: Generate vivid, memorable sentences for vocabulary memorization
- **Output Language**: Spanish only
- **Key Features**:
  - Clear, visual context (easy to picture)
  - A1/A2 level (simple vocabulary and grammar)
  - Castilian Spanish
  - Short (5-10 words maximum)
  - Creates memorable mental image
  - ONLY the Spanish sentence (no translation/explanation)
- **Used By**: Vocabulary tab "Help me remember" feature (app.py:539, llm.py:340-353)
- **Model Used**: llama3.2:latest
- **Usage Pattern**: On-demand memory aid generation
- **Example Output**:
  - Word: "silla" → "La silla roja está en la cocina."

---

### 4. Advanced Analysis (Structured Output)

#### `word_analysis` - Vocabulary Analysis for Content Discovery
- **Purpose**: Analyze Spanish words to get base forms, translations, and filter names/stopwords
- **Output Language**: JSON structured data
- **Key Features**:
  - Returns base/dictionary forms (infinitives, singular)
  - Filters proper nouns, articles, pronouns, conjunctions, prepositions
  - Part-of-speech tagging
  - English translations
  - Critical rules for verb lemmatization
  - MUST return valid JSON only
- **Used By**: Content Discovery tab (app.py:931, content_analysis.py:655-766, llm.py:356-433)
- **Input**: Batch of up to 20 words at a time
- **Output Format**: `{"words": [{"spanish": "...", "base_form": "...", "english": "...", "pos": "...", "skip": bool}]}`
- **Model Used**: llama3.2:latest
- **Processing**: Batch processing in chunks of 20 words
- **Error Handling**: Fallback to returning words unchanged if JSON parsing fails
- **Usage Pattern**: When user analyzes Spanish text to discover new vocabulary
- **Critical Function**: This is the most complex LLM task, requiring precise linguistic analysis

---

## LLM Integration Points in Application

### File: `src/llm.py` - Core LLM Functions

| Function | Purpose | System Prompt | Input | Output | Lines |
|----------|---------|---------------|-------|--------|-------|
| `chat()` | Main chat interface | Any mode | message, history | String response | 172-206 |
| `chat_stream()` | Streaming chat | Any mode | message, history | Generator[str] | 227-263 |
| `get_pronunciation_feedback()` | Pronunciation coaching | pronunciation_feedback | expected, spoken, accuracy | Feedback string | 266-284 |
| `explain_grammar()` | Grammar teaching | grammar_explanation | text, optional question | Explanation | 287-303 |
| `get_vocabulary_help()` | Word definitions | vocabulary_helper | word/phrase | Help text | 306-317 |
| `generate_practice_sentence()` | Practice generation | vocabulary_helper | topic, difficulty | Sentence+translation | 320-337 |
| `translate_to_english()` | Translation | translate | spanish_text | English translation | 209-211 |
| `suggest_response()` | Response suggestions | suggest_response | conversation history | Spanish suggestion | 214-224 |
| `generate_memory_sentence()` | Memory aids | memory_sentence | spanish, english | Memorable sentence | 340-353 |
| `analyze_words_with_llm()` | Vocabulary analysis | word_analysis | list of words | JSON word data | 356-433 |

### File: `app.py` - UI Integration Points

| Tab/Feature | Function Called | LLM Purpose | Frequency |
|-------------|-----------------|-------------|-----------|
| Speaking Practice | `get_pronunciation_feedback()` | Evaluate pronunciation after each attempt | High - every practice |
| Conversation (Female) | `chat()` with mode=conversation_female | Generate María's responses | High - every message |
| Conversation (Male) | `chat()` with mode=conversation_male | Generate Carlos's responses | High - every message |
| Conversation "Translate" | `translate_to_english()` | Translate AI response | On-demand |
| Conversation "Suggest" | `suggest_response()` | Suggest learner's next response | On-demand |
| Vocabulary Lookup | `get_vocabulary_help()` | Explain word/phrase | On-demand |
| Vocabulary "Help Remember" | `generate_memory_sentence()` + `translate_to_english()` | Create memory sentence + translate it | On-demand |
| Grammar | `explain_grammar()` | Explain Spanish grammar | On-demand |
| Content Discovery | `analyze_words_with_llm()` via `process_words_with_llm()` | Analyze text for new vocabulary | On-demand, batch |

### File: `src/content_analysis.py` - Advanced Processing

| Function | LLM Usage | Purpose |
|----------|-----------|---------|
| `process_words_with_llm()` | Calls `analyze_words_with_llm()` | Filter names, get base forms, verify translations for discovered vocabulary |

---

## Performance Characteristics by Use Case

### High-Frequency Operations (Need Speed)

**1. Conversation Chat (María/Carlos)**
- **Current Model**: llama3.2:latest (2.0 GB)
- **Frequency**: Every user message in conversation
- **Token Count**: Low-Medium (1-3 sentence responses)
- **Priority**: Response time critical for natural conversation flow
- **Recommendation**: ✅ llama3.2 is appropriate - small, fast, good for dialogue

**2. Pronunciation Feedback**
- **Current Model**: llama3.2:latest
- **Frequency**: Every speaking practice attempt
- **Token Count**: Low (3-5 sentences)
- **Priority**: Speed important but not critical (user expects slight delay)
- **Recommendation**: ✅ llama3.2 works well - fast enough, generates helpful feedback

### Medium-Frequency Operations (Balance Speed/Quality)

**3. Translation (Spanish→English)**
- **Current Model**: llama3.2:latest
- **Frequency**: On-demand (Translate button, memory aids)
- **Token Count**: Very low (direct translation only)
- **Priority**: Accuracy > Speed
- **Recommendation**: ⚠️ Consider specialized translation model for better accuracy
  - **Alternative**: qwen3:30b (better multilingual capabilities)
  - **Alternative**: Keep llama3.2 for speed if accuracy is acceptable

**4. Response Suggestions**
- **Current Model**: llama3.2:latest
- **Frequency**: On-demand ("Suggest" button)
- **Token Count**: Very low (1-2 sentences)
- **Priority**: Speed + A1-A2 appropriate vocabulary
- **Recommendation**: ✅ llama3.2 appropriate

**5. Memory Sentence Generation**
- **Current Model**: llama3.2:latest
- **Frequency**: On-demand ("Help me remember")
- **Token Count**: Very low (5-10 words)
- **Priority**: Creativity + Simplicity
- **Recommendation**: ✅ llama3.2 works well for simple creative tasks

### Low-Frequency, High-Complexity Operations (Prioritize Quality)

**6. Grammar Explanations**
- **Current Model**: llama3.2:latest
- **Frequency**: Occasional (Grammar tab usage)
- **Token Count**: Medium (detailed explanations)
- **Priority**: Accuracy and clarity critical
- **Recommendation**: ⚠️ Consider larger model for better explanations
  - **Alternative**: qwen3:30b or gemma3:27b for deeper linguistic knowledge
  - **Trade-off**: Slower but more accurate explanations

**7. Vocabulary Definitions**
- **Current Model**: llama3.2:latest
- **Frequency**: Occasional (word lookups)
- **Token Count**: Medium
- **Priority**: Accuracy critical
- **Recommendation**: ⚠️ Consider larger model for better linguistic knowledge
  - **Alternative**: qwen3:30b for more comprehensive definitions

**8. Word Analysis (Content Discovery)**
- **Current Model**: llama3.2:latest
- **Frequency**: Rare (when analyzing external content)
- **Token Count**: High (batches of 20 words, multiple batches)
- **Priority**: Accuracy CRITICAL - incorrect base forms corrupt vocabulary database
- **Current Implementation**: Batch size of 20 words
- **Recommendation**: 🔴 HIGH PRIORITY - Consider larger model for linguistic accuracy
  - **Alternative**: qwen3:30b or gemma3:27b - better at linguistic analysis
  - **Critical Need**: Correct lemmatization (verbs→infinitive, nouns→singular)
  - **Risk**: llama3.2 may struggle with edge cases, irregular verbs, subtle distinctions

---

## Model Recommendations by Use Case

### Option 1: Keep Current Setup (Simplest)
**Model**: llama3.2:latest for everything
**Pros**:
- Simple configuration
- Fastest response times across the board
- Smallest memory footprint (2.0 GB)
- Consistent behavior

**Cons**:
- May miss nuances in grammar explanations
- Word analysis accuracy could be better
- Translation quality may be basic

**Best For**: Users prioritizing speed and responsiveness

---

### Option 2: Two-Tier Model Strategy (Recommended)

#### Fast Model: llama3.2:latest (2.0 GB)
**Use For**:
- ✅ Conversation (María/Carlos)
- ✅ Pronunciation Feedback
- ✅ Response Suggestions
- ✅ Memory Sentences
- ✅ Translation (if accuracy is acceptable)

#### Accurate Model: qwen3:30b (18 GB) or gemma3:27b (17 GB)
**Use For**:
- ✅ Word Analysis (critical for vocabulary integrity)
- ✅ Grammar Explanations
- ✅ Vocabulary Definitions
- ⚠️ Translation (if higher accuracy needed)

**Pros**:
- Best balance of speed and accuracy
- Critical functions get the accuracy they need
- High-frequency functions stay fast
- Only ~20 GB total disk space

**Cons**:
- More complex configuration
- Need to specify model per function
- Higher memory usage when using both

**Implementation**: Add model parameter to high-level functions in app.py
```python
# Example modification
FAST_MODEL = "llama3.2:latest"
ACCURATE_MODEL = "qwen3:30b"

# In app.py
feedback = get_pronunciation_feedback(..., model=FAST_MODEL)
analysis = analyze_words_with_llm(..., model=ACCURATE_MODEL)
```

---

### Option 3: Specialized Models (Advanced)

#### Conversation: llama3.2:latest (2.0 GB)
- Fast, good for dialogue

#### Translation: qwen3:30b (18 GB)
- Better multilingual capabilities
- More accurate translations

#### Linguistic Analysis: gemma3:27b (17 GB)
- Excellent for grammar and word analysis
- Strong linguistic knowledge

**Pros**: Optimal performance for each task
**Cons**: Most complex, highest resource usage, harder to maintain

---

## Current Performance Concerns

### 1. Word Analysis Batching (MEDIUM PRIORITY)

**Current Implementation**: `analyze_words_with_llm()` in llm.py:356-433
- Processes in batches of 20 words
- No concurrency or parallelization
- Sequential batch processing could be slow for large texts

**Example**: Analyzing 100 words = 5 sequential LLM calls
- At ~2 seconds per call = 10 seconds total wait time

**Optimization Options**:
1. **Increase batch size** (if model can handle it)
   - Test with 30-50 words per batch
   - Monitor JSON parsing reliability

2. **Add progress feedback** for user
   - Show "Analyzing batch 1 of 5..." during processing

3. **Async batch processing** (advanced)
   - Process multiple batches concurrently
   - Requires async Ollama library usage

### 2. JSON Parsing Robustness (LOW PRIORITY)

**Current**: Lines 389-420 in llm.py
- Tries to extract JSON from response
- Falls back to returning words unchanged on error
- Basic error handling

**Potential Improvements**:
- Retry logic if JSON is malformed
- More explicit JSON format instructions in prompt
- Validation of returned data structure

### 3. Conversation History Management (LOW PRIORITY)

**Current**: Full conversation history passed to LLM
- Could grow very large in long conversations
- May slow down responses over time

**Optimization**:
- Limit context window (currently uses last 6 for suggestions, full for conversation)
- Consider implementing context summarization
- Monitor token counts in long sessions

---

## Testing Recommendations

### Before Making Model Changes

1. **Establish Baseline Performance**
   ```bash
   # Time a conversation response
   curl http://localhost:11434/api/generate \
     -d '{"model": "llama3.2", "prompt": "Hola, ¿cómo estás?", "stream": false}' \
     | jq '.eval_duration'

   # Time word analysis
   # (measure from UI or via direct function call)
   ```

2. **Test Model Switching**
   - Modify DEFAULT_MODEL in src/llm.py
   - Test each prompt type
   - Verify output quality and format
   - Measure response times

3. **Quality Checks**
   - **Conversation**: Does it stay in character? Appropriate vocabulary level?
   - **Grammar**: Are explanations clear and accurate?
   - **Word Analysis**: Check base forms (infinitives, singular forms)
   - **Translation**: Verify accuracy for common phrases
   - **Memory Sentences**: Are they visual and memorable?

### Recommended Test Inputs

**Conversation**:
- "Hola, ¿cómo estás?" (basic greeting)
- "Yo soy tiene hambre" (intentional error)
- "¿Qué hiciste este fin de semana?" (past tense question)

**Word Analysis** (critical test):
- Input: ["sienta", "miran", "poemas", "Eduardo", "cuando"]
- Expected:
  - sienta → base: sentar, skip: false
  - miran → base: mirar, skip: false
  - poemas → base: poema, skip: false
  - Eduardo → skip: true (name)
  - cuando → skip: true (conjunction)

**Grammar**:
- "Tengo que ir al trabajo" (obligation)
- "Me gusta el café" (indirect object pronoun)
- "Estoy trabajando" (present progressive)

**Translation**:
- "¡Ah, tienes hambre! ¿Qué te gustaría comer?" (conversational)
- "El perro grande corre en el parque." (simple sentence)
- "Necesito ayuda con este proyecto." (workplace context)

---

## API Call Patterns

### Current Ollama Usage

**Library**: `ollama` Python package
**Import**: `import ollama` (llm.py:6)

**Main Functions Used**:
1. `ollama.list()` - Get available models (llm.py:165)
2. `ollama.chat()` - Standard chat completion (llm.py:200, 255)
   - Parameters: model, messages
   - Supports streaming (stream=True)

**Message Format**:
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    # ... history ...
    {"role": "user", "content": current_message}
]
```

**Error Handling**:
- Try/except blocks around all LLM calls
- Returns error messages to user (llm.py:206, 262)
- Fallback behavior in word analysis (llm.py:400-421)

---

## Configuration Management

### Current Configuration

**File**: `src/llm.py`
**Line 10**: `DEFAULT_MODEL = "llama3.2:latest"`

**To Change Model Globally**:
```python
# In src/llm.py line 10
DEFAULT_MODEL = "qwen3:30b"  # Example: switch to larger model
```

**To Use Different Models Per Task** (requires code changes):
```python
# Add at top of src/llm.py
FAST_MODEL = "llama3.2:latest"
ACCURATE_MODEL = "qwen3:30b"

# Then in specific functions:
def analyze_words_with_llm(words: list, model: str = ACCURATE_MODEL):
    # Use accurate model for critical linguistic analysis

def chat(message: str, mode: str = "conversation",
         history: list = None, model: str = FAST_MODEL):
    # Use fast model for conversation
```

---

## System Requirements Analysis

### Current Setup (llama3.2:latest only)
- **Disk Space**: 2.0 GB
- **RAM Usage**: ~2-3 GB during inference
- **VRAM** (if GPU): ~2 GB
- **Speed**: Fast (2.0 GB model)

### Recommended Two-Tier Setup
- **Disk Space**: 20 GB (llama3.2 + qwen3:30b)
- **RAM Usage**:
  - llama3.2 loaded: ~3 GB
  - qwen3:30b loaded: ~30 GB
  - Both can swap based on usage
- **Speed**:
  - Fast operations: <2s (llama3.2)
  - Accurate operations: 3-5s (qwen3:30b)

### Alternative: gemma3:27b
- **Disk Space**: 19 GB (llama3.2 + gemma3:27b)
- **RAM Usage**: Similar to qwen3
- **Advantage**: Google's strong linguistic training

---

## Prompt Engineering Quality Assessment

### Strengths ✅

1. **Clear Role Definitions**: Each prompt starts with clear role/persona
2. **Explicit Output Constraints**: Specifies language, length, format
3. **CEFR Level Awareness**: Prompts reference A1/A2 level appropriately
4. **Cultural Context**: Madrid workplace theme consistent
5. **Few-Shot Examples**: Includes examples where helpful (conversation_female, memory_sentence)
6. **Output Format Strictness**: Clear instructions for translate, suggest_response, memory_sentence
7. **Error Handling Guidance**: Shows how to correct gently (conversation)

### Areas for Improvement ⚠️

1. **conversation vs conversation_female/male**: Legacy prompt could be removed
2. **JSON Output Validation**: word_analysis could benefit from schema enforcement
3. **Temperature Settings**: Currently using defaults - could optimize per task
   - Lower for factual tasks (translate, word_analysis)
   - Higher for creative tasks (memory_sentence, conversation)
4. **Token Limits**: No max_tokens specified - could control verbosity better
5. **Stop Sequences**: Not used - could prevent over-generation

### Recommended Prompt Enhancements

**For word_analysis**:
```python
# Add explicit JSON schema to prompt
"Respond with valid JSON matching this schema:
{
  \"words\": [
    {
      \"spanish\": \"string (original word)\",
      \"base_form\": \"string (lemmatized form)\",
      \"english\": \"string (translation)\",
      \"pos\": \"string (verb|noun|adjective|adverb)\",
      \"skip\": \"boolean (true if name/stopword)\"
    }
  ]
}
Do not include any text outside the JSON structure."
```

**For conversation**:
```python
# Add temperature and token limits
response = ollama.chat(
    model=model,
    messages=messages,
    options={
        "temperature": 0.8,  # More natural, varied responses
        "max_tokens": 100    # Enforce short responses
    }
)
```

**For translation**:
```python
# Lower temperature for consistency
response = ollama.chat(
    model=model,
    messages=messages,
    options={
        "temperature": 0.3,  # More deterministic translation
        "max_tokens": 200
    }
)
```

---

## Security & Safety Considerations

### Current Safety Measures ✅
1. **No User Data Sent**: LLM only receives text content, no personal info
2. **Local Processing**: All LLM calls to local Ollama server
3. **No External API Keys**: Self-hosted model
4. **Sandboxed Prompts**: System prompts clearly define boundaries

### Recommendations
1. **Input Sanitization**: Consider limiting input length for word_analysis
2. **Output Validation**: Validate LLM outputs before database insertion (especially word_analysis)
3. **Rate Limiting**: Could add rate limits for expensive operations
4. **Monitoring**: Log unusual outputs or errors for review

---

## Summary of Optimization Opportunities

### 🔴 High Priority
1. **Use larger model for word_analysis** (qwen3:30b or gemma3:27b)
   - Critical for vocabulary database integrity
   - Affects: Content Discovery feature
   - Impact: Better lemmatization, fewer errors

### 🟡 Medium Priority
2. **Add temperature/token controls** to LLM calls
   - Improve output quality and consistency
   - Affects: All LLM functions
   - Impact: Better control over responses

3. **Optimize word_analysis batching**
   - Add progress indicators for large texts
   - Consider larger batch sizes
   - Affects: Content Discovery with large texts
   - Impact: Better user experience

### 🟢 Low Priority
4. **Clean up legacy conversation prompt**
   - Remove unused conversation mode
   - Affects: Code clarity
   - Impact: Maintainability

5. **Add conversation history trimming**
   - Prevent extremely long contexts
   - Affects: Long conversation sessions
   - Impact: Consistent performance

---

## Next Steps for Implementation

### Phase 1: Testing Current Performance
1. Measure baseline response times for each LLM function
2. Test current word_analysis accuracy on known edge cases
3. Document any current quality issues

### Phase 2: Model Evaluation
1. Test qwen3:30b with word_analysis prompt
2. Compare accuracy against llama3.2
3. Measure response time difference
4. Verify JSON output reliability

### Phase 3: Implementation
1. Add model selection configuration
2. Update word_analysis to use accurate model
3. Add temperature/token controls
4. Test end-to-end with both models

### Phase 4: Optimization
1. Tune batch sizes for word_analysis
2. Add progress indicators
3. Optimize conversation history management
4. Monitor production performance

---

## Conclusion

The HablaConmigo app has a well-designed LLM integration with clear separation of concerns and appropriate prompt engineering for language learning. The current use of llama3.2:latest is a reasonable default, but there are opportunities to improve accuracy for critical linguistic tasks by using a larger model (qwen3:30b or gemma3:27b) for word analysis and potentially grammar explanations.

**Recommended Action**: Implement a two-tier model strategy with llama3.2 for conversational speed and qwen3:30b for linguistic accuracy, prioritizing the word_analysis function upgrade.
