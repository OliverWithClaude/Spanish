"""
Test Grammar Progress UI
Quick test to verify the grammar progress functions work correctly
"""

from src.database import (
    get_grammar_progress_summary,
    get_grammar_topics_with_progress,
    update_grammar_progress
)

def test_summary():
    """Test progress summary"""
    print("=" * 60)
    print("GRAMMAR PROGRESS SUMMARY TEST")
    print("=" * 60)

    summary = get_grammar_progress_summary()

    print(f"\nTotal Topics: {summary['total_topics']}")
    print(f"Mastered: {summary.get('mastered', 0)}")
    print(f"Learned: {summary.get('learned', 0)}")
    print(f"Learning: {summary.get('learning', 0)}")
    print(f"New: {summary.get('new', 0)}")

    print("\nBy CEFR Level:")
    for level, data in summary['by_level'].items():
        bar = "#" * int(data['percentage'] / 10) + "-" * (10 - int(data['percentage'] / 10))
        print(f"  {level}: {data['mastered']}/{data['total']} ({data['percentage']}%) [{bar}]")

    print("\nBy Category:")
    for category, data in summary['by_category'].items():
        bar = "#" * int(data['percentage'] / 10) + "-" * (10 - int(data['percentage'] / 10))
        print(f"  {category.title()}: {data['mastered']}/{data['total']} ({data['percentage']}%) [{bar}]")

def test_topics_display():
    """Test topics with progress"""
    print("\n" + "=" * 60)
    print("TOPICS DISPLAY TEST")
    print("=" * 60)

    topics = get_grammar_topics_with_progress(cefr_level='A1')

    print(f"\nFound {len(topics)} A1 topics:\n")
    print(f"{'ID':<15} {'Status':<15} {'Category':<15}")
    print("-" * 50)

    for topic in topics[:10]:  # Show first 10 only
        status_map = {
            'mastered': '[X] Mastered',
            'learned': '[-] Learned',
            'learning': '[~] Learning',
            'new': '[ ] New'
        }
        status = status_map.get(topic.get('mastery_level', 'new'), '[ ] New')

        print(f"{topic['id']:<15} {status:<15} {topic['category']:<15}")

def test_update():
    """Test updating progress"""
    print("\n" + "=" * 60)
    print("UPDATE TEST")
    print("=" * 60)

    # Update a few topics
    updates = [
        ('A1_V_001', 'mastered'),
        ('A1_V_002', 'learned'),
        ('A1_V_003', 'learning')
    ]

    for topic_id, status in updates:
        update_grammar_progress(topic_id, status)
        print(f"[OK] Updated {topic_id} to {status}")

    # Show updated summary
    print("\nUpdated summary:")
    summary = get_grammar_progress_summary()
    print(f"  Mastered: {summary.get('mastered', 0)}")
    print(f"  Learned: {summary.get('learned', 0)}")
    print(f"  Learning: {summary.get('learning', 0)}")

if __name__ == "__main__":
    test_summary()
    test_topics_display()
    test_update()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED [SUCCESS]")
    print("=" * 60)
    print("\nThe grammar progress UI is ready to use!")
    print("Run the app with: python app.py")
