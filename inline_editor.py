#!/usr/bin/env python3
"""
Inline editor with vim-style commands
"""

import sys
from ui_utils import Colors, Screen, Input


def edit_line_inline(line_num, current_text):
    """
    Edit a line with vim-style interface
    Cursor color: WHITE = normal mode, RED = insert mode
    Returns: (modified_text, cancelled)
    """
    text = current_text
    cursor_pos = len(text)
    mode = 'normal'
    
    # Print header
    print(f"\n{Colors.BRIGHT_CYAN}Editing line {line_num}{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}Commands: {Colors.BRIGHT_YELLOW}i{Colors.RESET}=insert {Colors.BRIGHT_YELLOW}a{Colors.RESET}=append {Colors.BRIGHT_YELLOW}x{Colors.RESET}=delete {Colors.BRIGHT_YELLOW}d{Colors.RESET}=delete word {Colors.BRIGHT_YELLOW}ESC{Colors.RESET}=save {Colors.BRIGHT_YELLOW}q{Colors.RESET}=cancel{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}Cursor: {Colors.BRIGHT_WHITE}WHITE{Colors.RESET}=normal {Colors.BRIGHT_RED}RED{Colors.RESET}=insert{Colors.RESET}\n")
    
    # Save the starting cursor position (row, col)
    start_row, start_col = Screen.get_cursor_position()
    
    def redraw():
        """Redraw the edit line from the saved position"""
        # Move cursor back to saved position
        Screen.move_cursor(start_row, start_col)
        # Clear from cursor to end of screen
        Screen.clear_from_cursor()
        
        # Show line number
        sys.stdout.write(f"{Colors.GREEN}[{line_num}]{Colors.RESET} ")
        
        # Choose cursor color based on mode
        if mode == 'insert':
            cursor_color = Colors.BRIGHT_RED
        else:
            cursor_color = Colors.BRIGHT_WHITE
        
        # Display text with colored cursor
        if cursor_pos < len(text):
            sys.stdout.write(text[:cursor_pos])
            sys.stdout.write(f"{cursor_color}{Colors.BOLD}{text[cursor_pos]}{Colors.RESET}")
            sys.stdout.write(text[cursor_pos+1:])
        else:
            sys.stdout.write(text)
            sys.stdout.write(f"{cursor_color}{Colors.BOLD} {Colors.RESET}")
        
        sys.stdout.flush()
    
    # Initial draw
    redraw()
    
    while True:
        ch = Input.getch()
        
        if mode == 'normal':
            if ch == 'i':
                mode = 'insert'
                redraw()
            
            elif ch == 'a':
                mode = 'insert'
                if cursor_pos < len(text):
                    cursor_pos += 1
                redraw()
            
            elif ch == 'A':
                mode = 'insert'
                cursor_pos = len(text)
                redraw()
            
            elif ch == 'I':
                mode = 'insert'
                cursor_pos = 0
                redraw()
            
            elif ch == 'x':
                if cursor_pos < len(text):
                    text = text[:cursor_pos] + text[cursor_pos+1:]
                    if cursor_pos >= len(text) and cursor_pos > 0:
                        cursor_pos -= 1
                redraw()
            
            elif ch == 'd':
                if cursor_pos < len(text):
                    next_space = text.find(' ', cursor_pos)
                    if next_space == -1:
                        text = text[:cursor_pos]
                    else:
                        text = text[:cursor_pos] + text[next_space+1:]
                    if cursor_pos >= len(text) and cursor_pos > 0:
                        cursor_pos = len(text)
                redraw()
            
            elif ch == 'h':
                if cursor_pos > 0:
                    cursor_pos -= 1
                redraw()
            
            elif ch == 'l':
                if cursor_pos < len(text):
                    cursor_pos += 1
                redraw()
            
            elif ch == '0':
                cursor_pos = 0
                redraw()
            
            elif ch == '$':
                cursor_pos = len(text)
                redraw()
            
            elif ch == '\x1b':
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Saved\n")
                return text, False
            
            elif ch == 'q':
                print(f"\n{Colors.YELLOW}Cancelled{Colors.RESET}\n")
                return current_text, True
            
            elif ch == '\r' or ch == '\n':
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Saved\n")
                return text, False
        
        elif mode == 'insert':
            if ch == '\x1b':
                mode = 'normal'
                if cursor_pos > 0 and cursor_pos >= len(text):
                    cursor_pos = len(text) - 1 if len(text) > 0 else 0
                redraw()
            
            elif ch == '\x7f' or ch == '\x08':
                if cursor_pos > 0:
                    text = text[:cursor_pos-1] + text[cursor_pos:]
                    cursor_pos -= 1
                redraw()
            
            elif ch == '\r' or ch == '\n':
                print(f"\n{Colors.GREEN}✓{Colors.RESET} Saved\n")
                return text, False
            
            elif ch >= ' ' and ch <= '~':
                text = text[:cursor_pos] + ch + text[cursor_pos:]
                cursor_pos += 1
                redraw()
