#!/usr/bin/env python3
"""
Database Migration Script
Removes UNIQUE constraints from major_categories and subcategories tables
"""

import sqlite3
import shutil
from datetime import datetime

def migrate_database(db_path="project_outlines.db"):
    """Migrate database to remove UNIQUE constraints"""
    
    # Create backup
    backup_path = f"{db_path.rsplit('.', 1)[0]}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting migration...")
    
    try:
        # Step 1: Recreate major_categories table without UNIQUE constraint
        print("  Migrating major_categories table...")
        
        cursor.execute("""
            CREATE TABLE major_categories_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO major_categories_new (id, project_id, name, sort_order, created_at)
            SELECT id, project_id, name, sort_order, created_at
            FROM major_categories
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE major_categories")
        cursor.execute("ALTER TABLE major_categories_new RENAME TO major_categories")
        
        print("    ✓ major_categories migrated")
        
        # Step 2: Recreate subcategories table without UNIQUE constraint
        print("  Migrating subcategories table...")
        
        cursor.execute("""
            CREATE TABLE subcategories_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (major_category_id) REFERENCES major_categories(id) ON DELETE CASCADE
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO subcategories_new (id, major_category_id, name, sort_order, created_at)
            SELECT id, major_category_id, name, sort_order, created_at
            FROM subcategories
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE subcategories")
        cursor.execute("ALTER TABLE subcategories_new RENAME TO subcategories")
        
        print("    ✓ subcategories migrated")
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        print(f"  Backup saved to: {backup_path}")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print(f"  Restoring from backup: {backup_path}")
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("  Database restored from backup")
        return False
    
    finally:
        conn.close()
    
    return True


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "project_outlines.db"
    
    print(f"Database Migration Tool")
    print(f"Target database: {db_path}\n")
    
    confirm = input("This will modify your database. Continue? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        success = migrate_database(db_path)
        if success:
            print("\nYou can now use duplicate heading names in your projects!")
        sys.exit(0 if success else 1)
    else:
        print("Migration cancelled.")
        sys.exit(0)
