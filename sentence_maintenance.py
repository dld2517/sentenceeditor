#!/usr/bin/env python3
"""
Sentence Maintenance - View, copy, and move sentences between projects and headings
"""

import sqlite3
import os
import sys

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLUE = '\033[44m'


class SentenceMaintenance:
    def __init__(self, db_path: str = "project_outlines.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_all_projects(self):
        """Get all projects"""
        self.cursor.execute("SELECT id, name FROM projects ORDER BY name")
        return self.cursor.fetchall()
    
    def get_major_categories(self, project_id: int):
        """Get all major categories in a project"""
        self.cursor.execute("""
            SELECT id, name, sort_order 
            FROM major_categories 
            WHERE project_id = ? 
            ORDER BY sort_order
        """, (project_id,))
        return self.cursor.fetchall()
    
    def get_subcategories(self, major_category_id: int):
        """Get all subcategories for a major category"""
        self.cursor.execute("""
            SELECT id, name, sort_order 
            FROM subcategories 
            WHERE major_category_id = ? 
            ORDER BY sort_order
        """, (major_category_id,))
        return self.cursor.fetchall()
    
    def get_sentences(self, subcategory_id: int):
        """Get all sentences in a subcategory"""
        self.cursor.execute("""
            SELECT id, content, sort_order
            FROM sentences
            WHERE subcategory_id = ?
            ORDER BY sort_order
        """, (subcategory_id,))
        return self.cursor.fetchall()
    
    def get_sentence_by_id(self, sentence_id: int):
        """Get a sentence by ID with full context"""
        self.cursor.execute("""
            SELECT 
                s.id,
                s.content,
                s.subcategory_id,
                mc.name as major_cat,
                sc.name as subcat,
                mc.project_id,
                p.name as project_name,
                mc.id as mc_id,
                sc.id as sc_id
            FROM sentences s
            JOIN subcategories sc ON s.subcategory_id = sc.id
            JOIN major_categories mc ON sc.major_category_id = mc.id
            JOIN projects p ON mc.project_id = p.id
            WHERE s.id = ?
        """, (sentence_id,))
        return self.cursor.fetchone()
    
    def copy_sentence(self, sentence_id: int, target_subcategory_id: int):
        """Copy a sentence to a target subcategory"""
        self.cursor.execute("SELECT content FROM sentences WHERE id = ?", (sentence_id,))
        result = self.cursor.fetchone()
        if not result:
            return False
        
        content = result[0]
        
        # Get the next sort_order for target subcategory
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
    
    def move_sentence(self, sentence_id: int, target_subcategory_id: int):
        """Move a sentence to a target subcategory"""
        self.cursor.execute("SELECT subcategory_id FROM sentences WHERE id = ?", (sentence_id,))
        result = self.cursor.fetchone()
        if not result:
            return False
        
        old_subcategory_id = result[0]
        
        # Get the next sort_order for target subcategory
        self.cursor.execute("""
            SELECT COALESCE(MAX(sort_order), 0) + 1 
            FROM sentences 
            WHERE subcategory_id = ?
        """, (target_subcategory_id,))
        sort_order = self.cursor.fetchone()[0]
        
        # Move the sentence
        self.cursor.execute("""
            UPDATE sentences 
            SET subcategory_id = ?, sort_order = ?
            WHERE id = ?
        """, (target_subcategory_id, sort_order, sentence_id))
        self.conn.commit()
        
        # Reorder remaining sentences in old subcategory
        self.cursor.execute("""
            UPDATE sentences 
            SET sort_order = (
                SELECT COUNT(*) 
                FROM sentences s2 
                WHERE s2.subcategory_id = sentences.subcategory_id 
                AND s2.id <= sentences.id
            )
            WHERE subcategory_id = ?
        """, (old_subcategory_id,))
        self.conn.commit()
        
        return True


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def main_menu():
    """Display main menu"""
    maintenance = SentenceMaintenance()
    
    while True:
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  SENTENCE MAINTENANCE  {Colors.RESET}\n")
        
        print(f"{Colors.BRIGHT_YELLOW}1{Colors.RESET}. {Colors.BRIGHT_WHITE}Browse & View Sentences{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}2{Colors.RESET}. {Colors.BRIGHT_WHITE}Copy Sentence{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}3{Colors.RESET}. {Colors.BRIGHT_WHITE}Move Sentence{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}4{Colors.RESET}. {Colors.BRIGHT_WHITE}Exit{Colors.RESET}")
        
        choice = input(f"\n{Colors.BRIGHT_GREEN}Enter your choice (1-4):{Colors.RESET} ").strip()
        
        if choice == "1":
            browse_sentences(maintenance)
        elif choice == "2":
            copy_sentence_workflow(maintenance)
        elif choice == "3":
            move_sentence_workflow(maintenance)
        elif choice == "4":
            maintenance.close()
            break
        else:
            print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")


def browse_sentences(maintenance):
    """Browse sentences with expandable tree view"""
    while True:
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  BROWSE SENTENCES  {Colors.RESET}\n")
        
        # Step 1: Select project
        projects = maintenance.get_all_projects()
        
        if not projects:
            print(f"{Colors.DIM}No projects found.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_WHITE}Select a project:{Colors.RESET}\n")
        for idx, (proj_id, proj_name) in enumerate(projects, 1):
            print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
        
        print(f"\n  {Colors.BRIGHT_YELLOW}0{Colors.RESET}. {Colors.DIM}Back to main menu{Colors.RESET}")
        
        try:
            choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select project:{Colors.RESET} ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(projects):
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
                continue
            
            selected_proj_id, selected_proj_name = projects[choice - 1]
            browse_project(maintenance, selected_proj_id, selected_proj_name)
            
        except ValueError:
            print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def browse_project(maintenance, project_id, project_name):
    """Browse headings in a project"""
    while True:
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  BROWSE: {project_name}  {Colors.RESET}\n")
        
        major_cats = maintenance.get_major_categories(project_id)
        
        if not major_cats:
            print(f"{Colors.DIM}No headings found in this project.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_WHITE}Select a heading:{Colors.RESET}\n")
        for idx, (mc_id, mc_name, mc_order) in enumerate(major_cats, 1):
            print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_BLUE}[{chr(96+idx)}]{Colors.RESET} {Colors.BRIGHT_WHITE}{mc_name}{Colors.RESET}")
        
        print(f"\n  {Colors.BRIGHT_YELLOW}0{Colors.RESET}. {Colors.DIM}Back to projects{Colors.RESET}")
        
        try:
            choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select heading:{Colors.RESET} ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(major_cats):
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
                continue
            
            selected_mc_id, selected_mc_name, _ = major_cats[choice - 1]
            browse_heading(maintenance, project_id, project_name, selected_mc_id, selected_mc_name)
            
        except ValueError:
            print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def browse_heading(maintenance, project_id, project_name, mc_id, mc_name):
    """Browse subheadings and sentences in a heading"""
    while True:
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  {project_name} > {mc_name}  {Colors.RESET}\n")
        
        subcats = maintenance.get_subcategories(mc_id)
        
        if not subcats:
            print(f"{Colors.DIM}No subheadings found.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_WHITE}Select a subheading to view sentences:{Colors.RESET}\n")
        for idx, (sc_id, sc_name, sc_order) in enumerate(subcats, 1):
            display_name = sc_name if sc_name else f"{Colors.DIM}(Direct to heading){Colors.RESET}"
            print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.CYAN}[{idx}]{Colors.RESET} {display_name}")
        
        print(f"\n  {Colors.BRIGHT_YELLOW}0{Colors.RESET}. {Colors.DIM}Back to headings{Colors.RESET}")
        
        try:
            choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select subheading:{Colors.RESET} ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(subcats):
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
                input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
                continue
            
            selected_sc_id, selected_sc_name, _ = subcats[choice - 1]
            view_sentences(maintenance, project_name, mc_name, selected_sc_name, selected_sc_id)
            
        except ValueError:
            print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def view_sentences(maintenance, project_name, mc_name, sc_name, sc_id):
    """View all sentences in a subheading"""
    clear_screen()
    
    location = f"{project_name} > {mc_name}"
    if sc_name:
        location += f" > {sc_name}"
    
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  {location}  {Colors.RESET}\n")
    
    sentences = maintenance.get_sentences(sc_id)
    
    if not sentences:
        print(f"{Colors.DIM}No sentences found in this subheading.{Colors.RESET}")
    else:
        print(f"{Colors.BRIGHT_WHITE}Sentences:{Colors.RESET}\n")
        for sent_id, content, sort_order in sentences:
            print(f"  {Colors.BRIGHT_YELLOW}ID:{sent_id}{Colors.RESET}")
            print(f"  {Colors.BRIGHT_WHITE}{content}{Colors.RESET}\n")
    
    input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def copy_sentence_workflow(maintenance):
    """Workflow for copying a sentence"""
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  COPY SENTENCE  {Colors.RESET}\n")
    
    # Step 1: Select source sentence
    sentence_id = select_sentence(maintenance, "Select sentence to copy")
    if not sentence_id:
        return
    
    # Show the sentence
    sentence_info = maintenance.get_sentence_by_id(sentence_id)
    if not sentence_info:
        print(f"\n{Colors.RED}Sentence not found.{Colors.RESET}")
        input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
        return
    
    sent_id, content, subcat_id, major_cat, subcat, proj_id, proj_name, mc_id, sc_id = sentence_info
    
    print(f"\n{Colors.GREEN}Selected sentence:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
    print(f"  {Colors.DIM}From: {proj_name} > {major_cat}{' > ' + subcat if subcat else ''}{Colors.RESET}")
    
    # Step 2: Select target location
    target_subcat_id = select_target_location(maintenance, "Copy to")
    if not target_subcat_id:
        return
    
    # Perform copy
    if maintenance.copy_sentence(sentence_id, target_subcat_id):
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence copied successfully!")
    else:
        print(f"\n{Colors.RED}Error copying sentence.{Colors.RESET}")
    
    input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def move_sentence_workflow(maintenance):
    """Workflow for moving a sentence"""
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  MOVE SENTENCE  {Colors.RESET}\n")
    
    # Step 1: Select source sentence
    sentence_id = select_sentence(maintenance, "Select sentence to move")
    if not sentence_id:
        return
    
    # Show the sentence
    sentence_info = maintenance.get_sentence_by_id(sentence_id)
    if not sentence_info:
        print(f"\n{Colors.RED}Sentence not found.{Colors.RESET}")
        input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
        return
    
    sent_id, content, subcat_id, major_cat, subcat, proj_id, proj_name, mc_id, sc_id = sentence_info
    
    print(f"\n{Colors.GREEN}Selected sentence:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_WHITE}{content}{Colors.RESET}")
    print(f"  {Colors.DIM}From: {proj_name} > {major_cat}{' > ' + subcat if subcat else ''}{Colors.RESET}")
    
    # Step 2: Select target location
    target_subcat_id = select_target_location(maintenance, "Move to")
    if not target_subcat_id:
        return
    
    # Perform move
    if maintenance.move_sentence(sentence_id, target_subcat_id):
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Sentence moved successfully!")
    else:
        print(f"\n{Colors.RED}Error moving sentence.{Colors.RESET}")
    
    input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def select_sentence(maintenance, prompt):
    """Helper to select a sentence by ID"""
    print(f"\n{Colors.BRIGHT_CYAN}{prompt}{Colors.RESET}")
    print(f"{Colors.DIM}(Use 'Browse & View Sentences' to see sentence IDs){Colors.RESET}\n")
    
    try:
        sentence_id = int(input(f"{Colors.BRIGHT_GREEN}Enter sentence ID:{Colors.RESET} ").strip())
        return sentence_id
    except ValueError:
        print(f"\n{Colors.RED}Invalid ID.{Colors.RESET}")
        input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
        return None


def select_target_location(maintenance, prompt):
    """Helper to select a target project, heading, and subheading"""
    print(f"\n{Colors.BRIGHT_CYAN}{prompt}{Colors.RESET}\n")
    
    # Step 1: Select project
    projects = maintenance.get_all_projects()
    if not projects:
        print(f"{Colors.RED}No projects found.{Colors.RESET}")
        return None
    
    print(f"{Colors.BRIGHT_WHITE}Available projects:{Colors.RESET}")
    for idx, (proj_id, proj_name) in enumerate(projects, 1):
        print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
    
    try:
        choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select project number:{Colors.RESET} ").strip())
        if choice < 1 or choice > len(projects):
            print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
            return None
        target_proj_id = projects[choice - 1][0]
        target_proj_name = projects[choice - 1][1]
    except ValueError:
        print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
        return None
    
    # Step 2: Select major category (heading)
    major_cats = maintenance.get_major_categories(target_proj_id)
    if not major_cats:
        print(f"\n{Colors.RED}No headings found in project.{Colors.RESET}")
        return None
    
    print(f"\n{Colors.BRIGHT_WHITE}Available headings in '{target_proj_name}':{Colors.RESET}")
    for idx, (mc_id, mc_name, mc_order) in enumerate(major_cats, 1):
        print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{mc_name}{Colors.RESET}")
    
    try:
        choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select heading number:{Colors.RESET} ").strip())
        if choice < 1 or choice > len(major_cats):
            print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
            return None
        target_mc_id = major_cats[choice - 1][0]
        target_mc_name = major_cats[choice - 1][1]
    except ValueError:
        print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
        return None
    
    # Step 3: Select subcategory (subheading or blank)
    subcats = maintenance.get_subcategories(target_mc_id)
    if not subcats:
        print(f"\n{Colors.RED}No subheadings found. Create one first.{Colors.RESET}")
        return None
    
    print(f"\n{Colors.BRIGHT_WHITE}Available subheadings in '{target_mc_name}':{Colors.RESET}")
    for idx, (sc_id, sc_name, sc_order) in enumerate(subcats, 1):
        display_name = sc_name if sc_name else f"{Colors.DIM}(Direct to heading){Colors.RESET}"
        print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {display_name}")
    
    try:
        choice = int(input(f"\n{Colors.BRIGHT_GREEN}Select subheading number:{Colors.RESET} ").strip())
        if choice < 1 or choice > len(subcats):
            print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
            return None
        target_sc_id = subcats[choice - 1][0]
    except ValueError:
        print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")
        return None
    
    return target_sc_id


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal Error:{Colors.RESET} {str(e)}")
        import traceback
        traceback.print_exc()
        input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")
