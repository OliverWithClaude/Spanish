"""
Test word forms generation with a small sample to debug issues
"""

from src.word_forms import generate_all_word_forms, get_word_forms_count

print("=" * 70)
print("Testing word forms generation with small sample (10 words)")
print("=" * 70)
print()

# Generate forms for just 10 words to see what happens
result = generate_all_word_forms(force_regenerate=True, limit=10)

print()
print("=" * 70)
print("RESULTS:")
print("=" * 70)
print(f"Words processed: {result['words_processed']}")
print(f"Total forms generated: {result['total_forms_generated']}")
print(f"Average multiplier: {result['average_multiplier']:.1f}x")
print(f"Verbs: {result.get('verbs_processed', 0)}")
print(f"Nouns: {result.get('nouns_processed', 0)}")
print(f"Adjectives: {result.get('adjectives_processed', 0)}")
print()

# Check database
stats = get_word_forms_count()
print("Database stats:")
print(f"  Base words with forms: {stats['base_words_with_forms']}")
print(f"  Total forms: {stats['total_forms']}")
print(f"  Generated forms: {stats['generated_forms']}")
print(f"  Multiplier: {stats['multiplier']:.1f}x")
print()

if stats['multiplier'] <= 1.0:
    print("WARNING: No additional forms generated (multiplier = 1.0)")
    print("This means only base forms were created, no conjugations/plurals/agreements")
    print()
    print("Possible issues:")
    print("1. LLM is not responding correctly")
    print("2. JSON parsing is failing")
    print("3. Forms are being generated but not saved")
else:
    print(f"SUCCESS: Multiplier of {stats['multiplier']:.1f}x achieved!")
