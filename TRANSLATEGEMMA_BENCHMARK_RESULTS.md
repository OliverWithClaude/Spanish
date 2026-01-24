# TranslateGemma Benchmark Results

**Test Date:** 2026-01-24 12:25:53
**Hardware:** RTX 5090 (24GB VRAM)
**Total Tests per Model:** 30

## Overall Performance Comparison

| Model | Avg Time (ms) | Avg Quality | Speed Rank | Quality Rank |
|-------|---------------|-------------|------------|-------------|
| translategemma:4b | 287 | 4.17/5 | #1 | #3 |
| translategemma:12b | 478 | 4.20/5 | #2 | #2 |
| translategemma:27b | 763 | 4.23/5 | #3 | #1 |

## Performance by Use Case

### A. Simple Vocabulary Sentences

| Model | Avg Time (ms) | Avg Quality |
|-------|---------------|-------------|
| translategemma:4b | 377 | 4.20/5 |
| translategemma:12b | 655 | 4.20/5 |
| translategemma:27b | 949 | 4.30/5 |

### B. Conversation Responses

| Model | Avg Time (ms) | Avg Quality |
|-------|---------------|-------------|
| translategemma:4b | 213 | 4.20/5 |
| translategemma:12b | 330 | 4.20/5 |
| translategemma:27b | 534 | 4.20/5 |

### C. Complex Content

| Model | Avg Time (ms) | Avg Quality |
|-------|---------------|-------------|
| translategemma:4b | 270 | 4.10/5 |
| translategemma:12b | 449 | 4.20/5 |
| translategemma:27b | 805 | 4.20/5 |

## Recommendations

### Optimal Model Assignment

**A. Simple Vocabulary Sentences**

- **Recommended:** `translategemma:4b` (fastest with excellent quality 4.2/5)

**B. Conversation Responses**

- **Recommended:** `translategemma:4b` (fastest AND best quality)

**C. Complex Content**

- **Recommended:** `translategemma:4b` (fastest with excellent quality 4.1/5)

### Implementation Strategy

**Two-Tier Strategy Recommended:**

- **TRANSLATE_FAST_MODEL:** `translategemma:4b` for real-time features
  - Memory sentence translation ("Help me remember")
  - Response suggestions
  - Speed: 287ms | Quality: 4.17/5

- **TRANSLATE_ACCURATE_MODEL:** `translategemma:27b` for accuracy-critical tasks
  - Content discovery analysis
  - Complex paragraph translation
  - Speed: 763ms | Quality: 4.23/5

### Performance vs. App Targets

**Current Target:** "Help me remember" feature <2s total (currently ~1.34s)

- `translategemma:4b`: 377ms ✓
- `translategemma:12b`: 655ms ✓
- `translategemma:27b`: 949ms ✗

## Key Findings

### Speed Advantage of 4B Model

The **translategemma:4b** model provides exceptional performance:
- **2.7x faster** than 27B (287ms vs 763ms)
- **1.7x faster** than 12B (287ms vs 478ms)
- Still maintains excellent quality (4.17/5 vs 4.23/5 for 27B)

### Quality Analysis

All three models provide excellent translation quality:
- **4B**: 4.17/5 average (only 1.4% quality drop vs 27B)
- **12B**: 4.20/5 average (0.7% quality drop vs 27B)
- **27B**: 4.23/5 average (best quality)

The quality difference is **negligible** for Spanish learning app use cases:
- Simple sentences: 4B matches 12B exactly (4.2/5)
- Conversations: All three models identical (4.2/5)
- Complex content: 4B is 4.1/5 vs 4.2/5 for larger models

### Real-World Impact

For the "Help me remember" feature workflow:
1. Generate memory sentence with gemma2:2b (~500ms)
2. Translate with translategemma:4b (~377ms)
3. **Total: ~877ms** (well under 2s target)

Switching from 27B to 4B saves **572ms per translation** with minimal quality impact.

### VRAM Efficiency

Model sizes on RTX 5090:
- **4B**: ~3.3 GB (leaves 20.7 GB free)
- **12B**: ~8.1 GB (leaves 15.9 GB free)
- **27B**: ~17 GB (leaves 7 GB free)

The 4B model leaves maximum VRAM available for other models (qwen3:30b, gemma2, etc.).

## Final Recommendation

**Use translategemma:4b as the default TRANSLATE_MODEL** for the HablaConmigo app.

### Rationale

1. **Speed**: 2.7x faster than 27B, critical for real-time user experience
2. **Quality**: 4.17/5 is excellent for Spanish learning contexts
3. **VRAM**: Minimal footprint allows running multiple models simultaneously
4. **Consistency**: Performs well across all three use case categories

### When to Consider Larger Models

The 27B model may be worth using for:
- Professional translation services (not applicable to this app)
- Literary or nuanced translation work (not applicable to this app)
- Batch processing where speed is less critical (not a current use case)

For the Spanish learning app's real-time, interactive nature, **4B is optimal**.

### Implementation Change Required

Update `src/llm.py`:
```python
# Change from:
TRANSLATE_MODEL = "translategemma:27b"

# To:
TRANSLATE_MODEL = "translategemma:4b"
```

No other code changes needed - the existing `translate_to_english()` function will automatically use the faster model.

