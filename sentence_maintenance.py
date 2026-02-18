#!/usr/bin/env python3
"""
Sentence Maintenance Module
View, copy, and move sentences between projects with collapsible views and seamless pagination
"""

import re
import string
import time
from ui_utils import Colors, Screen, Input, UI
from database_utils import Database
from help import show_sentence_maintenance_help


def build_all_output_lines(db, collapsed_projects):
    """
    Build all output lines for all projects (respecting collapse state)
    Returns: (output_lines, project_map)
    """
    projects = db.get_projects()
    
    if not projects:
        return [f"{Colors.DIM}(No projects found){Colors.RESET}"], {}
    
    output_lines = []
    project_map = {}
    
    for idx, (proj_id, proj_name) in enumerate(projects):
        letter = string.ascii_lowercase[idx] if idx < 26 else f"#{idx}"
        project_map[letter] = proj_id
        
        is_collapsed = proj_id in collapsed_projects
        collapse_indicator = f"{Colors.DIM}[+]{Colors.RESET}" if is_collapsed else f"{Colors.DIM}[-]{Colors.RESET}"
        
        output_lines.append(f"{collapse_indicator} {Colors.BRIGHT_BLUE}[{letter}]{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{proj_name}{Colors.RESET} {Colors.DIM}(proj_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{proj_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
        
        if not is_collapsed:
            # Show project structure
            lines = db.get_all_lines(proj_id)
            
            if not lines:
                output_lines.append(f"  {Colors.DIM}(Empty project){Colors.RESET}")
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
                    output_lines.append(f"  {Colors.CYAN}• {mc_data['name']}{Colors.RESET} {Colors.DIM}(mc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{mc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                    
                    for sc_id in sorted(mc_data['subcategories'].keys(), key=lambda x: mc_data['subcategories'][x]['order']):
                        sc_data = mc_data['subcategories'][sc_id]
                        
                        if sc_data['name']:
                            output_lines.append(f"    {Colors.BRIGHT_BLACK}→ {sc_data['name']}{Colors.RESET} {Colors.DIM}(sc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{sc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                        else:
                            output_lines.append(f"    {Colors.BRIGHT_BLACK}→ {Colors.DIM}(direct){Colors.RESET} {Colors.DIM}(sc_id:{Colors.RESET}{Colors.BRIGHT_YELLOW}{sc_id}{Colors.RESET}{Colors.DIM}){Colors.RESET}")
                        
                        for sentence in sc_data['sentences']:
                            # Show full sentence without truncation
                            output_lines.append(f"      {Colors.GREEN}[{sentence['id']}]{Colors.RESET} {Colors.BRIGHT_WHITE}{sentence['content']}{Colors.RESET}")
        
        output_lines.append("")  # Blank line between projects
    
    return output_lines, project_map


def chunk_lines(lines, max_lines):
    """Split lines into chunks that fit on screen"""
    if not lines:
        return [[]]
    chunks = []
    for i in range(0, len(lines), max_lines):
        chunks.append(lines[i:i + max_lines])
    return chunks


def main():
    """Main sentence maintenance interface"""
    db = Database()
    
    # Start with all projects collapsed
    projects = db.get_projects()
    collapsed_projects = set(proj_id for proj_id, _ in projects)
    
    current_page = 0
    status_message = None
    status_type = None  # 'success' or 'error'
    
    while True:
        # Calculate available lines for content
        rows, cols = Screen.get_size()
        # Reserve lines (being conservative):
        # header(3) + blank(1) + tip(2) + blank(1) + page_info(1) + 
        # status(1) + blank(1) + command_bar(2) + prompt(1) + buffer(2) = 15 lines
        reserved_lines = 15
        available_lines = max(5, rows - reserved_lines)
        
        # Build all output lines based on current collapse state
        output_lines, project_map = build_all_output_lines(db, collapsed_projects)
        
        # Chunk into pages
        pages = chunk_lines(output_lines, available_lines)
        total_pages = len(pages)
        
        # Ensure current_page is within bounds
        if current_page >= total_pages:
            current_page = total_pages - 1
        if current_page < 0:
            current_page = 0
        
        # Display screen
        Screen.clear()
        UI.print_header("SENTENCE MAINTENANCE")
        
        # Display current page - print ONLY available_lines to prevent scrolling
        print()
        lines_to_display = pages[current_page][:available_lines]
        for line in lines_to_display:
            print(line)
        
        # Fill remaining lines with blank space to keep layout consistent
        lines_displayed = len(lines_to_display)
        for _ in range(available_lines - lines_displayed):
            print()
        
        # Show helpful prompt if all projects are collapsed
        all_projects = db.get_projects()
        all_collapsed = all(proj_id in collapsed_projects for proj_id, _ in all_projects)
        
        if all_collapsed and all_projects:
            print(f"\n{Colors.BRIGHT_CYAN}💡 Tip:{Colors.RESET} Use {Colors.BRIGHT_YELLOW}@<letter>{Colors.RESET} to expand a project (e.g., {Colors.BRIGHT_YELLOW}@a{Colors.RESET})")
        
        # Show page indicator if multiple pages
        if total_pages > 1:
            print(f"\n{Colors.DIM}Page {current_page + 1}/{total_pages} (use h/l to navigate){Colors.RESET}")
        
        # Show status message if present
        if status_message:
            print()
            if status_type == 'success':
                UI.success(status_message)
            else:
                UI.error(status_message)
            status_message = None  # Clear after displaying
        
        print()  # Blank line before command bar
        
        commands = [
            ("@x", "toggle"),
            ("cs <s_id> <sc_id>", "copy sent"),
            ("ch <mc_id> <before_mc_id>", "copy head"),
            ("cp <mc_id> <proj_id>", "copy to proj"),
            ("dh <mc_id>", "delete head"),
            ("h/l", "page"),
            ("?", "help"),
            ("q", "quit")
        ]
        UI.print_command_bar(commands)
        
        # Read first character to check for single-key commands (h, l, q, ?)
        first_char = Input.getch()
        
        # Handle single-key commands
        if first_char.lower() == 'h':
            # Previous page
            if current_page > 0:
                current_page -= 1
            continue
        
        elif first_char.lower() == 'l':
            # Next page
            if current_page < total_pages - 1:
                current_page += 1
            continue
        
        elif first_char.lower() == 'q':
            break
        
        elif first_char == '?':
            show_sentence_maintenance_help()
            continue
        
        # For multi-character commands, show what was typed and get the rest
        print(first_char, end='', flush=True)
        rest_of_line = input()
        cmd = first_char + rest_of_line
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        if command == '@':
            # Toggle project collapse
            match = re.match(r'^@([a-zA-Z0-9#]+)$', cmd, re.IGNORECASE)
            if not match:
                status_message = "Invalid format. Use '@a' to toggle project"
                status_type = 'error'
                continue
            
            letter = match.group(1).lower()
            
            if letter not in project_map:
                status_message = f"Project [{letter}] not found"
                status_type = 'error'
                continue
            
            proj_id = project_map[letter]
            
            if proj_id in collapsed_projects:
                collapsed_projects.remove(proj_id)
            else:
                collapsed_projects.add(proj_id)
            
            # Pages will be recalculated on next iteration
            continue
        
        elif cmd.startswith('cs '):
            # Copy sentence
            match = re.match(r'^cs\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                status_message = "Invalid format. Use 'cs <sentence_id> <target_sc_id>'"
                status_type = 'error'
                continue
            
            sentence_id = int(match.group(1))
            target_sc_id = int(match.group(2))
            
            if db.copy_sentence(sentence_id, target_sc_id):
                status_message = f"Sentence {sentence_id} copied to sc_id:{target_sc_id}"
                status_type = 'success'
            else:
                status_message = "Failed to copy sentence"
                status_type = 'error'
            continue
        
        elif cmd.startswith('ch '):
            # Copy heading within same project (insert before another heading)
            match = re.match(r'^ch\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                status_message = "Invalid format. Use 'ch <mc_id> <before_mc_id>'"
                status_type = 'error'
                continue
            
            mc_id = int(match.group(1))
            before_mc_id = int(match.group(2))
            
            if db.copy_major_category_before(mc_id, before_mc_id):
                status_message = f"Heading mc_id:{mc_id} copied before mc_id:{before_mc_id}"
                status_type = 'success'
            else:
                status_message = "Failed to copy heading"
                status_type = 'error'
            continue
        
        elif cmd.startswith('cp '):
            # Copy heading to another project
            match = re.match(r'^cp\s+(\d+)\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                status_message = "Invalid format. Use 'cp <mc_id> <target_project_id>'"
                status_type = 'error'
                continue
            
            mc_id = int(match.group(1))
            target_proj_id = int(match.group(2))
            
            # Copy to end of target project
            if db.copy_major_category(mc_id, target_proj_id, 999):
                status_message = f"Heading mc_id:{mc_id} copied to project {target_proj_id}"
                status_type = 'success'
            else:
                status_message = "Failed to copy heading"
                status_type = 'error'
            continue
        
        elif cmd.startswith('dh '):
            # Delete heading
            match = re.match(r'^dh\s+(\d+)$', cmd, re.IGNORECASE)
            if not match:
                status_message = "Invalid format. Use 'dh <mc_id>'"
                status_type = 'error'
                continue
            
            mc_id = int(match.group(1))
            
            if db.delete_major_category(mc_id):
                status_message = f"Heading mc_id:{mc_id} deleted"
                status_type = 'success'
            else:
                status_message = "Failed to delete heading"
                status_type = 'error'
            continue
        
        elif command == 'p':
            # Refresh
            continue
        
        else:
            status_message = f"Unknown command: {command}"
            status_type = 'error'
    
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
