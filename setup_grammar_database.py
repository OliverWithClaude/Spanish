"""
Setup Grammar Tracking Database
Phase 1: Create tables and import grammar taxonomy
"""
import sqlite3
import json
import os
from pathlib import Path

# Paths
DB_PATH = "data/hablaconmigo.db"
SCHEMA_PATH = "IMPLEMENTATION_SCHEMA.sql"
TAXONOMY_PATH = "SPANISH_GRAMMAR_TAXONOMY.json"

def drop_existing_tables(conn):
    """Drop existing grammar tables if they exist"""
    print("[*] Dropping existing grammar tables (if any)...")

    cursor = conn.cursor()
    tables = [
        'grammar_practice_log',
        'word_forms',
        'grammar_coverage',
        'grammar_user_progress',
        'morphology_rules',
        'grammar_dependencies',
        'grammar_topics'
    ]

    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            cursor.execute(f"DROP INDEX IF EXISTS idx_{table}_*")
        except:
            pass

    conn.commit()
    print("  [OK] Cleanup complete\n")

def execute_schema(conn):
    """Execute SQL schema to create tables"""
    print("[*] Creating grammar tables...")

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Use executescript to handle multi-line statements properly
    try:
        conn.executescript(schema_sql)
        print("  [OK] Schema executed successfully")
    except sqlite3.Error as e:
        print(f"  [ERROR] Schema execution failed: {e}")
        raise

    conn.commit()
    print("[SUCCESS] Schema created successfully\n")

def import_taxonomy(conn):
    """Import grammar taxonomy from JSON"""
    print("[*] Importing grammar taxonomy...")

    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)

    cursor = conn.cursor()

    topic_count = 0
    dependency_count = 0

    # Process each CEFR level
    for level in ['A1', 'A2', 'B1']:
        if level not in taxonomy:
            continue

        print(f"\n  Processing {level} topics...")

        # Process each category
        for category, subcategories in taxonomy[level].items():
            if not isinstance(subcategories, dict):
                continue

            # Process each subcategory
            for subcategory, topics in subcategories.items():
                if not isinstance(topics, dict):
                    continue

                # Process each topic
                for topic_key, topic_data in topics.items():
                    if not isinstance(topic_data, dict) or 'id' not in topic_data:
                        continue

                    # Insert topic
                    applies_to_pos_val = topic_data.get('applies_to_pos', [])
                    if isinstance(applies_to_pos_val, list):
                        applies_to_pos_str = ','.join(applies_to_pos_val)
                    else:
                        applies_to_pos_str = str(applies_to_pos_val) if applies_to_pos_val else ''

                    # Convert morphological_rule to string if it's a dict
                    morphological_rule_val = topic_data.get('morphological_rule', '')
                    if isinstance(morphological_rule_val, dict):
                        morphological_rule_str = json.dumps(morphological_rule_val)
                    else:
                        morphological_rule_str = str(morphological_rule_val) if morphological_rule_val else ''

                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO grammar_topics (
                                id, title, cefr_level, cefr_sublevel,
                                category, subcategory,
                                morphological_rule, applies_to_pos, multiplier,
                                difficulty, frequency, high_priority,
                                description, examples_json, notes
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            topic_data['id'],
                            topic_data.get('title', ''),
                            topic_data.get('cefr_level', level),
                            topic_data.get('cefr_sublevel', ''),
                            topic_data.get('category', category),
                            topic_data.get('subcategory', subcategory),
                            morphological_rule_str,
                            applies_to_pos_str,
                            topic_data.get('multiplier', 1),
                            topic_data.get('difficulty', 'medium'),
                            topic_data.get('frequency', 'medium'),
                            1 if topic_data.get('high_priority', False) else 0,
                            topic_data.get('description', ''),
                            json.dumps(topic_data.get('examples', {})),
                            topic_data.get('note', topic_data.get('notes', ''))
                        ))
                        topic_count += 1
                    except Exception as e:
                        print(f"  [ERROR] Failed to insert topic {topic_data.get('id', 'unknown')}: {e}")
                        print(f"          Topic data: {topic_data}")
                        raise

                    # Insert dependencies
                    for prereq_id in topic_data.get('prerequisites', []):
                        cursor.execute("""
                            INSERT OR IGNORE INTO grammar_dependencies (
                                topic_id, prerequisite_id, dependency_type
                            ) VALUES (?, ?, 'required')
                        """, (topic_data['id'], prereq_id))
                        dependency_count += 1

    conn.commit()
    print(f"\n[SUCCESS] Imported {topic_count} topics and {dependency_count} dependencies\n")

    return topic_count, dependency_count

def verify_import(conn):
    """Verify the import was successful"""
    print("[*] Verifying import...")

    cursor = conn.cursor()

    # Count topics by level
    cursor.execute("""
        SELECT cefr_level, COUNT(*)
        FROM grammar_topics
        GROUP BY cefr_level
        ORDER BY cefr_level
    """)

    print("\n  Topics by CEFR level:")
    total = 0
    for level, count in cursor.fetchall():
        print(f"    {level}: {count} topics")
        total += count
    print(f"    TOTAL: {total} topics")

    # Count dependencies
    cursor.execute("SELECT COUNT(*) FROM grammar_dependencies")
    dep_count = cursor.fetchone()[0]
    print(f"\n  Total dependencies: {dep_count}")

    # Show bottleneck topics (most prerequisites)
    cursor.execute("""
        SELECT
            gt.id,
            gt.title,
            COUNT(gd.prerequisite_id) as prereq_count
        FROM grammar_topics gt
        LEFT JOIN grammar_dependencies gd ON gt.id = gd.topic_id
        GROUP BY gt.id
        HAVING prereq_count > 0
        ORDER BY prereq_count DESC
        LIMIT 5
    """)

    print("\n  Topics with most prerequisites (need most learning):")
    for topic_id, title, count in cursor.fetchall():
        # Remove Unicode characters for console compatibility
        title_clean = title.encode('ascii', 'ignore').decode('ascii')
        print(f"    {topic_id}: {title_clean} ({count} prerequisites)")

    # Show enabling topics (unlock most others)
    cursor.execute("""
        SELECT
            gt.id,
            gt.title,
            COUNT(gd.topic_id) as enables_count
        FROM grammar_topics gt
        LEFT JOIN grammar_dependencies gd ON gt.id = gd.prerequisite_id
        GROUP BY gt.id
        HAVING enables_count > 0
        ORDER BY enables_count DESC
        LIMIT 5
    """)

    print("\n  Topics that unlock the most (bottlenecks):")
    for topic_id, title, count in cursor.fetchall():
        # Remove Unicode characters for console compatibility
        title_clean = title.encode('ascii', 'ignore').decode('ascii')
        print(f"    {topic_id}: {title_clean} (unlocks {count} topics)")

    print("\n[SUCCESS] Verification complete!\n")

def main():
    """Main setup function"""
    print("="*70)
    print("  GRAMMAR DATABASE SETUP - PHASE 1")
    print("="*70)
    print()

    # Check files exist
    if not os.path.exists(SCHEMA_PATH):
        print(f"[ERROR] Schema file not found: {SCHEMA_PATH}")
        return

    if not os.path.exists(TAXONOMY_PATH):
        print(f"[ERROR] Taxonomy file not found: {TAXONOMY_PATH}")
        return

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Connect to database
    print(f"[*] Connecting to database: {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Step 0: Drop existing tables
        drop_existing_tables(conn)

        # Step 1: Create tables
        execute_schema(conn)

        # Step 2: Import taxonomy
        import_taxonomy(conn)

        # Step 3: Verify
        verify_import(conn)

        print("="*70)
        print("  [SUCCESS] PHASE 1 COMPLETE - Grammar database ready!")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Review the imported topics in the database")
        print("  2. Test queries to find topics by level, category, etc.")
        print("  3. Proceed to Phase 2: Word Forms Generation")
        print()

    except Exception as e:
        print(f"\n[ERROR] Error during setup: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

if __name__ == "__main__":
    main()
