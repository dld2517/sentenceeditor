#!/usr/bin/env python3
"""
Help System for Outline Management System
Provides detailed help documentation for outline_editor and sentence_maintenance
"""

from ui_utils import Colors, Screen, Input


def chunk_content(lines, max_lines):
    """Split content lines into chunks that fit on screen"""
    chunks = []
    current_chunk = []
    
    for line in lines:
        current_chunk.append(line)
        if len(current_chunk) >= max_lines:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def show_paged_help(content_lines, title):
    """Display help content with dynamic paging based on terminal height"""
    rows, cols = Screen.get_size()
    
    # Reserve lines for header (3 lines) and navigation bar (4 lines)
    available_lines = rows - 7
    
    # Chunk the content
    pages = chunk_content(content_lines, available_lines)
    current_page = 0
    total_pages = len(pages)
    
    while True:
        Screen.clear()
        
        # Header
        print(f"{Colors.BLUE_BG}{' ' * cols}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{Colors.BRIGHT_WHITE}{title:^{cols}}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{' ' * cols}{Colors.RESET}")
        print()
        
        # Display current page
        print(pages[current_page])
        
        # Navigation bar
        print()
        print(f"{Colors.DIM}{'─' * cols}{Colors.RESET}")
        nav_text = f"Page {current_page + 1}/{total_pages}  |  "
        nav_text += f"{Colors.BRIGHT_YELLOW}h{Colors.RESET}:prev  "
        nav_text += f"{Colors.BRIGHT_YELLOW}l{Colors.RESET}:next  "
        nav_text += f"{Colors.BRIGHT_YELLOW}q{Colors.RESET}:quit"
        print(nav_text)
        print(f"{Colors.DIM}{'─' * cols}{Colors.RESET}")
        
        # Get single keypress
        ch = Input.getch()
        
        if ch == 'q' or ch == 'Q':
            break
        elif ch == 'h' or ch == 'H':
            if current_page > 0:
                current_page -= 1
        elif ch == 'l' or ch == 'L':
            if current_page < total_pages - 1:
                current_page += 1
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def show_paged_help(content_lines, title):
    """Display help content with dynamic paging based on terminal height"""
    rows, cols = get_terminal_size()
    
    # Reserve lines for header (3 lines) and navigation bar (4 lines)
    available_lines = rows - 7
    
    # Chunk the content
    pages = chunk_content(content_lines, available_lines)
    current_page = 0
    total_pages = len(pages)
    
    while True:
        clear_screen()
        
        # Header
        print(f"{Colors.BLUE_BG}{' ' * cols}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{Colors.BRIGHT_WHITE}{title:^{cols}}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{' ' * cols}{Colors.RESET}")
        print()
        
        # Display current page
        print(pages[current_page])
        
        # Navigation bar
        print()
        print(f"{Colors.DIM}{'─' * cols}{Colors.RESET}")
        nav_text = f"Page {current_page + 1}/{total_pages}  |  "
        nav_text += f"{Colors.BRIGHT_YELLOW}h{Colors.RESET}:prev  "
        nav_text += f"{Colors.BRIGHT_YELLOW}l{Colors.RESET}:next  "
        nav_text += f"{Colors.BRIGHT_YELLOW}q{Colors.RESET}:quit"
        print(nav_text)
        print(f"{Colors.DIM}{'─' * cols}{Colors.RESET}")
        
        # Get single keypress
        ch = getch()
        
        if ch == 'q' or ch == 'Q':
            break
        elif ch == 'h' or ch == 'H':
            if current_page > 0:
                current_page -= 1
        elif ch == 'l' or ch == 'L':
            if current_page < total_pages - 1:
                current_page += 1


def show_outline_editor_help():
    """Display comprehensive help for the Outline Editor"""
    
    content_lines = [
        f"{Colors.BRIGHT_CYAN}OVERVIEW{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "The Outline Editor is a hierarchical document editor that organizes content",
        "into headings, subheadings, and sentences. It uses simple commands to create",
        "and manage your outline structure.",
        "",
        f"{Colors.BRIGHT_CYAN}DOCUMENT STRUCTURE{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}Headings{Colors.RESET}      → Main topics (labeled [a], [b], [c], etc.)",
        f"  {Colors.BRIGHT_YELLOW}Subheadings{Colors.RESET}   → Subtopics under headings (labeled [a1], [a2], [b1], etc.)",
        f"  {Colors.BRIGHT_YELLOW}Sentences{Colors.RESET}     → Content items (numbered [1], [2], [3], etc.)",
        "",
        f"{Colors.BRIGHT_CYAN}HEADING COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}ha <name>{Colors.RESET}     Create or rename heading A",
        f"                 Example: {Colors.DIM}ha Introduction{Colors.RESET}",
        "",
        f"  {Colors.BRIGHT_YELLOW}ha{Colors.RESET}            Select existing heading A (clears subheading selection)",
        "                 Use this before adding sentences directly to a heading",
        "",
        f"  {Colors.BRIGHT_YELLOW}hb <name>{Colors.RESET}     Create or rename heading B",
        f"  {Colors.BRIGHT_YELLOW}hc <name>{Colors.RESET}     Create or rename heading C",
        "                 (and so on for d, e, f, etc.)",
        "",
        f"{Colors.BRIGHT_CYAN}SUBHEADING COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}ha1 <name>{Colors.RESET}    Create or rename subheading A1",
        f"                 Example: {Colors.DIM}ha1 Background{Colors.RESET}",
        "",
        f"  {Colors.BRIGHT_YELLOW}ha1{Colors.RESET}           Select existing subheading A1",
        "",
        f"  {Colors.BRIGHT_YELLOW}ha2 <name>{Colors.RESET}    Create or rename subheading A2",
        f"  {Colors.BRIGHT_YELLOW}hb1 <name>{Colors.RESET}    Create or rename subheading B1",
        "                 (and so on for any heading/subheading combination)",
        "",
        f"{Colors.BRIGHT_CYAN}SENTENCE COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}+ <text>{Colors.RESET}      Add a new sentence",
        "                 Adds to current subheading, or creates blank subheading",
        "                 under current heading if no subheading selected",
        f"                 Example: {Colors.DIM}+ This is my first sentence.{Colors.RESET}",
        "",
        f"  {Colors.BRIGHT_YELLOW}i <#> <text>{Colors.RESET}  Insert sentence before line number",
        f"                 Example: {Colors.DIM}i 3 This goes before line 3{Colors.RESET}",
        "",
        f"  {Colors.BRIGHT_YELLOW}e <#>{Colors.RESET}         Edit sentence at line number (vim-style editor)",
        f"                 Example: {Colors.DIM}e 5{Colors.RESET}",
        "",
        f"  {Colors.BRIGHT_YELLOW}d <#>{Colors.RESET}         Delete sentence at line number",
        f"                 Example: {Colors.DIM}d 7{Colors.RESET}",
        "",
        f"{Colors.BRIGHT_CYAN}VIM-STYLE INLINE EDITOR{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "When you use the 'e' command, you enter a vim-style editor:",
        "",
        f"  {Colors.BRIGHT_YELLOW}Normal Mode{Colors.RESET} (white cursor):",
        f"    {Colors.BRIGHT_YELLOW}i{Colors.RESET}           Insert at cursor position",
        f"    {Colors.BRIGHT_YELLOW}a{Colors.RESET}           Append after cursor",
        f"    {Colors.BRIGHT_YELLOW}A{Colors.RESET}           Append at end of line",
        f"    {Colors.BRIGHT_YELLOW}I{Colors.RESET}           Insert at beginning of line",
        f"    {Colors.BRIGHT_YELLOW}h / l{Colors.RESET}       Move cursor left / right",
        f"    {Colors.BRIGHT_YELLOW}0 / ${Colors.RESET}       Jump to beginning / end of line",
        f"    {Colors.BRIGHT_YELLOW}x{Colors.RESET}           Delete character at cursor",
        f"    {Colors.BRIGHT_YELLOW}d{Colors.RESET}           Delete word at cursor",
        f"    {Colors.BRIGHT_YELLOW}ESC{Colors.RESET}         Save changes and exit",
        f"    {Colors.BRIGHT_YELLOW}Enter{Colors.RESET}       Save changes and exit",
        f"    {Colors.BRIGHT_YELLOW}q{Colors.RESET}           Cancel without saving",
        "",
        f"  {Colors.BRIGHT_YELLOW}Insert Mode{Colors.RESET} (red cursor):",
        "    Type normally to insert text",
        f"    {Colors.BRIGHT_YELLOW}Backspace{Colors.RESET}   Delete previous character",
        f"    {Colors.BRIGHT_YELLOW}ESC{Colors.RESET}         Return to normal mode",
        f"    {Colors.BRIGHT_YELLOW}Enter{Colors.RESET}       Save and exit",
        "",
        f"{Colors.BRIGHT_CYAN}VIEW COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}@a{Colors.RESET}           Toggle collapse/expand heading A",
        f"  {Colors.BRIGHT_YELLOW}@b{Colors.RESET}           Toggle collapse/expand heading B",
        f"                 {Colors.DIM}[-]{Colors.RESET} = expanded, {Colors.DIM}[+]{Colors.RESET} = collapsed",
        "                 Collapsed headings hide their content to save screen space",
        "",
        f"  {Colors.BRIGHT_YELLOW}p{Colors.RESET}            Refresh/redraw the outline",
        "",
        f"{Colors.BRIGHT_CYAN}OTHER COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}q{Colors.RESET}            Quit and return to main menu",
        f"  {Colors.BRIGHT_YELLOW}F1{Colors.RESET}           Show this help screen",
        "",
        f"{Colors.BRIGHT_CYAN}TIPS & WORKFLOW{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "1. Create headings first: ha Introduction, hb Methods, hc Results",
        "2. Select a heading: ha",
        "3. Add sentences directly: + This is my opening sentence.",
        "4. Or create subheadings: ha1 Background, ha2 Purpose",
        "5. Select a subheading: ha1",
        "6. Add sentences: + Content goes here.",
        "7. Use @ commands to collapse sections you're not working on",
        "8. Use line numbers to edit, insert, or delete specific sentences",
        "",
        f"{Colors.BRIGHT_CYAN}EXAMPLE SESSION{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.DIM}> ha Introduction{Colors.RESET}          (create heading A)",
        f"  {Colors.DIM}> + Opening sentence{Colors.RESET}       (add sentence to heading A)",
        f"  {Colors.DIM}> ha1 Background{Colors.RESET}           (create subheading A1)",
        f"  {Colors.DIM}> + Background info here{Colors.RESET}   (add sentence to subheading A1)",
        f"  {Colors.DIM}> e 1{Colors.RESET}                      (edit sentence 1 with vim editor)",
        f"  {Colors.DIM}> @a{Colors.RESET}                       (collapse heading A)",
    ]
    
    show_paged_help(content_lines, "OUTLINE EDITOR - HELP")


def show_sentence_maintenance_help():
    """Display comprehensive help for Sentence Maintenance"""
    
    content_lines = [
        f"{Colors.BRIGHT_CYAN}OVERVIEW{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "Sentence Maintenance allows you to browse all projects and sentences in your",
        "database, and copy or move sentences between different locations.",
        "",
        f"{Colors.BRIGHT_CYAN}NAVIGATION{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}@a, @b, @c{Colors.RESET}   Toggle collapse/expand projects",
        f"                 {Colors.DIM}[-]{Colors.RESET} = expanded (showing content)",
        f"                 {Colors.DIM}[+]{Colors.RESET} = collapsed (hiding content)",
        "",
        f"  {Colors.BRIGHT_YELLOW}h{Colors.RESET}            Previous page of projects",
        f"  {Colors.BRIGHT_YELLOW}l{Colors.RESET}            Next page of projects",
        "                 (5 projects per page)",
        "",
        f"  {Colors.BRIGHT_YELLOW}p{Colors.RESET}            Refresh the display",
        "",
        f"{Colors.BRIGHT_CYAN}UNDERSTANDING IDs{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "When projects are expanded, you'll see:",
        "",
        f"  {Colors.BRIGHT_YELLOW}mc_id{Colors.RESET}        Major Category ID (heading)",
        f"  {Colors.BRIGHT_YELLOW}sc_id{Colors.RESET}        Subcategory ID (subheading)",
        f"  {Colors.BRIGHT_YELLOW}[###]{Colors.RESET}        Sentence ID (in green brackets)",
        "",
        "Example display:",
        f"  {Colors.CYAN}• Introduction{Colors.RESET} {Colors.DIM}(mc_id:{Colors.BRIGHT_YELLOW}5{Colors.DIM}){Colors.RESET}",
        f"    {Colors.DIM}→ Background{Colors.RESET} {Colors.DIM}(sc_id:{Colors.BRIGHT_YELLOW}12{Colors.DIM}){Colors.RESET}",
        f"      {Colors.BRIGHT_GREEN}[47]{Colors.RESET} This is the first sentence.",
        f"      {Colors.BRIGHT_GREEN}[48]{Colors.RESET} This is the second sentence.",
        "",
        "The IDs in bright yellow are what you use for copy/move commands.",
        "",
        f"{Colors.BRIGHT_CYAN}COPY SENTENCE{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}c <sentence_id> <target_sc_id>{Colors.RESET}",
        "",
        "  Copies a sentence to a different subcategory (can be in any project)",
        "  The original sentence remains in place",
        "",
        "  Example:",
        f"    {Colors.DIM}c 47 15{Colors.RESET}    Copy sentence 47 to subcategory 15",
        "",
        f"{Colors.BRIGHT_CYAN}MOVE SENTENCE{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}m <sentence_id> <target_sc_id>{Colors.RESET}",
        "",
        "  Moves a sentence to a different subcategory (can be in any project)",
        "  The sentence is removed from its original location",
        "  Sentence numbers are automatically reordered in both locations",
        "",
        "  Example:",
        f"    {Colors.DIM}m 48 20{Colors.RESET}    Move sentence 48 to subcategory 20",
        "",
        f"{Colors.BRIGHT_CYAN}TYPICAL WORKFLOW{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "1. Expand projects to see their content: @a, @b",
        "2. Note the sentence ID [###] you want to copy/move",
        "3. Note the target sc_id where you want it to go",
        "4. Use c or m command with those IDs",
        "5. The display will refresh showing the changes",
        "",
        f"{Colors.BRIGHT_CYAN}TIPS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "• You can copy/move sentences between different projects",
        "• Collapse projects you're not working with to reduce clutter",
        "• Use paging (h/l) if you have many projects",
        "• The sentence ID and sc_id are shown in bright yellow for easy reading",
        "",
        f"{Colors.BRIGHT_CYAN}OTHER COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}q{Colors.RESET}            Quit and return to main menu",
        f"  {Colors.BRIGHT_YELLOW}F1{Colors.RESET}           Show this help screen",
    ]
    
    show_paged_help(content_lines, "SENTENCE MAINTENANCE - HELP")


if __name__ == "__main__":
    print("This is a help module. Import and call show_outline_editor_help() or show_sentence_maintenance_help()")
