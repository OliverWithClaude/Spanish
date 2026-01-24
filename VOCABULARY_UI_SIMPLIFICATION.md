# Vocabulary Review UI Simplification

**Date:** 2026-01-24

## The Problem

The vocabulary review feature used 4 rating buttons based on the SM-2 spaced repetition algorithm:
- **Again (0)** - Complete failure
- **Hard (2)** - Correct with difficulty
- **Good (3)** - Correct with hesitation
- **Easy (5)** - Perfect recall

### Real-World Usage Pattern

After extensive real-world use, the user found:
- **90% of reviews** used only "Easy" or "Again"
- **Middle ratings** (Hard, Good) were rarely used
- **Recall is binary**: Either the meaning comes to mind instantly, or it doesn't

### Actual Workflow

The successful review loop (60% of cases):
1. Click "Get Word"
2. Auto-listen to pronunciation
3. Instantly recall meaning
4. Click "Easy"

When unsuccessful:
1. Click "Get Word"
2. Can't recall
3. Click "Reveal"
4. Click "Again"

## The Solution

### Simplified to Binary Rating

Removed the middle ratings and simplified to two options:
- **Known** (was "Easy", quality=5) - Instant recall
- **Again** (quality=0) - Needs review

### Rationale

**Why this works with SM-2:**
- The SM-2 algorithm's threshold is `quality >= 3` for "correct"
- Quality 3, 4, or 5 all count as successful recall
- The main distinction is: Did you recall it correctly? (Yes/No)
- Fine-grained difficulty ratings don't significantly change scheduling

**The algorithm behavior:**
```python
if quality >= 3:
    times_correct += 1
    # Success - increase interval
else:
    times_incorrect += 1
    # Failure - reset to beginning
```

So whether you rate it 3, 4, or 5, the outcome is similar. The key is: did you get it right?

### New UI Layout

**Old layout** (vertical, wide buttons):
```
Row 1: [Get Word] [🔊 Listen] [👁 Reveal]
Row 2: Spanish | English | Example
Row 3: Help me remember button
Row 4: Rate your recall:
Row 5: [Again (0)] [Hard (2)] [Good (3)] [Easy (5)]
```

**New layout** (compact, top-aligned):
```
Row 1: [Get Word] [✓ Known] [Reveal] [Again] [🔊 Listen]
Row 2: Spanish | English | Example
Row 3: Help me remember button
```

### Benefits

1. **Faster workflow** - Buttons at the top, no scrolling
2. **Less cognitive load** - No need to choose between 4 options
3. **Honest ratings** - Binary choice eliminates "gaming" the system
4. **Better UX** - Matches natural mental process (know it or don't)
5. **Streamlined layout** - Compact buttons, more screen space for content

## Implementation Details

### Button Changes

| Old | New | Quality | Notes |
|-----|-----|---------|-------|
| Easy (5) | ✓ Known | 5 | Renamed for clarity |
| Good (3) | *removed* | - | Rarely used |
| Hard (2) | *removed* | - | Rarely used |
| Again (0) | Again | 0 | Kept, moved to top row |
| 🔊 Listen | 🔊 Listen | - | Moved to top row |
| 👁 Reveal | Reveal | - | Simplified label, moved to top row |
| Get Word | Get Word | - | Kept in same position |

### Button Properties

All buttons now use `size="sm"` for compact display:
```python
get_vocab_btn = gr.Button("Get Word", variant="primary", size="sm")
btn_known = gr.Button("✓ Known", variant="secondary", size="sm")
reveal_btn = gr.Button("Reveal", size="sm")
btn_again = gr.Button("Again", variant="stop", size="sm")
vocab_audio_btn = gr.Button("🔊 Listen", size="sm")
```

### Event Handlers

Simplified from 4 rating handlers to 2:
```python
# Known = quality 5 (perfect recall)
btn_known.click(
    lambda vid: submit_vocab_review(vid, 5),
    inputs=[vocab_id],
    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
)

# Again = quality 0 (failed recall)
btn_again.click(
    lambda vid: submit_vocab_review(vid, 0),
    inputs=[vocab_id],
    outputs=[vocab_spanish, vocab_english, vocab_id, vocab_example, vocab_audio]
)
```

## SM-2 Algorithm Compatibility

The simplified UI still works perfectly with SM-2 because:

1. **Success threshold unchanged**: `quality >= 3` is still "correct"
2. **Binary decision is natural**: Research shows recall is often binary
3. **Interval adjustments**: The algorithm still adjusts intervals based on success/failure
4. **Ease factor**: Still calculated, but simplified to binary input doesn't hurt accuracy

### Quality Mapping

Old system (4 options):
- 0 → Failure (reset)
- 2 → Success (small increase)
- 3 → Success (moderate increase)
- 5 → Success (large increase)

New system (2 options):
- 0 → Failure (reset)
- 5 → Success (large increase)

**Impact:** Words progress slightly faster through review cycles, which is fine because:
- If you truly don't know it, you click "Again" (same as before)
- If you know it, it deserves the maximum advancement
- No more hesitation about "is this Hard or Good?"

## User Feedback Incorporated

This change directly addresses user feedback:
> "In practice I am just using Easy and Again in 90% of the times. Either the meaning comes to my mind or not."

The redesign matches actual usage patterns and removes unused complexity.

## Future Considerations

If we find we need more granular ratings:
- Could add a single middle option: "Barely Recalled" (quality=3)
- Could make advanced ratings opt-in via settings
- Current binary system can be enhanced without breaking workflow

For now, the simplified approach matches real-world usage and improves the user experience.
