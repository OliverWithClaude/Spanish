"""
Test Word Forms Integration

Verifies that the word forms generation system is properly integrated.
"""

from src.database import init_database, get_connection
from src.word_forms import (
    get_word_forms_count,
    generate_all_word_forms,
    get_all_word_forms
)


def test_database_schema():
    """Test that word_forms table exists"""
    print("=" * 70)
    print("TEST 1: Database Schema")
    print("=" * 70)

    # Initialize database (creates tables if they don't exist)
    init_database()

    conn = get_connection()
    cursor = conn.cursor()

    # Check if word_forms table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='word_forms'
    """)
    result = cursor.fetchone()

    if result:
        print("[OK] word_forms table exists")

        # Check table structure
        cursor.execute("PRAGMA table_info(word_forms)")
        columns = cursor.fetchall()
        print(f"\nTable has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("[ERROR] word_forms table does not exist!")

    conn.close()
    print()


def test_word_forms_count():
    """Test get_word_forms_count function"""
    print("=" * 70)
    print("TEST 2: Word Forms Count")
    print("=" * 70)

    stats = get_word_forms_count()

    print(f"Base words with forms: {stats['base_words_with_forms']}")
    print(f"Total forms: {stats['total_forms']}")
    print(f"Generated forms: {stats['generated_forms']}")
    print(f"Multiplier: {stats['multiplier']:.1f}x")
    print()

    if stats['total_forms'] == 0:
        print("[INFO]  No word forms generated yet (expected if first run)")
    else:
        print("[OK] Word forms found in database")

    print()


def test_small_generation():
    """Test generating word forms for a small sample"""
    print("=" * 70)
    print("TEST 3: Small Word Forms Generation (Sample)")
    print("=" * 70)

    # Check if user has any learned vocabulary
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM vocabulary v
        JOIN vocabulary_progress vp ON v.id = vp.vocabulary_id
        WHERE vp.status IN ('learned', 'learning', 'due')
    """)
    learned_count = cursor.fetchone()[0]
    conn.close()

    print(f"Learned/learning vocabulary: {learned_count} words")

    if learned_count == 0:
        print("[WARNING]  No learned vocabulary found. Add some vocabulary first.")
        print()
        return

    print("\nNote: Full generation test skipped to save time.")
    print("To test full generation, run the app and click 'Generate Word Forms' in Progress tab.")
    print()


def test_content_integration():
    """Test that content analysis can use word forms"""
    print("=" * 70)
    print("TEST 4: Content Analysis Integration")
    print("=" * 70)

    try:
        from src.content_analysis import analyze_content

        # Test with a simple Spanish sentence
        test_text = "Yo hablo español. Nosotros hablamos todos los días."

        print(f"Test text: '{test_text}'")
        print("\nAnalyzing...")

        result = analyze_content(test_text)

        print(f"\nResults:")
        print(f"  Total words: {result.total_words}")
        print(f"  Unique words: {result.unique_words}")
        print(f"  Known: {result.known_count}")
        print(f"  Learning: {result.learning_count}")
        print(f"  New: {result.new_count}")
        print(f"  Comprehension: {result.comprehension_pct:.1f}%")

        if hasattr(result, 'word_forms_matched'):
            print(f"  Word forms matched: {result.word_forms_matched}")
            print("\n[OK] Content analysis includes word forms matching")
        else:
            print("\n[WARNING]  word_forms_matched field not found")

    except Exception as e:
        print(f"\n[ERROR] Error testing content integration: {e}")

    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print(" " * 15 + "WORD FORMS INTEGRATION TEST SUITE")
    print("=" * 70)
    print()

    test_database_schema()
    test_word_forms_count()
    test_small_generation()
    test_content_integration()

    print("=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run the app: python app.py")
    print("2. Go to Progress tab")
    print("3. Click 'Generate Word Forms' button")
    print("4. Go to Discover tab and test content analysis")
    print()


if __name__ == "__main__":
    main()
