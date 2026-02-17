#!/usr/bin/env python3
"""
Export Project Outline Database to Plain Text File and/or Word Document
"""

import os
import sys
from ui_utils import Colors, Screen, UI
from database_utils import Database
from export_utils import ExportManager


def main():
    """Main function"""
    db_path = "project_outlines.db"
    
    Screen.clear()
    
    if not os.path.exists(db_path):
        UI.print_header("EXPORT PROJECT")
        UI.error(f"Database file '{db_path}' not found.")
        print(f"{Colors.DIM}Make sure you're running this script in the same directory as your database.{Colors.RESET}\n")
        sys.exit(1)
    
    # Initialize database and export manager
    db = Database(db_path)
    exporter = ExportManager()
    
    # Get projects
    projects = db.get_projects()
    
    if not projects:
        UI.print_header("EXPORT PROJECT")
        print(f"\n{Colors.DIM}(No projects found in the database){Colors.RESET}\n")
        db.close()
        sys.exit(1)
    
    UI.print_header("EXPORT PROJECT")
    
    print(f"\n{Colors.BRIGHT_CYAN}Available Projects:{Colors.RESET}\n")
    for idx, (proj_id, proj_name) in enumerate(projects, 1):
        print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
    
    # Select project
    while True:
        try:
            choice = input(f"\n{Colors.BRIGHT_GREEN}> Enter project number:{Colors.RESET} ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(projects):
                project_id = projects[choice_num - 1][0]
                project_name = projects[choice_num - 1][1]
                break
            else:
                print(f"{Colors.RED}Invalid project number. Please try again.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
    
    # Ask for export format
    print(f"\n{Colors.BRIGHT_CYAN}Export Format:{Colors.RESET}\n")
    print(f"  {Colors.BRIGHT_YELLOW}1{Colors.RESET}. Text file only (.txt)")
    print(f"  {Colors.BRIGHT_YELLOW}2{Colors.RESET}. Word document only (.docx)")
    print(f"  {Colors.BRIGHT_YELLOW}3{Colors.RESET}. Both text and Word")
    
    while True:
        format_choice = input(f"\n{Colors.BRIGHT_GREEN}> Select format:{Colors.RESET} ").strip()
        if format_choice in ['1', '2', '3']:
            break
        print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.RESET}")
    
    # Get filename
    default_filename = project_name.replace(' ', '_')
    output_filename = input(f"\n{Colors.BRIGHT_GREEN}> Enter filename (default: {Colors.BRIGHT_WHITE}{default_filename}{Colors.BRIGHT_GREEN}):{Colors.RESET} ").strip()
    
    if not output_filename:
        output_filename = default_filename
    
    success_count = 0
    
    # Export text file
    if format_choice in ['1', '3']:
        print(f"\n{Colors.DIM}Exporting to text file...{Colors.RESET}")
        txt_file = exporter.export_to_text(db, project_id, project_name)
        if txt_file:
            UI.success(f"Text file saved: {Colors.BRIGHT_WHITE}{txt_file}{Colors.RESET}")
            success_count += 1
        else:
            UI.error("Text export failed")
    
    # Export Word document
    if format_choice in ['2', '3']:
        print(f"\n{Colors.DIM}Exporting to Word document...{Colors.RESET}")
        try:
            docx_file = exporter.export_to_word(db, project_id, project_name)
            if docx_file:
                UI.success(f"Word document saved: {Colors.BRIGHT_WHITE}{docx_file}{Colors.RESET}")
                success_count += 1
            else:
                UI.error("Word export failed")
        except Exception as e:
            UI.error(f"Word export failed: {e}")
    
    db.close()
    
    if success_count > 0:
        print(f"\n{Colors.GREEN}✓{Colors.RESET} Export completed successfully!\n")
    else:
        print(f"\n{Colors.RED}✗ Export failed.{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_CYAN}Export cancelled.{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        UI.error(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
