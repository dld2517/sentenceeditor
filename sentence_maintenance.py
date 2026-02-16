#!/usr/bin/env python3
"""
Sentence Maintenance Module
View, copy, and move sentences between projects with collapsible views and paging
"""

import re
import string
import time
from ui_utils import Colors, Screen, Input, UI
from database_utils import Database
from help import show_sentence_maintenance_help


def display_all_projects(db, collapsed_projects, page=0, items_per_page=5):
    """Display all projects with collapsible structure and paging"""
    projects = db.get_projects()
    
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
        
        print(f"{collapse_indicator} {Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET} {Colors.DIM}(proj_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{proj_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
        
        if not is_collapsed:
            # Show project structure
            lines = db.get_all_lines(proj_id)
            
            if not lines:
                print(f"  {Colors.DIM}(Empty project){Colors.RESET}")
            else:
                # Organize structure
                structure = {}
                for sentence_id, mc_id, mc_name, sc_id, sc_name, content, mc_order, sc_order, s_order in lines:
                    if mc_id not in structure:
                        structure[mc_id] = {
                            'name': mc_name,
                            'order': mc_order,
                            'subcategories': {}
                        }
                    
                    if sc_id not in structure[mc_id]['subcategories']:
                        structure[mc_id]['subcategories'][sc_id] = {
                            'name': sc_name,
                            'order': sc_order,
                            'sentences': []
                        }
                    
                    structure[mc_id]['subcategories'][sc_id]['sentences'].append({
                        'id': sentence_id,
                        'content': content
                    })
                
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
    db = Database()
    
    # Start with all projects collapsed
    projects = db.get_projects()
    collapsed_projects = set(proj_id for proj_id, _ in projects)
    
    current_page = 0
    
    while True:
        Screen.clear()
        UI.print_header("SENTENCE MAINTENANCE")
        
        project_map, total_pages = display_all_projects(db, collapsed_projects, current_page)
        
        # Show helpful prompt if all projects are collapsed
        all_projects = db.get_projects()
        all_collapsed = all(proj_id in collapsed_projects for proj_id, _ in all_projects)
        
        if all_collapsed and all_projects:
            print(f"\n{Colors.BRIGHT_CYAN}💡 Tip:{Colors.RESET} Use {Colors.BRIGHT_YELLOW}@<letter>{Colors.RESET} to expand a project (e.g., {Colors.BRIGHT_YELLOW}@a{Colors.RESET})\n")
        
        commands = [
            ("@x", "toggle"),
            ("cs <s_id> <sc_id>", "copy sent"),
            ("ch <mc_id> <before_mc_id>", "copy head"),
            ("cp <mc_id> <proj_id>", "copy to proj"),
            ("dh <mc_id>", "delete head"),
            ("h", "prev"),
            ("l", "next"),
            ("?", "help"),
            ("q", "quit")
        ]
        UI.print_command_bar(commands)
        
        # Read command with F1 detection
        cmd, is_f1 = Input.read_command_with_f1()
        
        if is_f1:
            show_sentence_maintenance_help()
            continue
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        if command == 'q':
            break
        
        elif command == '@':
            # Toggle project collapse
            match = re.match(r'^@([a-zA-Z0-9#]+)$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use '@a' to toggle project")
                time.sleep(1)
                continue
            
            letter = match.group(1).lower()
            
            if letter not in project_map:
                UI.error(f"Project [{letter}] not found on this page")
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
        
        elif cmd.startswith('cs '):
            # Copy sentence
            match = re.match(r'^cs\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use 'cs <sentence_id> <target_sc_id>'")
                time.sleep(2)
                continue
            
            sentence_id = int(match.group(1))
            target_sc_id = int(match.group(2))
            
            if db.copy_sentence(sentence_id, target_sc_id):
                UI.success(f"Sentence {sentence_id} copied to sc_id:{target_sc_id}")
            else:
                UI.error("Failed to copy sentence")
            
            time.sleep(2)
        
        elif cmd.startswith('ch '):
            # Copy heading within same project (insert before another heading)
            match = re.match(r'^ch\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use 'ch <mc_id> <before_mc_id>'")
                time.sleep(2)
                continue
            
            mc_id = int(match.group(1))
            before_mc_id = int(match.group(2))
            
            if db.copy_major_category_before(mc_id, before_mc_id):
                UI.success(f"Heading mc_id:{mc_id} copied before mc_id:{before_mc_id}")
            else:
                UI.error("Failed to copy heading")
            
            time.sleep(2)
        
        elif cmd.startswith('cp '):
            # Copy heading to another project
            match = re.match(r'^cp\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use 'cp <mc_id> <target_project_id>'")
                time.sleep(2)
                continue
            
            mc_id = int(match.group(1))
            target_proj_id = int(match.group(2))
            
            # Copy to end of target project
            if db.copy_major_category(mc_id, target_proj_id, 999):
                UI.success(f"Heading mc_id:{mc_id} copied to project {target_proj_id}")
            else:
                UI.error("Failed to copy heading")
            
            time.sleep(2)
        
        elif cmd.startswith('dh '):
            # Delete heading
            match = re.match(r'^dh\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                UI.error("Invalid format. Use 'dh <mc_id>'")
                time.sleep(2)
                continue
            
            mc_id = int(match.group(1))
            
            if db.delete_major_category(mc_id):
                UI.success(f"Heading mc_id:{mc_id} deleted")
            else:
                UI.error("Failed to delete heading")
            
            time.sleep(2)
        
        elif command == 'p':
            # Refresh
            continue
        
        else:
            UI.error(f"Unknown command: {command}")
            time.sleep(1)
    
    db.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
    except Exception as e:
        UI.error(str(e))
        import traceback
        traceback.print_exc()
        input("Press Enter to continue...")
