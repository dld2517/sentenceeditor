#!/usr/bin/env python3
"""
Outline Editor - Modern word-processor style interface for hierarchical outlines
"""

import re
from ui_utils import Colors, Screen, Input, UI
from database_utils import Database
from editor_utils import EditorHelpers, CollapseManager
from project_state import get_active_project, set_active_project
from inline_editor import edit_line_inline
from help import show_outline_editor_help


def main():
    """Main outline editor function"""
    # Initialize database
    db = Database()
    
    # Get or create project
    active_project = get_active_project()
    
    if active_project:
        project_id, project_name = active_project
        # Verify project still exists
        project = db.get_project(project_id)
        if not project:
            active_project = None
    
    if not active_project:
        Screen.clear()
        UI.print_header("SELECT OR CREATE PROJECT")
        
        projects = db.list_projects()
        
        if projects:
            print(f"\n{Colors.BRIGHT_CYAN}Existing Projects:{Colors.RESET}\n")
            for idx, (proj_id, proj_name) in enumerate(projects, 1):
                print(f"  {Colors.BRIGHT_YELLOW}{idx}{Colors.RESET}. {Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET}")
            
            choice = input(f"\n{Colors.BRIGHT_GREEN}Select project (number or N):{Colors.RESET} ").strip().upper()
            
            if choice == 'N':
                name = input(f"{Colors.BRIGHT_GREEN}Enter project name:{Colors.RESET} ").strip()
                if name:
                    project_id = db.create_project(name)
                    if not project_id:
                        UI.error("Project already exists.")
                        db.close()
                        return
                    set_active_project(project_id, name)
                else:
                    UI.error("Project name cannot be empty.")
                    db.close()
                    return
            else:
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(projects):
                        project_id, project_name = projects[idx - 1]
                        set_active_project(project_id, project_name)
                    else:
                        UI.error("Invalid selection.")
                        db.close()
                        return
                except ValueError:
                    UI.error("Invalid input.")
                    db.close()
                    return
        else:
            name = input(f"\n{Colors.BRIGHT_GREEN}Enter project name:{Colors.RESET} ").strip()
            if name:
                project_id = db.create_project(name)
                if not project_id:
                    UI.error("Project already exists.")
                    db.close()
                    return
                set_active_project(project_id, name)
            else:
                UI.error("Project name cannot be empty.")
                db.close()
                return
    
    # Main editor loop
    current_major_category_id = None
    current_major_category_name = None
    current_subcategory_id = None
    current_subcategory_name = None
    collapse_mgr = CollapseManager()
    current_page = 0
    total_pages = 1
    
    while True:
        Screen.clear()
        
        # Get current project name
        project = db.get_project(project_id)
        project_name = project[1]
        
        # Print header
        UI.print_header("PROJECT", project_name)
        
        # Print outline with paging
        heading_map, subheading_map, total_pages = EditorHelpers.print_outline(db, project_id, collapse_mgr.collapsed, current_page)
        
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
        
        # Print context and command bar
        UI.print_context(current_major_category_name, current_heading_key, current_subcategory_name, current_subheading_key)
        
        commands = [
            ("h", "a <name>", "heading"),
            ("h", "a1 <name>", "subheading"),
            ("+  <text>", "", "add"),
            ("i <#> <text>", "", "insert"),
            ("e <#>", "", "edit"),
            ("d <#>", "", "delete"),
            ("@a", "", "toggle"),
            ("h/l", "", "page"),
            ("?", "", "help"),
            ("q", "", "quit")
        ]
        UI.print_command_bar(commands)
        
        # Read command with F1 detection
        cmd, is_f1 = Input.read_command_with_f1()
        
        if is_f1:
            show_outline_editor_help()
            continue
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        # Quit command
        if command == 'q':
            break
        
        # Page navigation - check for single 'h' or 'l' before heading commands
        elif cmd == 'h':
            # Previous page
            if current_page > 0:
                current_page -= 1
            continue
        
        elif cmd == 'l':
            # Next page
            if current_page < total_pages - 1:
                current_page += 1
            continue
        
        # Toggle collapse/expand
        elif command == '@':
            match = re.match(r'^@([a-zA-Z])$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use '@a' to toggle heading a")
                continue
            
            letter = match.group(1).lower()
            
            if letter not in heading_map:
                UI.error(f"Heading [{letter}] doesn't exist")
                continue
            
            # Toggle collapse state
            is_collapsed = collapse_mgr.toggle(letter)
            if is_collapsed:
                UI.success(f"Heading [{letter}] collapsed")
            else:
                UI.success(f"Heading [{letter}] expanded")
        
        # Heading/subheading commands
        elif command == 'h':
            result = EditorHelpers.parse_heading_command(cmd)
            if not result:
                UI.error("Invalid format. Use 'ha <name>' for heading or 'ha1 <name>' for subheading")
                continue
            
            letter, number, text = result
            
            # Subheading command
            if number:
                subheading_key = f"{letter}{number}"
                
                if letter not in heading_map:
                    UI.error(f"Heading [{letter}] doesn't exist. Create it first with 'h{letter} <name>'")
                    continue
                
                mc_id, mc_name = heading_map[letter]
                
                if subheading_key in subheading_map:
                    # Subheading exists
                    sc_id, sc_name, parent_mc_id = subheading_map[subheading_key]
                    
                    if text:
                        # Rename subheading
                        if db.update_subcategory_name(sc_id, text):
                            UI.success(f"Subheading [{subheading_key}] renamed to: {text}")
                            current_subcategory_id = sc_id
                            current_subcategory_name = text
                        else:
                            UI.error("Could not rename subheading")
                    else:
                        # Select subheading
                        current_subcategory_id = sc_id
                        current_subcategory_name = sc_name
                        current_major_category_id = mc_id
                        current_major_category_name = mc_name
                        UI.success(f"Current subheading set to: [{subheading_key}] {sc_name}")
                else:
                    # Create new subheading
                    if not text:
                        UI.error(f"Subheading name required. Example: h{subheading_key} Your Subheading Name")
                        continue
                    
                    existing_subs = [k for k in subheading_map.keys() if k.startswith(letter)]
                    expected_num = len(existing_subs) + 1
                    
                    if int(number) != expected_num:
                        UI.error(f"Next subheading should be '{letter}{expected_num}'. Use 'h{letter}{expected_num} <name>' to create it.")
                        continue
                    
                    sc_id = db.create_subcategory(mc_id, text)
                    if sc_id:
                        current_subcategory_id = sc_id
                        current_subcategory_name = text
                        current_major_category_id = mc_id
                        current_major_category_name = mc_name
                        UI.success(f"Subheading [{subheading_key}] created: {text}")
                    else:
                        UI.error("Could not create subheading")
            else:
                # Heading command
                if letter in heading_map:
                    # Heading exists
                    mc_id, mc_name = heading_map[letter]
                    
                    if text:
                        # Rename heading
                        if db.update_major_category_name(mc_id, text):
                            current_major_category_id = mc_id
                            current_major_category_name = text
                            current_subcategory_id = None
                            current_subcategory_name = None
                            UI.success(f"Heading [{letter}] renamed to: {text}")
                        else:
                            UI.error("Could not rename heading (name may already exist)")
                    else:
                        # Select heading
                        current_major_category_id = mc_id
                        current_major_category_name = mc_name
                        current_subcategory_id = None
                        current_subcategory_name = None
                        UI.success(f"Selected heading [{letter}] {mc_name}")
                        print(f"{Colors.DIM}Use '+' to add sentence, or 'h{letter}1 <name>' to create subheading{Colors.RESET}")
                else:
                    # Create new heading
                    if not text:
                        UI.error(f"Heading [{letter}] doesn't exist. Use 'h{letter} <name>' to create it.")
                        continue
                    
                    # Check sequence
                    expected_letter = EditorHelpers.get_heading_key(len(heading_map))
                    
                    if letter != expected_letter:
                        UI.error(f"Next heading should be '{expected_letter}'. Use 'h{expected_letter} <name>' to create it.")
                        continue
                    
                    # Create heading
                    mc_id = db.create_major_category(project_id, text)
                    if mc_id:
                        current_major_category_id = mc_id
                        current_major_category_name = text
                        current_subcategory_id = None
                        current_subcategory_name = None
                        UI.success(f"Heading [{letter}] created: {text}")
                        print(f"{Colors.DIM}Use '+' to add sentence, or 'h{letter}1 <name>' to create subheading{Colors.RESET}")
                    else:
                        UI.error("Could not create heading (name may already exist)")
        
        # Add sentence
        elif command == '+':
            if len(cmd) < 2 or not cmd[1:].strip():
                UI.error("Sentence text required. Example: + This is my sentence")
                continue
            
            sentence_text = cmd[1:].strip()
            
            # If no subcategory selected, use or create blank subcategory
            if not current_subcategory_id:
                if current_major_category_id:
                    # Look for existing blank subcategory
                    subcats = db.get_subcategories(current_major_category_id)
                    blank_subcat_id = None
                    for sc_id, sc_name, _ in subcats:
                        if sc_name == "":
                            blank_subcat_id = sc_id
                            break
                    
                    # Create blank subcategory if needed
                    if not blank_subcat_id:
                        blank_subcat_id = db.create_subcategory(current_major_category_id, "")
                    
                    if blank_subcat_id:
                        db.add_sentence(blank_subcat_id, sentence_text)
                        UI.success("Sentence added to topic")
                    else:
                        UI.error("Could not create subcategory")
                else:
                    UI.error("Select a heading first (e.g., 'ha' or 'ha Topic Name')")
            else:
                db.add_sentence(current_subcategory_id, sentence_text)
                UI.success("Sentence added")
        
        # Insert sentence
        elif command == 'i':
            parts = cmd[1:].strip().split(None, 1)
            if len(parts) < 2:
                UI.error("Usage: i <line#> <text>. Example: i 3 New sentence")
                continue
            
            try:
                line_num = int(parts[0])
                new_content = parts[1]
                
                new_id = db.insert_sentence(line_num, new_content, project_id)
                if new_id:
                    UI.success(f"Sentence inserted before line {line_num}")
                else:
                    UI.error(f"Line {line_num} does not exist")
            except ValueError:
                UI.error("Invalid line number. Example: i 3 New sentence")
        
        # Edit sentence
        elif command == 'e':
            try:
                line_num = int(cmd[1:].strip())
                
                sentence_data = db.get_sentence_by_line_number(project_id, line_num)
                if sentence_data:
                    sentence_id = sentence_data[0]
                    current_text = sentence_data[5]  # content
                    
                    # Use inline vim-style editor
                    new_text, cancelled = edit_line_inline(line_num, current_text)
                    
                    if not cancelled and new_text != current_text:
                        db.update_sentence(sentence_id, new_text)
                else:
                    UI.error(f"Line {line_num} does not exist")
            except ValueError:
                UI.error("Invalid line number. Example: e 3")
        
        # Delete sentence
        elif command == 'd':
            try:
                line_num = int(cmd[1:].strip())
                
                sentence_data = db.get_sentence_by_line_number(project_id, line_num)
                if sentence_data:
                    sentence_id = sentence_data[0]
                    db.delete_sentence(sentence_id)
                    UI.success(f"Line {line_num} deleted")
                else:
                    UI.error(f"Line {line_num} does not exist")
            except ValueError:
                UI.error("Invalid line number")
        
        # Refresh
        elif command == 'p':
            continue
        
        else:
            UI.error(f"Unknown command: {command}")
    
    db.close()
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
        UI.error(str(e))
        import traceback
        traceback.print_exc()
