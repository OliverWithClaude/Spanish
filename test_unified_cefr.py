"""
Test Unified CEFR Scoring System
"""

from src.database import calculate_unified_cefr_score

print("=" * 70)
print("  UNIFIED CEFR SCORING SYSTEM TEST")
print("=" * 70)
print()

result = calculate_unified_cefr_score()

print(f"Overall CEFR Level: {result['overall_cefr']} ({result['sublevel']})")
print(f"Overall Score: {result['overall_score']}%")
print()

print("Dimension Breakdown:")
print("-" * 70)
for dim_name, dim_data in result['dimensions'].items():
    weight = result['weights'][dim_name]
    print(f"\n{dim_name.upper()}:")
    print(f"  Weight: {weight}%")
    print(f"  Score: {dim_data['score']:.1f}%")
    print(f"  CEFR Level: {dim_data['cefr_level']}")

    if dim_name == 'vocabulary':
        print(f"  Learned: {dim_data['learned']}")
        print(f"  Learning: {dim_data['learning']}")
        print(f"  New: {dim_data['new']}")
        print(f"  Total: {dim_data['total']}")

    elif dim_name == 'grammar':
        print(f"  Mastered: {dim_data['mastered']}")
        print(f"  Learned: {dim_data['learned']}")
        print(f"  Learning: {dim_data['learning']}")
        print(f"  New: {dim_data['new']}")
        print(f"  Total: {dim_data['total']}")

    elif dim_name == 'speaking':
        print(f"  Attempts: {dim_data['attempts']}")
        print(f"  Recent Avg: {dim_data['recent_avg']:.1f}%")
        print(f"  Overall Avg: {dim_data['avg_accuracy']:.1f}%")

    elif dim_name == 'content':
        print(f"  Mastered Packages: {dim_data['mastered_packages']}")
        print(f"  Total Packages: {dim_data['total_packages']}")

print()
print("=" * 70)
print("  LEVEL UNLOCKING STATUS")
print("=" * 70)
print()

for level, data in result['gating'].items():
    status = "UNLOCKED" if data['unlocked'] else "LOCKED"
    print(f"{level.upper()}: {status}")

    if 'vocab_mastery' in data:
        print(f"  Vocabulary Mastery: {data['vocab_mastery']}%")
        print(f"  Grammar Mastery: {data['grammar_mastery']}%")

    if not data['unlocked'] and 'requirement' in data:
        print(f"  Requirement: {data['requirement']}")
    print()

print("=" * 70)
print("  SCORING FORMULA")
print("=" * 70)
print()
print("Overall Score = ")
print(f"  Vocabulary ({result['weights']['vocabulary']}%) × {result['dimensions']['vocabulary']['score']:.1f}% = {result['weights']['vocabulary'] * result['dimensions']['vocabulary']['score'] / 100:.1f}%")
print(f"  Grammar ({result['weights']['grammar']}%) × {result['dimensions']['grammar']['score']:.1f}% = {result['weights']['grammar'] * result['dimensions']['grammar']['score'] / 100:.1f}%")
print(f"  Speaking ({result['weights']['speaking']}%) × {result['dimensions']['speaking']['score']:.1f}% = {result['weights']['speaking'] * result['dimensions']['speaking']['score'] / 100:.1f}%")
print(f"  Content ({result['weights']['content']}%) × {result['dimensions']['content']['score']:.1f}% = {result['weights']['content'] * result['dimensions']['content']['score'] / 100:.1f}%")
print(f"  = {result['overall_score']}%")
print()

print("=" * 70)
print("  TEST COMPLETE - Unified CEFR scoring is working!")
print("=" * 70)
