#!/usr/bin/env python3
"""
Help System for Outline Management System
Provides detailed help documentation for outline_editor and sentence_maintenance
"""

import os
import sys


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_WHITE = '\033[97m'
    CYAN = '\033[36m'
    DIM = '\033[2m'
    BLUE_BG = '\033[44m'


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_terminal_size():
    """Get terminal size, default to 24x80 if unable to determine"""
    try:
        rows, cols = os.popen('stty size', 'r').read().split()
        return int(rows), int(cols)
    except:
        return 24, 80


def show_paged_help(pages, title):
    """Display help content with paging navigation"""
    current_page = 0
    total_pages = len(pages)
    
    while True:
        clear_screen()
        
        # Header
        print(f"{Colors.BLUE_BG}{' ' * 80}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{Colors.BRIGHT_WHITE}{title:^80}{Colors.RESET}")
        print(f"{Colors.BLUE_BG}{' ' * 80}{Colors.RESET}")
        print()
        
        # Display current page
        print(pages[current_page])
        
        # Navigation bar
        print()
        print(f"{Colors.DIM}{'─' * 80}{Colors.RESET}")
        nav_text = f"Page {current_page + 1}/{total_pages}  |  "
        nav_text += f"{Colors.BRIGHT_YELLOW}h{Colors.RESET}:prev  "
        nav_text += f"{Colors.BRIGHT_YELLOW}l{Colors.RESET}:next  "
        nav_text += f"{Colors.BRIGHT_YELLOW}q{Colors.RESET}:quit"
        print(nav_text)
        print(f"{Colors.DIM}{'─' * 80}{Colors.RESET}")
        
        # Get user input
        cmd = input(f"{Colors.BRIGHT_GREEN}> {Colors.RESET}").strip().lower()
        
        if cmd == 'q':
            break
        elif cmd == 'h' and current_page > 0:
            current_page -= 1
        elif cmd == 'l' and current_page < total_pages - 1:
            current_page += 1


def show_outline_editor_help():
    """Display comprehensive help for the Outline Editor"""
    
    pages = []
    
    # Page 1: Overview and Structure
    page1 = f"""{Colors.BRIGHT_CYAN}OVERVIEW{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
The Outline Editor is a hierarchical document editor that organizes content
into headings, subheadings, and sentences. It uses simple commands to create
and manage your outline structure.

{Colors.BRIGHT_CYAN}DOCUMENT STRUCTURE{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}Headings{Colors.RESET}      → Main topics (labeled [a], [b], [c], etc.)
  {Colors.BRIGHT_YELLOW}Subheadings{Colors.RESET}   → Subtopics under headings (labeled [a1], [a2], [b1], etc.)
  {Colors.BRIGHT_YELLOW}Sentences{Colors.RESET}     → Content items (numbered [1], [2], [3], etc.)"""
    pages.append(page1)
    
    # Page 2: Heading Commands
    page2 = f"""{Colors.BRIGHT_CYAN}HEADING COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}ha <name>{Colors.RESET}     Create or rename heading A
                 Example: {Colors.DIM}ha Introduction{Colors.RESET}

  {Colors.BRIGHT_YELLOW}ha{Colors.RESET}            Select existing heading A (clears subheading selection)
                 Use this before adding sentences directly to a heading

  {Colors.BRIGHT_YELLOW}hb <name>{Colors.RESET}     Create or rename heading B
  {Colors.BRIGHT_YELLOW}hc <name>{Colors.RESET}     Create or rename heading C
                 (and so on for d, e, f, etc.)

{Colors.BRIGHT_CYAN}SUBHEADING COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}ha1 <name>{Colors.RESET}    Create or rename subheading A1
                 Example: {Colors.DIM}ha1 Background{Colors.RESET}

  {Colors.BRIGHT_YELLOW}ha1{Colors.RESET}           Select existing subheading A1

  {Colors.BRIGHT_YELLOW}ha2 <name>{Colors.RESET}    Create or rename subheading A2
  {Colors.BRIGHT_YELLOW}hb1 <name>{Colors.RESET}    Create or rename subheading B1
                 (and so on for any heading/subheading combination)"""
    pages.append(page2)
    
    # Page 3: Sentence Commands
    page3 = f"""{Colors.BRIGHT_CYAN}SENTENCE COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}+ <text>{Colors.RESET}      Add a new sentence
                 Adds to current subheading, or creates blank subheading
                 under current heading if no subheading selected
                 Example: {Colors.DIM}+ This is my first sentence.{Colors.RESET}

  {Colors.BRIGHT_YELLOW}i <#> <text>{Colors.RESET}  Insert sentence before line number
                 Example: {Colors.DIM}i 3 This goes before line 3{Colors.RESET}

  {Colors.BRIGHT_YELLOW}e <#>{Colors.RESET}         Edit sentence at line number (vim-style editor)
                 Example: {Colors.DIM}e 5{Colors.RESET}

  {Colors.BRIGHT_YELLOW}d <#>{Colors.RESET}         Delete sentence at line number
                 Example: {Colors.DIM}d 7{Colors.RESET}"""
    pages.append(page3)
    
    # Page 4: Vim Editor
    page4 = f"""{Colors.BRIGHT_CYAN}VIM-STYLE INLINE EDITOR{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
When you use the 'e' command, you enter a vim-style editor:

  {Colors.BRIGHT_YELLOW}Normal Mode{Colors.RESET} (white cursor):
    {Colors.BRIGHT_YELLOW}i{Colors.RESET}           Insert at cursor position
    {Colors.BRIGHT_YELLOW}a{Colors.RESET}           Append after cursor
    {Colors.BRIGHT_YELLOW}A{Colors.RESET}           Append at end of line
    {Colors.BRIGHT_YELLOW}I{Colors.RESET}           Insert at beginning of line
    {Colors.BRIGHT_YELLOW}h / l{Colors.RESET}       Move cursor left / right
    {Colors.BRIGHT_YELLOW}0 / ${Colors.RESET}       Jump to beginning / end of line
    {Colors.BRIGHT_YELLOW}x{Colors.RESET}           Delete character at cursor
    {Colors.BRIGHT_YELLOW}d{Colors.RESET}           Delete word at cursor
    {Colors.BRIGHT_YELLOW}ESC{Colors.RESET}         Save changes and exit
    {Colors.BRIGHT_YELLOW}Enter{Colors.RESET}       Save changes and exit
    {Colors.BRIGHT_YELLOW}q{Colors.RESET}           Cancel without saving

  {Colors.BRIGHT_YELLOW}Insert Mode{Colors.RESET} (red cursor):
    Type normally to insert text
    {Colors.BRIGHT_YELLOW}Backspace{Colors.RESET}   Delete previous character
    {Colors.BRIGHT_YELLOW}ESC{Colors.RESET}         Return to normal mode
    {Colors.BRIGHT_YELLOW}Enter{Colors.RESET}       Save and exit"""
    pages.append(page4)
    
    # Page 5: View and Other Commands
    page5 = f"""{Colors.BRIGHT_CYAN}VIEW COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}@a{Colors.RESET}           Toggle collapse/expand heading A
  {Colors.BRIGHT_YELLOW}@b{Colors.RESET}           Toggle collapse/expand heading B
                 {Colors.DIM}[-]{Colors.RESET} = expanded, {Colors.DIM}[+]{Colors.RESET} = collapsed
                 Collapsed headings hide their content to save screen space

  {Colors.BRIGHT_YELLOW}p{Colors.RESET}            Refresh/redraw the outline

{Colors.BRIGHT_CYAN}OTHER COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}q{Colors.RESET}            Quit and return to main menu
  {Colors.BRIGHT_YELLOW}F1{Colors.RESET}           Show this help screen"""
    pages.append(page5)
    
    # Page 6: Tips & Workflow
    page6 = f"""{Colors.BRIGHT_CYAN}TIPS & WORKFLOW{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
1. Create headings first: ha Introduction, hb Methods, hc Results
2. Select a heading: ha
3. Add sentences directly: + This is my opening sentence.
4. Or create subheadings: ha1 Background, ha2 Purpose
5. Select a subheading: ha1
6. Add sentences: + Content goes here.
7. Use @ commands to collapse sections you're not working on
8. Use line numbers to edit, insert, or delete specific sentences

{Colors.BRIGHT_CYAN}EXAMPLE SESSION{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.DIM}> ha Introduction{Colors.RESET}          (create heading A)
  {Colors.DIM}> + Opening sentence{Colors.RESET}       (add sentence to heading A)
  {Colors.DIM}> ha1 Background{Colors.RESET}           (create subheading A1)
  {Colors.DIM}> + Background info here{Colors.RESET}   (add sentence to subheading A1)
  {Colors.DIM}> e 1{Colors.RESET}                      (edit sentence 1 with vim editor)
  {Colors.DIM}> @a{Colors.RESET}                       (collapse heading A)"""
    pages.append(page6)
    
    show_paged_help(pages, "OUTLINE EDITOR - HELP")


def show_sentence_maintenance_help():
    """Display comprehensive help for Sentence Maintenance"""
    
    pages = []
    
    # Page 1: Overview and Navigation
    page1 = f"""{Colors.BRIGHT_CYAN}OVERVIEW{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
Sentence Maintenance allows you to browse all projects and sentences in your
database, and copy or move sentences between different locations.

{Colors.BRIGHT_CYAN}NAVIGATION{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}@a, @b, @c{Colors.RESET}   Toggle collapse/expand projects
                 {Colors.DIM}[-]{Colors.RESET} = expanded (showing content)
                 {Colors.DIM}[+]{Colors.RESET} = collapsed (hiding content)

  {Colors.BRIGHT_YELLOW}h{Colors.RESET}            Previous page of projects
  {Colors.BRIGHT_YELLOW}l{Colors.RESET}            Next page of projects
                 (5 projects per page)

  {Colors.BRIGHT_YELLOW}p{Colors.RESET}            Refresh the display"""
    pages.append(page1)
    
    # Page 2: Understanding IDs
    page2 = f"""{Colors.BRIGHT_CYAN}UNDERSTANDING IDs{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
When projects are expanded, you'll see:

  {Colors.BRIGHT_YELLOW}mc_id{Colors.RESET}        Major Category ID (heading)
  {Colors.BRIGHT_YELLOW}sc_id{Colors.RESET}        Subcategory ID (subheading)
  {Colors.BRIGHT_YELLOW}[###]{Colors.RESET}        Sentence ID (in green brackets)

Example display:
  {Colors.CYAN}• Introduction{Colors.RESET} {Colors.DIM}(mc_id:{Colors.BRIGHT_YELLOW}5{Colors.DIM}){Colors.RESET}
    {Colors.DIM}→ Background{Colors.RESET} {Colors.DIM}(sc_id:{Colors.BRIGHT_YELLOW}12{Colors.DIM}){Colors.RESET}
      {Colors.BRIGHT_GREEN}[47]{Colors.RESET} This is the first sentence.
      {Colors.BRIGHT_GREEN}[48]{Colors.RESET} This is the second sentence.

The IDs in bright yellow are what you use for copy/move commands."""
    pages.append(page2)
    
    # Page 3: Copy and Move Commands
    page3 = f"""{Colors.BRIGHT_CYAN}COPY SENTENCE{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}c <sentence_id> <target_sc_id>{Colors.RESET}

  Copies a sentence to a different subcategory (can be in any project)
  The original sentence remains in place

  Example:
    {Colors.DIM}c 47 15{Colors.RESET}    Copy sentence 47 to subcategory 15

{Colors.BRIGHT_CYAN}MOVE SENTENCE{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}m <sentence_id> <target_sc_id>{Colors.RESET}

  Moves a sentence to a different subcategory (can be in any project)
  The sentence is removed from its original location
  Sentence numbers are automatically reordered in both locations

  Example:
    {Colors.DIM}m 48 20{Colors.RESET}    Move sentence 48 to subcategory 20"""
    pages.append(page3)
    
    # Page 4: Workflow and Tips
    page4 = f"""{Colors.BRIGHT_CYAN}TYPICAL WORKFLOW{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
1. Expand projects to see their content: @a, @b
2. Note the sentence ID [###] you want to copy/move
3. Note the target sc_id where you want it to go
4. Use c or m command with those IDs
5. The display will refresh showing the changes

{Colors.BRIGHT_CYAN}TIPS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
• You can copy/move sentences between different projects
• Collapse projects you're not working with to reduce clutter
• Use paging (h/l) if you have many projects
• The sentence ID and sc_id are shown in bright yellow for easy reading

{Colors.BRIGHT_CYAN}OTHER COMMANDS{Colors.RESET}
{Colors.DIM}{'─' * 80}{Colors.RESET}
  {Colors.BRIGHT_YELLOW}q{Colors.RESET}            Quit and return to main menu
  {Colors.BRIGHT_YELLOW}F1{Colors.RESET}           Show this help screen"""
    pages.append(page4)
    
    show_paged_help(pages, "SENTENCE MAINTENANCE - HELP")


if __name__ == "__main__":
    print("This is a help module. Import and call show_outline_editor_help() or show_sentence_maintenance_help()")
