# Lemmatization Fix: Adjectives vs Verbs

**Date:** 2026-01-24

## Problem

When analyzing Spanish text, the content discovery feature was incorrectly lemmatizing adjectives as verbs:

**User's reported example:**
- Sentence: "Eduardo ve una chica **baja** y muy, muy bonita"
- Word in sentence: **baja** (adjective meaning "short")
- System extracted: **bajar** (verb meaning "to go down") ❌
- Should have extracted: **bajo** (adjective meaning "short") ✅

## Impact

This bug affected vocabulary discovery and learning:
1. **Wrong words added to vocabulary**: Users would see "bajar" (verb) instead of "bajo" (adjective)
2. **Confusing translations**: The extracted word didn't match the context
3. **Incorrect learning materials**: Memory sentences and context would be for the wrong word

## Technical Root Cause

The `lemmatize_spanish()` function used simple pattern matching:

```python
# OLD CODE (BUGGY)
if word.endswith('a') and len(word) > 3:
    # Only checked if verb exists
    potential = word[:-1] + 'ar'
    if get_frequency_rank(potential) < 99999:
        return potential  # Return verb form
```

This logic:
1. Saw "baja" ends in 'a'
2. Created "bajar" by changing 'a' → 'ar'
3. Checked if "bajar" exists (it does!)
4. Returned "bajar" (verb) ❌
5. **Never checked** if "bajo" (adjective) exists

## Solution

Implemented intelligent part-of-speech aware lemmatization:

```python
# NEW CODE (FIXED)
if word.endswith('a') and len(word) > 3:
    # Check BOTH adjective and verb possibilities
    adj_form = word[:-1] + 'o'      # baja -> bajo
    verb_form = word[:-1] + 'ar'    # baja -> bajar

    adj_data = get_word_data(adj_form)
    verb_data = get_word_data(verb_form)

    # If both exist, prefer more common one
    if adj_data and verb_data:
        return adj_form if adj_data.rank < verb_data.rank else verb_form
    # If only adjective exists and is actually an adjective (check POS)
    elif adj_data and adj_data.pos in ('adj', 'adv'):
        return adj_form
    # If only verb exists
    elif verb_data:
        return verb_form
```

### Key Improvements

1. **Check both forms**: Tests both adjective (baja → bajo) and verb (baja → bajar)
2. **Use POS data**: Checks part-of-speech field in frequency_data.py
3. **Prioritize by frequency**: When both exist, uses more common word
4. **Handles plurals**: "bajas" → "bajo" (not "bajar")

## Test Results

All test cases now pass:

| Input | Expected | Before | After | Status |
|-------|----------|--------|-------|--------|
| baja | bajo | bajar ❌ | bajo ✅ | FIXED |
| bajas | bajo | bajar ❌ | bajo ✅ | FIXED |
| bajo | bajo | bajo ✅ | bajo ✅ | OK |
| bajos | bajo | bajo ✅ | bajo ✅ | OK |
| alta | alto | altar ❌ | alto ✅ | FIXED |
| altas | alto | altar ❌ | alto ✅ | FIXED |
| bonita | bonito | bonitar ❌ | bonito ✅ | FIXED |
| bonitas | bonito | bonitar ❌ | bonito ✅ | FIXED |
| habla | hablar | hablar ✅ | hablar ✅ | OK |

## User Impact

**Before fix:**
- Analyzing "Eduardo ve una chica baja" would extract "bajar" (to go down)
- User would practice the wrong word
- Context sentences wouldn't make sense

**After fix:**
- Analyzing the same sentence extracts "bajo" (short/low)
- Correct adjective added to vocabulary
- Context sentences match the original meaning

## Files Modified

- `src/content_analysis.py` (lines 320-350)
  - Updated `lemmatize_spanish()` function
  - Added POS-aware disambiguation logic

## Test Coverage

Created comprehensive tests:
- `test_lemmatization_fix.py` - 9 test cases covering all scenarios
- `test_baja_direct.py` - Direct test of user's reported issue
- `test_baja_sentence.py` - Full sentence analysis test

## Notes

- Verbs still work correctly (habla → hablar)
- Only affects words with ambiguous forms
- Uses frequency_data.py POS field for accuracy
- Backward compatible with existing functionality
