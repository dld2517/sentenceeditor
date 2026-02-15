#!/usr/bin/env python3
"""
Database Utilities - Centralized database operations
"""

import sqlite3


class Database:
    """Database connection and operations manager"""
    
    def __init__(self, db_path="project_outlines.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize()
    
    def initialize(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS major_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, name)
            );

            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (major_category_id) REFERENCES major_categories(id) ON DELETE CASCADE,
                UNIQUE(major_category_id, name)
            );

            CREATE TABLE IF NOT EXISTS sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subcategory_id INTEGER NOT NULL,
                content TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_major_categories_project ON major_categories(project_id);
            CREATE INDEX IF NOT EXISTS idx_subcategories_major_category ON subcategories(major_category_id);
            CREATE INDEX IF NOT EXISTS idx_sentences_subcategory ON sentences(subcategory_id);
        """)
        self.conn.commit()
        
        # Migration: Add sort_order column to sentences if it doesn't exist
        self._migrate_sort_order()
    
    def _migrate_sort_order(self):
        """Ensure sort_order column exists in sentences table"""
        self.cursor.execute("PRAGMA table_info(sentences)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if 'sort_order' not in columns:
            self.cursor.execute("ALTER TABLE sentences ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")
            self.cursor.execute("""
                UPDATE sentences
                SET sort_order = (
                    SELECT COUNT(*)
                    FROM sentences s2
                    WHERE s2.subcategory_id = sentences.subcategory_id
                    AND s2.id <= sentences.id
                )
            """)
            self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # Project operations
    def create_project(self, name):
        """Create a new project"""
        try:
            self.cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_projects(self):
        """Get all projects ordered by update time"""
        self.cursor.execute("SELECT id, name FROM projects ORDER BY updated_at DESC")
        return self.cursor.fetchall()
    
    def get_project(self, project_id):
        """Get a specific project"""
        self.cursor.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
        return self.cursor.fetchone()
    
    def delete_project(self, project_id):
        """Delete a project and all its data"""
        self.cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
    
    def update_project_timestamp(self, project_id):
        """Update the project's updated_at timestamp"""
        self.cursor.execute(
            "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (project_id,)
        )
        self.conn.commit()
    
    # Major category (heading) operations
    def create_major_category(self, project_id, name):
        """Create a new major category"""
        self.cursor.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM major_categories WHERE project_id = ?",
            (project_id,)
        )
        sort_order = self.cursor.fetchone()[0]
        
        try:
            self.cursor.execute(
                "INSERT INTO major_categories (project_id, name, sort_order) VALUES (?, ?, ?)",
                (project_id, name, sort_order)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_major_categories(self, project_id):
        """Get all major categories for a project"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM major_categories WHERE project_id = ? ORDER BY sort_order",
            (project_id,)
        )
        return self.cursor.fetchall()
    
    def update_major_category_name(self, major_category_id, new_name):
        """Update major category name"""
        try:
            self.cursor.execute(
                "UPDATE major_categories SET name = ? WHERE id = ?",
                (new_name, major_category_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def move_major_category(self, major_category_id, target_project_id, target_sort_order):
        """Move a major category to a different project or position"""
        # Get current info
        self.cursor.execute(
            "SELECT project_id, sort_order FROM major_categories WHERE id = ?",
            (major_category_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return False
        
        source_project_id, source_sort_order = result
        
        # If moving to different project
        if source_project_id != target_project_id:
            # Get max sort_order in target project
            self.cursor.execute(
                "SELECT COALESCE(MAX(sort_order), 0) FROM major_categories WHERE project_id = ?",
                (target_project_id,)
            )
            target_sort_order = self.cursor.fetchone()[0] + 1
            
            # Update the category
            self.cursor.execute(
                "UPDATE major_categories SET project_id = ?, sort_order = ? WHERE id = ?",
                (target_project_id, target_sort_order, major_category_id)
            )
            
            # Reorder source project
            self.cursor.execute(
                "UPDATE major_categories SET sort_order = sort_order - 1 WHERE project_id = ? AND sort_order > ?",
                (source_project_id, source_sort_order)
            )
        else:
            # Moving within same project
            if target_sort_order != source_sort_order:
                if target_sort_order < source_sort_order:
                    # Moving up
                    self.cursor.execute(
                        "UPDATE major_categories SET sort_order = sort_order + 1 WHERE project_id = ? AND sort_order >= ? AND sort_order < ?",
                        (source_project_id, target_sort_order, source_sort_order)
                    )
                else:
                    # Moving down
                    self.cursor.execute(
                        "UPDATE major_categories SET sort_order = sort_order - 1 WHERE project_id = ? AND sort_order > ? AND sort_order <= ?",
                        (source_project_id, source_sort_order, target_sort_order)
                    )
                
                self.cursor.execute(
                    "UPDATE major_categories SET sort_order = ? WHERE id = ?",
                    (target_sort_order, major_category_id)
                )
        
        self.conn.commit()
        return True
    
    # Subcategory (subheading) operations
    def create_subcategory(self, major_category_id, name):
        """Create a new subcategory"""
        # Blank subcategories should come first (sort_order=1)
        if name == "":
            # Check if blank subcategory already exists
            self.cursor.execute(
                "SELECT id FROM subcategories WHERE major_category_id = ? AND name = ''",
                (major_category_id,)
            )
            existing = self.cursor.fetchone()
            if existing:
                return existing[0]
            
            sort_order = 1
            # Shift all existing subcategories down
            self.cursor.execute(
                "UPDATE subcategories SET sort_order = sort_order + 1 WHERE major_category_id = ?",
                (major_category_id,)
            )
        else:
            # Named subcategories go after blank (if any)
            self.cursor.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM subcategories WHERE major_category_id = ?",
                (major_category_id,)
            )
            sort_order = self.cursor.fetchone()[0]
        
        try:
            self.cursor.execute(
                "INSERT INTO subcategories (major_category_id, name, sort_order) VALUES (?, ?, ?)",
                (major_category_id, name, sort_order)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_subcategories(self, major_category_id):
        """Get all subcategories for a major category"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM subcategories WHERE major_category_id = ? ORDER BY sort_order",
            (major_category_id,)
        )
        return self.cursor.fetchall()
    
    def update_subcategory_name(self, subcategory_id, new_name):
        """Update subcategory name"""
        try:
            self.cursor.execute(
                "UPDATE subcategories SET name = ? WHERE id = ?",
                (new_name, subcategory_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def move_subcategory(self, subcategory_id, target_major_category_id, target_sort_order):
        """Move a subcategory to a different major category or position"""
        # Get current info
        self.cursor.execute(
            "SELECT major_category_id, sort_order FROM subcategories WHERE id = ?",
            (subcategory_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return False
        
        source_major_category_id, source_sort_order = result
        
        # If moving to different major category
        if source_major_category_id != target_major_category_id:
            # Get max sort_order in target
            self.cursor.execute(
                "SELECT COALESCE(MAX(sort_order), 0) FROM subcategories WHERE major_category_id = ?",
                (target_major_category_id,)
            )
            target_sort_order = self.cursor.fetchone()[0] + 1
            
            # Update the subcategory
            self.cursor.execute(
                "UPDATE subcategories SET major_category_id = ?, sort_order = ? WHERE id = ?",
                (target_major_category_id, target_sort_order, subcategory_id)
            )
            
            # Reorder source major category
            self.cursor.execute(
                "UPDATE subcategories SET sort_order = sort_order - 1 WHERE major_category_id = ? AND sort_order > ?",
                (source_major_category_id, source_sort_order)
            )
        else:
            # Moving within same major category
            if target_sort_order != source_sort_order:
                if target_sort_order < source_sort_order:
                    # Moving up
                    self.cursor.execute(
                        "UPDATE subcategories SET sort_order = sort_order + 1 WHERE major_category_id = ? AND sort_order >= ? AND sort_order < ?",
                        (source_major_category_id, target_sort_order, source_sort_order)
                    )
                else:
                    # Moving down
                    self.cursor.execute(
                        "UPDATE subcategories SET sort_order = sort_order - 1 WHERE major_category_id = ? AND sort_order > ? AND sort_order <= ?",
                        (source_major_category_id, source_sort_order, target_sort_order)
                    )
                
                self.cursor.execute(
                    "UPDATE subcategories SET sort_order = ? WHERE id = ?",
                    (target_sort_order, subcategory_id)
                )
        
        self.conn.commit()
        return True
    
    # Sentence operations
    def add_sentence(self, subcategory_id, content):
        """Add a new sentence to a subcategory"""
        self.cursor.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM sentences WHERE subcategory_id = ?",
            (subcategory_id,)
        )
        sort_order = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            "INSERT INTO sentences (subcategory_id, content, sort_order) VALUES (?, ?, ?)",
            (subcategory_id, content, sort_order)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_sentences(self, subcategory_id):
        """Get all sentences for a subcategory"""
        self.cursor.execute(
            "SELECT id, content, sort_order FROM sentences WHERE subcategory_id = ? ORDER BY sort_order",
            (subcategory_id,)
        )
        return self.cursor.fetchall()
    
    def update_sentence(self, sentence_id, content):
        """Update a sentence"""
        self.cursor.execute(
            "UPDATE sentences SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, sentence_id)
        )
        self.conn.commit()
    
    def delete_sentence(self, sentence_id):
        """Delete a sentence and reorder remaining sentences"""
        # Get sentence info
        self.cursor.execute(
            "SELECT subcategory_id, sort_order FROM sentences WHERE id = ?",
            (sentence_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return False
        
        subcategory_id, sort_order = result
        
        # Delete the sentence
        self.cursor.execute("DELETE FROM sentences WHERE id = ?", (sentence_id,))
        
        # Reorder remaining sentences
        self.cursor.execute(
            "UPDATE sentences SET sort_order = sort_order - 1 WHERE subcategory_id = ? AND sort_order > ?",
            (subcategory_id, sort_order)
        )
        
        self.conn.commit()
        return True
    
    def move_sentence(self, sentence_id, target_subcategory_id):
        """Move a sentence to a different subcategory"""
        # Get source info
        self.cursor.execute(
            "SELECT subcategory_id, sort_order FROM sentences WHERE id = ?",
            (sentence_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return False
        
        source_subcategory_id, source_sort_order = result
        
        # Get target sort_order
        self.cursor.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM sentences WHERE subcategory_id = ?",
            (target_subcategory_id,)
        )
        target_sort_order = self.cursor.fetchone()[0]
        
        # Move the sentence
        self.cursor.execute(
            "UPDATE sentences SET subcategory_id = ?, sort_order = ? WHERE id = ?",
            (target_subcategory_id, target_sort_order, sentence_id)
        )
        
        # Reorder source subcategory
        self.cursor.execute(
            "UPDATE sentences SET sort_order = sort_order - 1 WHERE subcategory_id = ? AND sort_order > ?",
            (source_subcategory_id, source_sort_order)
        )
        
        self.conn.commit()
        return True
    
    def copy_sentence(self, sentence_id, target_subcategory_id):
        """Copy a sentence to a different subcategory"""
        # Get source sentence
        self.cursor.execute(
            "SELECT content FROM sentences WHERE id = ?",
            (sentence_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return False
        
        content = result[0]
        
        # Add to target
        self.add_sentence(target_subcategory_id, content)
        return True
    
    def insert_sentence(self, target_line_num, content, project_id):
        """Insert a sentence before a specific line number"""
        # Get all lines to find the target
        lines = self.get_all_lines(project_id)
        
        if target_line_num < 1 or target_line_num > len(lines):
            return False
        
        # Get the sentence at target line
        target_sentence = lines[target_line_num - 1]
        subcategory_id = target_sentence[3]  # sc_id
        target_sort_order = target_sentence[-1]  # Last item is sort_order
        
        # Shift sentences down
        self.cursor.execute(
            "UPDATE sentences SET sort_order = sort_order + 1 WHERE subcategory_id = ? AND sort_order >= ?",
            (subcategory_id, target_sort_order)
        )
        
        # Insert new sentence
        self.cursor.execute(
            "INSERT INTO sentences (subcategory_id, content, sort_order) VALUES (?, ?, ?)",
            (subcategory_id, content, target_sort_order)
        )
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_lines(self, project_id):
        """Get all lines (sentences) for a project with full context"""
        self.cursor.execute("""
            SELECT 
                s.id,
                mc.id as mc_id,
                mc.name as major_category,
                sc.id as sc_id,
                sc.name as subcategory,
                s.content,
                mc.sort_order,
                sc.sort_order as sc_order,
                s.sort_order
            FROM sentences s
            JOIN subcategories sc ON s.subcategory_id = sc.id
            JOIN major_categories mc ON sc.major_category_id = mc.id
            WHERE mc.project_id = ?
            ORDER BY mc.sort_order, sc.sort_order, s.sort_order
        """, (project_id,))
        return self.cursor.fetchall()
    
    def get_sentence_by_line_number(self, project_id, line_num):
        """Get a sentence by its line number in the project"""
        lines = self.get_all_lines(project_id)
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return None
