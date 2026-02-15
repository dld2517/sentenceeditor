#!/usr/bin/env python3
"""
Sentence Maintenance Module
View, copy, and move sentences between projects with collapsible views and paging
"""

import sqlite3
import os
import re
import string
import sys
import tty
import termios
from help import show_sentence_maintenance_help


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    BG_BLUE = "\033[44m"


def get_terminal_size():
    """Get terminal size"""
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
        return int(rows), int(cols)
    except:
        return 24, 80


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def getch():
    """Get a single character from stdin without echo"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # Check for escape sequences (like F1)
        if ch == '\x1b':
            # Read the next two characters
            ch2 = sys.stdin.read(1)
            if ch2 == 'O':
                ch3 = sys.stdin.read(1)
                return '\x1b' + ch2 + ch3
            elif ch2 == '[':
                ch3 = sys.stdin.read(1)
                return '\x1b' + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class SentenceMaintenance:
    def __init__(self, db_path="project_outlines.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def get_all_projects(self):
        """Get all projects"""
        self.cursor.execute("SELECT id, name FROM projects ORDER BY name")
        return self.cursor.fetchall()
    
    def get_project_structure(self, project_id):
        """Get complete structure of a project with sentence IDs"""
        self.cursor.execute("""
            SELECT 
                mc.id as mc_id,
                mc.name as mc_name,
                mc.sort_order as mc_order,
                sc.id as sc_id,
                sc.name as sc_name,
                sc.sort_order as sc_order,
                s.id as s_id,
                s.content as s_content,
                s.sort_order as s_order
            FROM major_categories mc
            LEFT JOIN subcategories sc ON mc.id = sc.major_category_id
            LEFT JOIN sentences s ON sc.id = s.subcategory_id
            WHERE mc.project_id = ?
            ORDER BY mc.sort_order, sc.sort_order, s.sort_order
        """, (project_id,))
        
        results = self.cursor.fetchall()
        
        # Organize into structure
        structure = {}
        for mc_id, mc_name, mc_order, sc_id, sc_name, sc_order, s_id, s_content, s_order in results:
            if mc_id not in structure:
                structure[mc_id] = {
                    'name': mc_name,
                    'order': mc_order,
                    'subcategories': {}
                }
            
            if sc_id and sc_id not in structure[mc_id]['subcategories']:
                structure[mc_id]['subcategories'][sc_id] = {
                    'name': sc_name or '',
                    'order': sc_order,
                    'sentences': []
                }
            
            if s_id:
                structure[mc_id]['subcategories'][sc_id]['sentences'].append({
                    'id': s_id,
                    'content': s_content,
                    'order': s_order
                })
        
        return structure
    
    def copy_sentence(self, sentence_id, target_subcategory_id):
        """Copy a sentence to a target subcategory"""
        # Get the original sentence
        self.cursor.execute("SELECT content FROM sentences WHERE id = ?", (sentence_id,))
        result = self.cursor.fetchone()
        if not result:
            return False
        
        content = result[0]
        
        # Get the max sort_order in target subcategory
        self.cursor.execute("""
            SELECT COALESCE(MAX(sort_order), 0) + 1
            FROM sentences
            WHERE subcategory_id = ?
        """, (target_subcategory_id,))
        sort_order = self.cursor.fetchone()[0]
        
        # Insert the copy
        self.cursor.execute("""
            INSERT INTO sentences (subcategory_id, content, sort_order)
            VALUES (?, ?, ?)
        """, (target_subcategory_id, content, sort_order))
        
        self.conn.commit()
        return True
    
    def move_sentence(self, sentence_id, target_subcategory_id):
        """Move a sentence to a target subcategory"""
        # Get source subcategory
        self.cursor.execute("SELECT subcategory_id FROM sentences WHERE id = ?", (sentence_id,))
        result = self.cursor.fetchone()
        if not result:
            return False
        
        source_subcategory_id = result[0]
        
        # Get the max sort_order in target subcategory
        self.cursor.execute("""
            SELECT COALESCE(MAX(sort_order), 0) + 1
            FROM sentences
            WHERE subcategory_id = ?
        """, (target_subcategory_id,))
        target_sort_order = self.cursor.fetchone()[0]
        
        # Move the sentence
        self.cursor.execute("""
            UPDATE sentences
            SET subcategory_id = ?, sort_order = ?
            WHERE id = ?
        """, (target_subcategory_id, target_sort_order, sentence_id))
        
        # Reorder sentences in source subcategory
        self.cursor.execute("""
            SELECT id FROM sentences
            WHERE subcategory_id = ?
            ORDER BY sort_order
        """, (source_subcategory_id,))
        
        for idx, (sid,) in enumerate(self.cursor.fetchall(), 1):
            self.cursor.execute("UPDATE sentences SET sort_order = ? WHERE id = ?", (idx, sid))
        
        self.conn.commit()
        return True


def print_header(title):
    """Print header bar"""
    rows, cols = get_terminal_size()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")
    header_text = f"  {title}"
    padding = " " * (cols - len(header_text))
    print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}{header_text}{padding}{Colors.RESET}")
    print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")


def print_command_bar(commands):
    """Print command bar at bottom"""
    rows, cols = get_terminal_size()
    print(f"{Colors.BRIGHT_BLACK}" + "─" * cols + f"{Colors.RESET}")
    
    cmd_parts = []
    for key, desc in commands:
        cmd_parts.append(f"{Colors.BRIGHT_YELLOW}{key}{Colors.RESET}:{desc}")
    
    cmd_line = "  ".join(cmd_parts)
    print(f"{Colors.BRIGHT_BLUE}{cmd_line}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}" + "─" * cols + f"{Colors.RESET}")


def display_all_projects(sm, collapsed_projects, page=0, items_per_page=5):
    """Display all projects with collapsible structure and paging"""
    projects = sm.get_all_projects()
    
    if not projects:
        print(f"\n{Colors.DIM}(No projects found){Colors.RESET}\n")
        return {}, 0
    
    # Calculate paging
    total_items = len(projects)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    page_projects = projects[start_idx:end_idx]
    
    print(f"\n{Colors.BRIGHT_CYAN}Projects (Page {page + 1}/{total_pages}):{Colors.RESET}\n")
    
    project_map = {}
    
    for idx, (proj_id, proj_name) in enumerate(page_projects):
        letter = string.ascii_lowercase[start_idx + idx] if (start_idx + idx) < 26 else f"#{start_idx + idx}"
        project_map[letter] = proj_id
        
        is_collapsed = proj_id in collapsed_projects
        collapse_indicator = f"{Colors.DIM}[+]{Colors.RESET}" if is_collapsed else f"{Colors.DIM}[-]{Colors.RESET}"
        
        print(f"{collapse_indicator} {Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
        
        if not is_collapsed:
            # Show project structure
            structure = sm.get_project_structure(proj_id)
            
            if not structure:
                print(f"  {Colors.DIM}(Empty project){Colors.RESET}")
            else:
                # Display headings and sentences
                for mc_id in sorted(structure.keys(), key=lambda x: structure[x]['order']):
                    mc_data = structure[mc_id]
                    print(f"  {Colors.CYAN}• {mc_data['name']}{Colors.RESET} {Colors.DIM}(mc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{mc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                    
                    for sc_id in sorted(mc_data['subcategories'].keys(), key=lambda x: mc_data['subcategories'][x]['order']):
                        sc_data = mc_data['subcategories'][sc_id]
                        
                        if sc_data['name']:
                            print(f"    {Colors.BRIGHT_BLACK}→ {sc_data['name']}{Colors.RESET} {Colors.DIM}(sc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{sc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                        else:
                            print(f"    {Colors.BRIGHT_BLACK}→ {Colors.DIM}(direct){Colors.RESET} {Colors.DIM}(sc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{sc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                        
                        for sentence in sc_data['sentences']:
                            content_preview = sentence['content'][:50] + "..." if len(sentence['content']) > 50 else sentence['content']
                            print(f"      {Colors.GREEN}[{sentence['id']}]{Colors.RESET} {Colors.BRIGHT_WHITE}{content_preview}{Colors.RESET}")
        
        print()
    
    return project_map, total_pages


def main():
    """Main sentence maintenance interface"""
    sm = SentenceMaintenance()
    collapsed_projects = set()
    current_page = 0
    
    while True:
        clear_screen()
        print_header("SENTENCE MAINTENANCE")
        
        project_map, total_pages = display_all_projects(sm, collapsed_projects, current_page)
        
        commands = [
            ("@x", "toggle"),
            ("c <id> <sc_id>", "copy"),
            ("m <id> <sc_id>", "move"),
            ("h", "prev"),
            ("l", "next"),
            ("F1", "help"),
            ("q", "quit")
        ]
        print_command_bar(commands)
        
        # Check for F1 key first (non-blocking)
        print(f"{Colors.BRIGHT_GREEN}> {Colors.RESET}", end='', flush=True)
        first_char = getch()
        
        # F1 key is typically \x1bOP or \x1b[11~
        if first_char == '\x1b':
            # Read escape sequence
            second_char = sys.stdin.read(1)
            if second_char == 'O':
                third_char = sys.stdin.read(1)
                if third_char == 'P':  # F1 key
                    print()  # New line after prompt
                    show_sentence_maintenance_help()
                    continue
            elif second_char == '[':
                # Could be F1 as \x1b[11~
                rest = sys.stdin.read(3)
                if rest == '11~':  # F1 key
                    print()  # New line after prompt
                    show_sentence_maintenance_help()
                    continue
        
        # Not F1, so read the rest of the line
        print(first_char, end='', flush=True)
        rest_of_line = input()
        cmd = (first_char + rest_of_line).strip()
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        if command == 'q':
            break
        
        elif command == '@':
            # Toggle project collapse
            match = re.match(r'^@([a-zA-Z0-9#]+)$', cmd, re.IGNORECASE)
            if not match:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid format. Use '@a' to toggle project")
                import time
                time.sleep(1)
                continue
            
            letter = match.group(1).lower()
            
            if letter not in project_map:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Project [{letter}] not found on this page")
                import time
                time.sleep(1)
                continue
            
            proj_id = project_map[letter]
            
            if proj_id in collapsed_projects:
                collapsed_projects.remove(proj_id)
            else:
                collapsed_projects.add(proj_id)
        
        elif command == 'h':
            # Previous page
            if current_page > 0:
                current_page -= 1
        
        elif command == 'l':
            # Next page
            if current_page < total_pages - 1:
                current_page += 1
        
        elif command == 'c':
            # Copy sentence
            match = re.match(r'^c\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid format. Use 'c <sentence_id> <target_sc_id>'")
                import time
                time.sleep(2)
                continue
            
            sentence_id = int(match.group(1))
            target_sc_id = int(match.group(2))
            
            if sm.copy_sentence(sentence_id, target_sc_id):
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence {sentence_id} copied to sc_id:{target_sc_id}")
            else:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Failed to copy sentence")
            
            import time
            time.sleep(2)
        
        elif command == 'm':
            # Move sentence
            match = re.match(r'^m\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Invalid format. Use 'm <sentence_id> <target_sc_id>'")
                import time
                time.sleep(2)
                continue
            
            sentence_id = int(match.group(1))
            target_sc_id = int(match.group(2))
            
            if sm.move_sentence(sentence_id, target_sc_id):
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence {sentence_id} moved to sc_id:{target_sc_id}")
            else:
                print(f"\n{Colors.RED}Error:{Colors.RESET} Failed to move sentence")
            
            import time
            time.sleep(2)
    
    sm.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal Error:{Colors.RESET} {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")
