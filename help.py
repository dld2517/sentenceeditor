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
        "Sentence Maintenance allows you to browse all projects, headings, and sentences",
        "in your database. You can copy sentences and headings, and delete headings.",
        "",
        f"{Colors.BRIGHT_CYAN}NAVIGATION{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}@x{Colors.RESET}           Toggle collapse/expand for project x (a, b, c, etc.)",
        "                 Collapsed projects show only the project name",
        "                 Expanded projects show all headings, subheadings, and sentences",
        "",
        f"  {Colors.BRIGHT_YELLOW}h{Colors.RESET}            Previous page",
        f"  {Colors.BRIGHT_YELLOW}l{Colors.RESET}            Next page",
        "",
        f"{Colors.BRIGHT_CYAN}UNDERSTANDING IDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "Each element has an ID shown in bright yellow:",
        "",
        f"  {Colors.BRIGHT_BLUE}[a]{Colors.RESET} My Project {Colors.DIM}(proj_id:{Colors.BRIGHT_YELLOW}1{Colors.DIM}){Colors.RESET}",
        f"    {Colors.CYAN}\u2022 Introduction{Colors.RESET} {Colors.DIM}(mc_id:{Colors.BRIGHT_YELLOW}5{Colors.DIM}){Colors.RESET}",
        f"      {Colors.BRIGHT_BLACK}\u2192 Background{Colors.RESET} {Colors.DIM}(sc_id:{Colors.BRIGHT_YELLOW}12{Colors.DIM}){Colors.RESET}",
        f"        {Colors.BRIGHT_GREEN}[47]{Colors.RESET} This is the first sentence.",
        f"        {Colors.BRIGHT_GREEN}[48]{Colors.RESET} This is the second sentence.",
        "",
        "• proj_id = Project ID",
        "• mc_id = Major Category (Heading) ID",
        "• sc_id = Subcategory (Subheading) ID",
        "• [##] = Sentence ID",
        "",
        f"{Colors.BRIGHT_CYAN}SENTENCE COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}cs <sentence_id> <sc_id>{Colors.RESET}",
        "  Copy sentence to a subheading (any project)",
        "  The sentence remains in its original location",
        "  Example:",
        f"    {Colors.DIM}cs 48 20{Colors.RESET}     Copy sentence 48 to subheading sc_id:20",
        "",
        f"{Colors.BRIGHT_CYAN}HEADING COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}ch <mc_id> <before_mc_id>{Colors.RESET}",
        "  Copy heading before another heading (same project)",
        "  Copies all subheadings and sentences",
        "  Example:",
        f"    {Colors.DIM}ch 5 3{Colors.RESET}      Copy heading mc_id:5 before mc_id:3",
        "",
        f"  {Colors.BRIGHT_YELLOW}cp <mc_id> <proj_id>{Colors.RESET}",
        "  Copy heading to another project",
        "  Copies all subheadings and sentences to end of target project",
        "  Example:",
        f"    {Colors.DIM}cp 5 2{Colors.RESET}      Copy heading mc_id:5 to project proj_id:2",
        "",
        f"  {Colors.BRIGHT_YELLOW}dh <mc_id>{Colors.RESET}",
        "  Delete heading (and all its subheadings and sentences)",
        "  Example:",
        f"    {Colors.DIM}dh 5{Colors.RESET}        Delete heading mc_id:5",
        "",
        f"{Colors.BRIGHT_CYAN}TYPICAL WORKFLOWS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "Copy sentence to another location:",
        "  1. Expand projects: @a, @b",
        "  2. Note sentence ID [###] and target sc_id",
        "  3. Use: cs 48 20",
        "",
        "Move sentence (copy then delete):",
        "  1. Copy: cs 48 20",
        "  2. Delete original from outline editor: d 48",
        "",
        "Reorder heading within project:",
        "  1. Copy before target: ch 5 3",
        "  2. Delete original: dh 5",
        "",
        "Move heading to another project:",
        "  1. Copy to project: cp 5 2",
        "  2. Delete original: dh 5",
        "",
        f"{Colors.BRIGHT_CYAN}TIPS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        "• IDs are shown in bright yellow: proj_id, mc_id, sc_id, sentence [id]",
        "• Copy operations are safer than move - you can delete after verifying",
        "• Collapse projects you're not working with to reduce clutter",
        "• Use paging (h/l) if you have many projects",
        "• Delete heading (dh) removes all subheadings and sentences - be careful!",
        "",
        f"{Colors.BRIGHT_CYAN}OTHER COMMANDS{Colors.RESET}",
        f"{Colors.DIM}{'─' * 80}{Colors.RESET}",
        f"  {Colors.BRIGHT_YELLOW}q{Colors.RESET}            Quit and return to main menu",
        f"  {Colors.BRIGHT_YELLOW}?{Colors.RESET}            Show this help screen",
    ]
    
    show_paged_help(content_lines, "SENTENCE MAINTENANCE - HELP")



if __name__ == "__main__":
    print("This is a help module. Import and call show_outline_editor_help() or show_sentence_maintenance_help()")
