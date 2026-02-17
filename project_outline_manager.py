#!/usr/bin/env python3
"""
Project Outline Manager - Menu-based interface for managing projects
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional
from project_state import set_active_project
from config import DB_PATH

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BG_BLUE = '\033[44m'


class ProjectOutlineManager:
    def __init__(self, db_path: str = None):
        # Use configured database path if not specified
        self.db_path = db_path if db_path is not None else DB_PATH
        self.conn = None
        self.cursor = None
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_major_categories_project ON major_categories(project_id);
            CREATE INDEX IF NOT EXISTS idx_subcategories_major_category ON subcategories(major_category_id);
            CREATE INDEX IF NOT EXISTS idx_sentences_subcategory ON sentences(subcategory_id);
        """)
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_project(self, name: str) -> int:
        """Create a new project"""
        try:
            self.cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def list_projects(self) -> List[Tuple]:
        """List all projects"""
        self.cursor.execute("SELECT id, name, created_at FROM projects ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def get_project_by_id(self, project_id: int) -> Optional[Tuple]:
        """Get project by ID"""
        self.cursor.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
        return self.cursor.fetchone()
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its data"""
        self.cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def main_menu():
    """Display main menu and handle user interaction"""
    manager = ProjectOutlineManager()
    
    while True:
        clear_screen()
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  PROJECT MANAGER  {Colors.RESET}\n")
        
        print(f"{Colors.BRIGHT_YELLOW}1{Colors.RESET}. {Colors.BRIGHT_WHITE}Create New Project{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}2{Colors.RESET}. {Colors.BRIGHT_WHITE}Select Project (Set as Active){Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}3{Colors.RESET}. {Colors.BRIGHT_WHITE}List All Projects{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}4{Colors.RESET}. {Colors.BRIGHT_WHITE}Delete Project{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}Q{Colors.RESET}. {Colors.BRIGHT_BLACK}Quit{Colors.RESET}")
        
        choice = input(f"\n{Colors.BRIGHT_GREEN}Enter your choice (1-4, Q):{Colors.RESET} ").strip().upper()
        
        if choice == "1":
            create_project_workflow(manager)
        elif choice == "2":
            select_project_workflow(manager)
        elif choice == "3":
            list_projects_workflow(manager)
        elif choice == "4":
            delete_project_workflow(manager)
        elif choice == "Q":
            manager.close()
            break
        else:
            print(f"\n{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")


def create_project_workflow(manager):
    """Workflow for creating a new project"""
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  CREATE NEW PROJECT  {Colors.RESET}\n")
    
    name = input(f"{Colors.BRIGHT_GREEN}Enter project name:{Colors.RESET} ").strip()
    if not name:
        print(f"{Colors.RED}Project name cannot be empty.{Colors.RESET}")
        return
    
    project_id = manager.create_project(name)
    if project_id:
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Project '{Colors.BRIGHT_WHITE}{name}{Colors.RESET}' created successfully!")
        
        set_as_active = input(f"\n{Colors.BRIGHT_GREEN}Set as active project? (y/n):{Colors.RESET} ").strip().lower()
        if set_as_active == 'y':
            set_active_project(project_id, name)
            print(f"{Colors.GREEN}✓{Colors.RESET} Set as active project")
    else:
        print(f"{Colors.RED}Error: Project already exists.{Colors.RESET}")


def select_project_workflow(manager):
    """Workflow for selecting a project as active"""
    projects = manager.list_projects()
    
    if not projects:
        clear_screen()
        print(f"\n{Colors.DIM}No projects found. Create a new project first.{Colors.RESET}")
        return
    
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  SELECT PROJECT  {Colors.RESET}\n")
    
    print(f"{Colors.BRIGHT_CYAN}Available Projects:{Colors.RESET}\n")
    for idx, (proj_id, proj_name, created_at) in enumerate(projects, 1):
        print(f"{Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET} {Colors.DIM}(Created: {created_at}){Colors.RESET}")
    
    choice = input(f"\n{Colors.BRIGHT_GREEN}Enter project number (or 0 to cancel):{Colors.RESET} ").strip()
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            return
        if 1 <= choice_num <= len(projects):
            project_id, project_name, _ = projects[choice_num - 1]
            set_active_project(project_id, project_name)
            print(f"\n{Colors.GREEN}✓{Colors.RESET} '{Colors.BRIGHT_WHITE}{project_name}{Colors.RESET}' is now the active project")
            print(f"{Colors.DIM}Use Outline Editor to work with this project{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid project number.{Colors.RESET}")
    except ValueError:
        print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")


def list_projects_workflow(manager):
    """Workflow for listing all projects"""
    projects = manager.list_projects()
    
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  ALL PROJECTS  {Colors.RESET}\n")
    
    if not projects:
        print(f"{Colors.DIM}No projects found.{Colors.RESET}")
    else:
        for idx, (proj_id, proj_name, created_at) in enumerate(projects, 1):
            print(f"\n{Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
            print(f"   {Colors.DIM}ID: {proj_id}{Colors.RESET}")
            print(f"   {Colors.DIM}Created: {created_at}{Colors.RESET}")
    
    input(f"\n{Colors.BRIGHT_GREEN}Press Enter to continue...{Colors.RESET}")


def delete_project_workflow(manager):
    """Workflow for deleting a project"""
    projects = manager.list_projects()
    
    if not projects:
        clear_screen()
        print(f"\n{Colors.DIM}No projects found.{Colors.RESET}")
        return
    
    clear_screen()
    print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}  DELETE PROJECT  {Colors.RESET}\n")
    
    print(f"{Colors.BRIGHT_CYAN}Available Projects:{Colors.RESET}\n")
    for idx, (proj_id, proj_name, created_at) in enumerate(projects, 1):
        print(f"{Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
    
    choice = input(f"\n{Colors.BRIGHT_GREEN}Enter project number to delete (or 0 to cancel):{Colors.RESET} ").strip()
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            return
        if 1 <= choice_num <= len(projects):
            project_id, project_name, _ = projects[choice_num - 1]
            confirm = input(f"\n{Colors.RED}Are you sure you want to delete '{project_name}'? (yes/no):{Colors.RESET} ").strip().lower()
            if confirm == "yes":
                if manager.delete_project(project_id):
                    print(f"\n{Colors.GREEN}✓{Colors.RESET} Project '{Colors.BRIGHT_WHITE}{project_name}{Colors.RESET}' deleted successfully!")
                else:
                    print(f"\n{Colors.RED}Failed to delete project.{Colors.RESET}")
            else:
                print(f"\n{Colors.DIM}Deletion cancelled.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid project number.{Colors.RESET}")
    except ValueError:
        print(f"\n{Colors.RED}Invalid input.{Colors.RESET}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_CYAN}Exiting...{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error:{Colors.RESET} {e}")
        import traceback
        traceback.print_exc()
