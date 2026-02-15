#!/usr/bin/env python3
"""
Outline Editor - Modern word-processor style interface for hierarchical outlines
"""

import sqlite3
import os
import sys
import string
import re
import tty
import termios
from project_state import get_active_project, set_active_project
from inline_editor import edit_line_inline
from help import show_outline_editor_help

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'


class OutlineEditor:
    def __init__(self, db_path: str = "project_outlines.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.current_project_id = None
        self.initialize_database()
    
    def initialize_database(self):
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
        self.cursor.execute("PRAGMA table_info(sentences)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if 'sort_order' not in columns:
            # Add the column
            self.cursor.execute("ALTER TABLE sentences ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")
            # Set sort_order based on current ID order for existing sentences
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
    
    def create_project(self, name: str):
        """Create a new project"""
        try:
            self.cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def list_projects(self):
        """List all projects"""
        self.cursor.execute("SELECT id, name FROM projects ORDER BY updated_at DESC")
        return self.cursor.fetchall()
    
    def get_major_categories(self, project_id: int):
        """Get all major categories for a project in order"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM major_categories WHERE project_id = ? ORDER BY sort_order",
            (project_id,)
        )
        return self.cursor.fetchall()
    
    def create_major_category(self, project_id: int, name: str):
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
    
    def update_major_category_name(self, major_category_id: int, new_name: str):
        """Update the name of a major category"""
        try:
            self.cursor.execute(
                "UPDATE major_categories SET name = ? WHERE id = ?",
                (new_name, major_category_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_subcategories(self, major_category_id: int):
        """Get all subcategories for a major category"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM subcategories WHERE major_category_id = ? ORDER BY sort_order",
            (major_category_id,)
        )
        return self.cursor.fetchall()
    
    def create_subcategory(self, major_category_id: int, name: str):
        """Create a new subcategory (subheading)"""
        # Blank subcategories should come first (sort_order=1)
        # Named subcategories come after
        if name == "":
            # Check if blank subcategory already exists
            self.cursor.execute(
                "SELECT id FROM subcategories WHERE major_category_id = ? AND name = ''",
                (major_category_id,)
            )
            existing = self.cursor.fetchone()
            if existing:
                return existing[0]
            
            # Put blank subcategory first
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
    
    def update_subcategory_name(self, subcategory_id: int, new_name: str):
        """Update the name of a subcategory"""
        try:
            self.cursor.execute(
                "UPDATE subcategories SET name = ? WHERE id = ?",
                (new_name, subcategory_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def add_sentence(self, subcategory_id: int, content: str):
        """Add a new sentence to a subcategory"""
        # Get next sort_order
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
    
    def get_all_lines(self, project_id: int):
        """Get all lines with line numbers"""
        self.cursor.execute("""
            SELECT 
                s.id,
                mc.id as mc_id,
                mc.name as major_category,
                sc.id as sc_id,
                sc.name as subcategory,
                s.content,
                mc.sort_order,
                sc.sort_order as sc_order
            FROM sentences s
            JOIN subcategories sc ON s.subcategory_id = sc.id
            JOIN major_categories mc ON sc.major_category_id = mc.id
            WHERE mc.project_id = ?
            ORDER BY mc.sort_order, sc.sort_order, s.sort_order
        """, (project_id,))
        return self.cursor.fetchall()
    
    def update_sentence(self, sentence_id: int, content: str):
        """Update a sentence by ID"""
        self.cursor.execute(
            "UPDATE sentences SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, sentence_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_sentence(self, sentence_id: int):
        """Delete a sentence by ID"""
        self.cursor.execute("DELETE FROM sentences WHERE id = ?", (sentence_id,))
        self.conn.commit()
        return True
    
    def insert_sentence_before(self, target_sentence_id: int, content: str):
        """Insert a new sentence before the target sentence"""
        # Get target sentence info
        self.cursor.execute(
            "SELECT subcategory_id, sort_order FROM sentences WHERE id = ?",
            (target_sentence_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            return None
        
        subcategory_id, target_sort_order = result
        
        # Shift all sentences at or after target position down by 1
        self.cursor.execute(
            "UPDATE sentences SET sort_order = sort_order + 1 WHERE subcategory_id = ? AND sort_order >= ?",
            (subcategory_id, target_sort_order)
        )
        
        # Insert new sentence at target position
        self.cursor.execute(
            "INSERT INTO sentences (subcategory_id, content, sort_order) VALUES (?, ?, ?)",
            (subcategory_id, content, target_sort_order)
        )
        
        self.conn.commit()
        return self.cursor.lastrowid


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_terminal_size():
    """Get terminal size (rows, columns)"""
    try:
        size = os.get_terminal_size()
        return size.lines, size.columns
    except:
        return 24, 80


def getch():
    """Get a single character from stdin"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def print_command_bar(current_heading_name=None, heading_key=None, current_subheading_name=None, subheading_key=None):
    """Print command bar at bottom of screen"""
    rows, cols = get_terminal_size()
    
    commands = [
        ("h", "a <name>", "heading"),
        ("h", "a1 <name>", "subheading"),
        ("+", " <text>", "add"),
        ("i", " <#> <text>", "insert"),
        ("e", " <#>", "edit"),
        ("d", " <#>", "delete"),
        ("@", "a", "toggle"),
        ("p", "", "refresh"),
        ("F1", "", "help"),
        ("q", "", "quit")
    ]
    
    cmd_parts = []
    for prefix, suffix, desc in commands:
        cmd_parts.append(f"{Colors.BRIGHT_YELLOW}{prefix}{suffix}{Colors.RESET}:{desc}")
    
    cmd_line = "  ".join(cmd_parts)
    
    print(f"\n{Colors.BRIGHT_BLACK}" + "─" * cols + f"{Colors.RESET}")
    
    # Build context line showing current heading and/or subheading
    context_parts = []
    if current_heading_name and heading_key:
        context_parts.append(f"Heading: {Colors.BRIGHT_BLUE}[{heading_key}]{Colors.RESET} {Colors.BRIGHT_WHITE}{current_heading_name}{Colors.RESET}")
    
    if current_subheading_name and subheading_key:
        context_parts.append(f"Subheading: {Colors.CYAN}[{subheading_key}]{Colors.RESET} {Colors.BRIGHT_CYAN}{current_subheading_name}{Colors.RESET}")
    
    if context_parts:
        context = " | ".join(context_parts)
    else:
        context = f"{Colors.DIM}No heading selected{Colors.RESET}"
    
    print(f"{context}")
    print(f"{Colors.BRIGHT_BLUE}{cmd_line}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}" + "─" * cols + f"{Colors.RESET}")


def print_outline(editor, project_id, collapsed_headings=None):
    """Print the entire outline with headings, subheadings, and sentences in unified view"""
    if collapsed_headings is None:
        collapsed_headings = set()
    major_categories = editor.get_major_categories(project_id)
    
    if not major_categories:
        print(f"\n{Colors.DIM}(No headings yet - use 'ha <heading name>' to create first heading){Colors.RESET}\n")
        return {}, {}
    
    heading_map = {}
    subheading_map = {}
    
    # Build maps
    for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
        letter = string.ascii_lowercase[idx] if idx < 26 else f"#{idx}"
        heading_map[letter] = (mc_id, mc_name)
        
        subcategories = editor.get_subcategories(mc_id)
        for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
            subheading_key = f"{letter}{sub_idx}"
            subheading_map[subheading_key] = (sc_id, sc_name, mc_id)
    
    # Get all lines
    lines = editor.get_all_lines(project_id)
    
    # Build a structure: {mc_id: {sc_id: [sentences]}}
    structure = {}
    for sentence_id, mc_id, major_cat, sc_id, subcat, content, mc_order, sc_order in lines:
        if mc_id not in structure:
            structure[mc_id] = {}
        if sc_id not in structure[mc_id]:
            structure[mc_id][sc_id] = []
        structure[mc_id][sc_id].append((sentence_id, content))
    
    # Print unified view
    print()
    line_num = 1
    
    for idx, (mc_id, mc_name, mc_order) in enumerate(major_categories):
        letter = string.ascii_lowercase[idx] if idx < 26 else f"#{idx}"
        
        # Check if heading is collapsed
        is_collapsed = letter in collapsed_headings
        
        # Print heading with collapse indicator
        collapse_indicator = f"{Colors.DIM}[+]{Colors.RESET}" if is_collapsed else f"{Colors.DIM}[-]{Colors.RESET}"
        print(f"{collapse_indicator} {Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{mc_name}{Colors.RESET}")
        
        # Skip content if collapsed
        if is_collapsed:
            print()
            continue
        
        # Get subcategories for this heading
        subcategories = editor.get_subcategories(mc_id)
        
        # Print subheadings and their sentences
        for sub_idx, (sc_id, sc_name, sc_order) in enumerate(subcategories, 1):
            subheading_key = f"{letter}{sub_idx}"
            
            # If subcategory has a name, show it
            if sc_name:
                print(f"  {Colors.CYAN}[{subheading_key}]{Colors.RESET} {Colors.BRIGHT_CYAN}{sc_name}{Colors.RESET}")
            
            # Print sentences under this subcategory
            if mc_id in structure and sc_id in structure[mc_id]:
                for sentence_id, content in structure[mc_id][sc_id]:
                    print(f"    {Colors.GREEN}[{line_num}]{Colors.RESET} {Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
                    line_num += 1
        
        print()  # Blank line between headings
    
    if line_num == 1:
        print(f"{Colors.DIM}(No content yet - use '+ <text>' to add sentences){Colors.RESET}\n")
    
    return heading_map, subheading_map


def main():
    """Main application loop"""
    editor = OutlineEditor()
    project_id = None
    
    # Check for active project
    active_id, active_name = get_active_project()
    
    if active_id:
        # Verify project still exists
        editor.cursor.execute("SELECT id, name FROM projects WHERE id = ?", (active_id,))
        result = editor.cursor.fetchone()
        if result:
            project_id = active_id
            print(f"\n{Colors.GREEN}✓{Colors.RESET} Using active project: {Colors.BRIGHT_CYAN}{active_name}{Colors.RESET}")
            import time
            time.sleep(1)
        else:
            active_id = None
    
    if not active_id:
        # Project selection/creation
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  OUTLINE EDITOR  {Colors.RESET}\n")
        
        projects = editor.list_projects()
        
        if projects:
            print(f"{Colors.BRIGHT_CYAN}Existing Projects:{Colors.RESET}")
            for idx, (proj_id, proj_name) in enumerate(projects, 1):
                print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
            
            print(f"\n  {Colors.BRIGHT_YELLOW}N{Colors.RESET}. Create New Project")
            choice = input(f"\n{Colors.BRIGHT_GREEN}Select project (number or N):{Colors.RESET} ").strip().upper()
            
            if choice == 'N':
                name = input(f"{Colors.BRIGHT_GREEN}Enter project name:{Colors.RESET} ").strip()
                if name:
                    project_id = editor.create_project(name)
                    if not project_id:
                        print(f"{Colors.RED}Error:{Colors.RESET} Project already exists.")
                        editor.close()
                        return
                    set_active_project(project_id, name)
                else:
                    print(f"{Colors.RED}Error:{Colors.RESET} Project name cannot be empty.")
                    editor.close()
                    return
            else:
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(projects):
                        project_id, project_name = projects[idx - 1]
                        set_active_project(project_id, project_name)
                    else:
                        print(f"{Colors.RED}Error:{Colors.RESET} Invalid selection.")
                        editor.close()
                        return
                except ValueError:
                    print(f"{Colors.RED}Error:{Colors.RESET} Invalid input.")
                    editor.close()
                    return
        else:
            name = input(f"\n{Colors.BRIGHT_GREEN}Enter project name:{Colors.RESET} ").strip()
            if name:
                project_id = editor.create_project(name)
                if not project_id:
                    print(f"{Colors.RED}Error:{Colors.RESET} Project already exists.")
                    editor.close()
                    return
                set_active_project(project_id, name)
            else:
                print(f"{Colors.RED}Error:{Colors.RESET} Project name cannot be empty.")
                editor.close()
                return
    
    # Main editor loop
    current_major_category_id = None
    current_major_category_name = None
    current_subcategory_id = None
    current_subcategory_name = None
    collapsed_headings = set()  # Track which headings are collapsed
    
    while True:
        clear_screen()
        
        editor.cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,))
        project_name = editor.cursor.fetchone()[0]
        
        rows, cols = get_terminal_size()
        
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")
        header_text = f"  PROJECT: {project_name}"
        padding = " " * (cols - len(header_text))
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}{header_text}{padding}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")
        
        heading_map, subheading_map = print_outline(editor, project_id, collapsed_headings)
        
        # Find current heading key
        current_heading_key = None
        if current_major_category_id:
            for key, (mc_id, mc_name) in heading_map.items():
                if mc_id == current_major_category_id:
                    current_heading_key = key
                    break
        
        # Find current subheading key
        current_subheading_key = None
        if current_subcategory_id:
            for key, (sc_id, sc_name, mc_id) in subheading_map.items():
                if sc_id == current_subcategory_id:
                    current_subheading_key = key
                    break
        
        print_command_bar(current_major_category_name, current_heading_key, current_subcategory_name, current_subheading_key)
        
        # Check for F1 key first
        print(f"{Colors.BRIGHT_GREEN}> {Colors.RESET}", end='', flush=True)
        ch = getch()
        
        # Check if it's escape sequence (F1 starts with ESC)
        if ch == '\x1b':
            # Read next characters
            ch2 = getch()
            ch3 = getch()
            
            full_seq = ch + ch2 + ch3
            
            # Check for F1 (ESC O P)
            if full_seq == '\x1bOP':
                print()  # New line after prompt
                show_outline_editor_help()
                continue
            else:
                # Not F1, treat as regular input
                print(full_seq, end='', flush=True)
                rest_of_line = input()
                cmd = (full_seq + rest_of_line).strip()
        else:
            # Regular character, read the rest of the line
            print(ch, end='', flush=True)
            rest_of_line = input()
            cmd = (ch + rest_of_line).strip()
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        if command == 'q':
            break
        
        elif command == '@':
            # Toggle collapse/expand for heading
            match = re.match(r'^@([a-zA-Z])$', cmd, re.IGNORECASE)
            if not match:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid format. Use '@a' to toggle heading a")
                continue
            
            letter = match.group(1).lower()
            
            if letter not in heading_map:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Heading [{letter}] doesn't exist")
                continue
            
            # Toggle collapse state
            if letter in collapsed_headings:
                collapsed_headings.remove(letter)
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Heading [{letter}] expanded")
            else:
                collapsed_headings.add(letter)
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Heading [{letter}] collapsed")
        
        elif command == 'h':
            match = re.match(r'^h([a-zA-Z])(\d*)(.*)$', cmd, re.IGNORECASE)
            
            if not match:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid format. Use 'ha <name>' for heading or 'ha1 <name>' for subheading")
                continue
            
            letter = match.group(1).lower()
            number = match.group(2)
            rest = match.group(3).strip()
            
            if number:
                subheading_key = f"{letter}{number}"
                
                if letter not in heading_map:
                    print(f"\n{Colors.RED}Error:{Colors.RESET} Heading [{letter}] doesn't exist. Create it first with 'h{letter} <name>'")
                    continue
                
                mc_id, mc_name = heading_map[letter]
                
                if subheading_key in subheading_map:
                    sc_id, sc_name, parent_mc_id = subheading_map[subheading_key]
                    
                    if rest:
                        if editor.update_subcategory_name(sc_id, rest):
                            print(f"\n{Colors.GREEN}✓{Colors.RESET} Subheading [{subheading_key}] renamed to: {rest}")
                            current_subcategory_id = sc_id
                            current_subcategory_name = rest
                        else:
                            print(f"\n{Colors.RED}Error:{Colors.RESET} Could not rename subheading")
                    else:
                        current_subcategory_id = sc_id
                        current_subcategory_name = sc_name
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Current subheading set to: [{subheading_key}] {sc_name}")
                else:
                    if not rest:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Subheading name required. Example: h{subheading_key} Your Subheading Name")
                        continue
                    
                    existing_subs = [k for k in subheading_map.keys() if k.startswith(letter)]
                    expected_num = len(existing_subs) + 1
                    
                    if int(number) != expected_num:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Next subheading should be '{letter}{expected_num}'. Use 'h{letter}{expected_num} <name>' to create it.")
                        continue
                    
                    sc_id = editor.create_subcategory(mc_id, rest)
                    if sc_id:
                        current_subcategory_id = sc_id
                        current_subcategory_name = rest
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Subheading [{subheading_key}] created: {rest}")
                    else:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Could not create subheading")
            else:
                # Heading command without number (e.g., ha or ha <text>)
                if letter in heading_map:
                    # Heading exists
                    mc_id, mc_name = heading_map[letter]
                    
                    if rest:
                        # Text provided - rename the heading
                        if editor.update_major_category_name(mc_id, rest):
                            current_major_category_id = mc_id
                            current_major_category_name = rest
                            # Clear subcategory selection when working with heading
                            current_subcategory_id = None
                            current_subcategory_name = None
                            print(f"\n{Colors.GREEN}✓{Colors.RESET} Heading [{letter}] renamed to: {rest}")
                        else:
                            print(f"\n{Colors.RED}Error:{Colors.RESET} Could not rename heading (name may already exist)")
                    else:
                        # No text - just select the heading
                        current_major_category_id = mc_id
                        current_major_category_name = mc_name
                        # Clear subcategory selection when selecting just heading
                        current_subcategory_id = None
                        current_subcategory_name = None
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Selected heading [{letter}] {mc_name}")
                        print(f"{Colors.DIM}Use '+' to add sentence, or 'h{letter}1 <name>' to create subheading{Colors.RESET}")
                else:
                    # Heading doesn't exist - must provide text to create it
                    if not rest:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Heading [{letter}] doesn't exist. Use 'h{letter} <name>' to create it.")
                        continue
                    
                    # Check if this is the next heading in sequence
                    expected_letter = string.ascii_lowercase[len(heading_map)] if len(heading_map) < 26 else f"#{len(heading_map)}"
                    
                    if letter != expected_letter:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Next heading should be '{expected_letter}'. Use 'h{expected_letter} <name>' to create it.")
                        continue
                    
                    # Create new heading
                    mc_id = editor.create_major_category(project_id, rest)
                    if mc_id:
                        current_major_category_id = mc_id
                        current_major_category_name = rest
                        # Clear subcategory selection for new heading
                        current_subcategory_id = None
                        current_subcategory_name = None
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Heading [{letter}] created: {rest}")
                        print(f"{Colors.DIM}Use '+' to add sentence, or 'h{letter}1 <name>' to create subheading{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Could not create heading (name may already exist)")
        
        elif command == '+':
            if len(cmd) < 2 or not cmd[1:].strip():
                print(f"\n{Colors.RED}Error:{Colors.RESET} Sentence text required. Example: + This is my sentence")
                continue
            
            sentence_text = cmd[1:].strip()
            
            # If no subcategory selected, check if we have a heading selected
            if not current_subcategory_id:
                # Try to find or create a blank subcategory under the current heading
                if current_major_category_id:
                    # Look for existing blank subcategory
                    subcats = editor.get_subcategories(current_major_category_id)
                    blank_subcat_id = None
                    for sc_id, sc_name, _ in subcats:
                        if sc_name == "":
                            blank_subcat_id = sc_id
                            break
                    
                    # Create blank subcategory if it doesn't exist
                    if not blank_subcat_id:
                        blank_subcat_id = editor.create_subcategory(current_major_category_id, "")
                    
                    if blank_subcat_id:
                        editor.add_sentence(blank_subcat_id, sentence_text)
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence added to topic")
                    else:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Could not create subcategory")
                else:
                    print(f"\n{Colors.RED}Error:{Colors.RESET} Select a heading first (e.g., 'ha' or 'ha Topic Name')")
            else:
                editor.add_sentence(current_subcategory_id, sentence_text)
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence added")
        
        elif command == 'i':
            # Insert command: i <line#> <text>
            parts = cmd[1:].strip().split(None, 1)
            if len(parts) < 2:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Usage: i <line#> <text>. Example: i 3 New sentence")
                continue
            
            try:
                line_num = int(parts[0])
                new_content = parts[1]
                
                lines = editor.get_all_lines(project_id)
                if 1 <= line_num <= len(lines):
                    target_sentence_id = lines[line_num - 1][0]
                    new_id = editor.insert_sentence_before(target_sentence_id, new_content)
                    if new_id:
                        print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence inserted before line {line_num}")
                    else:
                        print(f"\n{Colors.RED}Error:{Colors.RESET} Could not insert sentence")
                else:
                    print(f"\n{Colors.RED}Error:{Colors.RESET} Line {line_num} does not exist")
            except ValueError:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid line number. Example: i 3 New sentence")
        
        elif command == 'e':
            try:
                line_num = int(cmd[1:].strip())
                
                lines = editor.get_all_lines(project_id)
                if 1 <= line_num <= len(lines):
                    sentence_id = lines[line_num - 1][0]
                    current_text = lines[line_num - 1][5]  # content is at index 5
                    
                    # Use inline vim-style editor
                    new_text, cancelled = edit_line_inline(line_num, current_text)
                    
                    if not cancelled and new_text != current_text:
                        editor.update_sentence(sentence_id, new_text)
                else:
                    print(f"\n{Colors.RED}Error:{Colors.RESET} Line {line_num} does not exist")
            except ValueError:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid line number. Example: e 3")
        
        elif command == 'd':
            try:
                line_num = int(cmd[1:].strip())
                
                lines = editor.get_all_lines(project_id)
                if 1 <= line_num <= len(lines):
                    sentence_id = lines[line_num - 1][0]
                    editor.delete_sentence(sentence_id)
                    print(f"\n{Colors.GREEN}✓{Colors.RESET} Line {line_num} deleted")
                else:
                    print(f"\n{Colors.RED}Error:{Colors.RESET} Line {line_num} does not exist")
            except ValueError:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid line number")
        
        elif command == 'p':
            continue
        
        else:
            print(f"\n{Colors.RED}Error:{Colors.RESET} Unknown command: {command}")
    
    editor.close()
    print(f"\n{Colors.BRIGHT_CYAN}Goodbye!{Colors.RESET}\n")


def run_outline_editor():
    """Wrapper function for compatibility"""
    main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_CYAN}Exiting...{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal Error:{Colors.RESET} {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")
