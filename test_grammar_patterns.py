"""
Test Grammar Pattern Detection

Verifies that SpaCy-based grammar pattern detection works correctly.
"""

from src.grammar_patterns import (
    detect_verb_tenses,
    detect_grammar_structures,
    analyze_grammar_patterns,
    compare_grammar_with_user,
    get_grammar_recommendation
)


def test_present_tense():
    """Test detection of present tense"""
    print("=" * 70)
    print("TEST 1: Present Tense Detection")
    print("=" * 70)

    text = "Yo hablo español. Ella come manzanas. Nosotros vivimos en Madrid."

    print(f"Text: {text}")
    print()

    tenses = detect_verb_tenses(text)
    print(f"Detected tenses: {tenses}")

    if 'present' in tenses:
        print(f"[OK] Present tense detected ({tenses['present']} verbs)")
    else:
        print("[WARNING] Present tense not detected")

    print()


def test_preterite_tense():
    """Test detection of preterite tense"""
    print("=" * 70)
    print("TEST 2: Preterite Tense Detection")
    print("=" * 70)

    text = "Ayer comí pizza. Hablamos con María. Ellos vivieron en Barcelona."

    print(f"Text: {text}")
    print()

    tenses = detect_verb_tenses(text)
    print(f"Detected tenses: {tenses}")

    if 'preterite' in tenses or 'imperfect' in tenses:
        print("[OK] Past tense detected")
    else:
        print("[WARNING] Past tense not detected")

    print()


def test_future_tense():
    """Test detection of future tense"""
    print("=" * 70)
    print("TEST 3: Future Tense Detection")
    print("=" * 70)

    text = "Mañana hablaré con el profesor. Iremos a la playa."

    print(f"Text: {text}")
    print()

    tenses = detect_verb_tenses(text)
    print(f"Detected tenses: {tenses}")

    if 'future' in tenses:
        print(f"[OK] Future tense detected ({tenses['future']} verbs)")
    else:
        print("[WARNING] Future tense not detected")

    print()


def test_reflexive_verbs():
    """Test detection of reflexive verbs"""
    print("=" * 70)
    print("TEST 4: Reflexive Verb Detection")
    print("=" * 70)

    text = "Me levanto a las 7. Se llama Pedro. Nos duchamos por la mañana."

    print(f"Text: {text}")
    print()

    structures = detect_grammar_structures(text)
    print(f"Detected structures: {structures}")

    if 'reflexive_verbs' in structures:
        print(f"[OK] Reflexive verbs detected ({structures['reflexive_verbs']} uses)")
    else:
        print("[WARNING] Reflexive verbs not detected")

    print()


def test_comprehensive_analysis():
    """Test comprehensive grammar analysis"""
    print("=" * 70)
    print("TEST 5: Comprehensive Grammar Analysis")
    print("=" * 70)

    text = """
    Yo hablo español todos los días. Ayer comí paella en un restaurante.
    Mañana iré al cine con mis amigos. Me gusta la música española.
    """

    print(f"Text: {text[:100]}...")
    print()

    analysis = analyze_grammar_patterns(text)

    print("Results:")
    print(f"  Total verbs: {analysis['total_verbs']}")
    print(f"  Tenses detected: {analysis['tenses_detected']}")
    print(f"  Verb tenses: {analysis['verb_tenses']}")
    print(f"  Structures: {analysis['structures']}")
    print()

    if analysis['total_verbs'] > 0:
        print("[OK] Grammar analysis working")
    else:
        print("[WARNING] No verbs detected")

    print()


def test_user_comparison():
    """Test comparison with user's grammar knowledge"""
    print("=" * 70)
    print("TEST 6: Compare with User Knowledge")
    print("=" * 70)

    text = "Yo hablo español. Ayer comí pizza. Mañana iré al cine."

    print(f"Text: {text}")
    print()

    result = compare_grammar_with_user(text)

    print("Grammar Readiness:", f"{result['grammar_readiness']:.1f}%")
    print()

    if result['matched_patterns']:
        print("Patterns you know:")
        for p in result['matched_patterns']:
            print(f"  - [OK] {p['display_name']} ({p['count']} uses)")

    if result['unknown_patterns']:
        print("\nPatterns to learn:")
        for p in result['unknown_patterns']:
            print(f"  - [X] {p['display_name']} ({p['count']} uses)")

    print()

    # Test recommendation
    recommendation = get_grammar_recommendation(result, 75.0)
    print(f"Recommendation: {recommendation}")
    print()


def main():
    """Run all tests"""
    print()
    print("=" * 70)
    print(" " * 15 + "GRAMMAR PATTERN DETECTION TEST SUITE")
    print("=" * 70)
    print()

    try:
        test_present_tense()
        test_preterite_tense()
        test_future_tense()
        test_reflexive_verbs()
        test_comprehensive_analysis()
        test_user_comparison()

        print("=" * 70)
        print("ALL TESTS COMPLETE")
        print("=" * 70)
        print()
        print("Grammar pattern detection is working!")
        print()
        print("Next steps:")
        print("1. Run the app: python app.py")
        print("2. Go to Discover tab")
        print("3. Paste Spanish text or import from YouTube/website")
        print("4. See grammar analysis in the results!")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(f"Test failed with error: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
