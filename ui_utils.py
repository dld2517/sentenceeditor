#!/usr/bin/env python3
"""
UI Utilities - Centralized color, screen, and UI management
"""

import os
import sys
import tty
import termios


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'
    BLUE_BG = '\033[44m'  # Alias for compatibility


class Screen:
    """Screen management utilities"""
    
    @staticmethod
    def clear():
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    @staticmethod
    def get_size():
        """Get terminal size (rows, columns)"""
        try:
            size = os.get_terminal_size()
            return size.lines, size.columns
        except:
            return 24, 80
    
    @staticmethod
    def get_cursor_position():
        """Get current cursor position (row, col)"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdout.write('\033[6n')
            sys.stdout.flush()
            
            # Read response: ESC [ row ; col R
            response = ''
            while True:
                ch = sys.stdin.read(1)
                response += ch
                if ch == 'R':
                    break
            
            # Parse response
            if response.startswith('\033[') and response.endswith('R'):
                coords = response[2:-1].split(';')
                return int(coords[0]), int(coords[1])
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return 1, 1
    
    @staticmethod
    def move_cursor(row, col):
        """Move cursor to specific position"""
        sys.stdout.write(f'\033[{row};{col}H')
        sys.stdout.flush()
    
    @staticmethod
    def clear_line():
        """Clear the current line"""
        print('\r\033[K', end='', flush=True)
    
    @staticmethod
    def clear_from_cursor():
        """Clear from cursor to end of screen"""
        sys.stdout.write('\033[J')
        sys.stdout.flush()


class Input:
    """Input utilities"""
    
    @staticmethod
    def getch():
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    @staticmethod
    def read_command_with_f1(prompt="> "):
        """
        Read a command with help detection (? or help)
        Uses regular input() for full line editing with backspace
        Returns: (command_string, is_help_requested)
        """
        cmd = input(f"{Colors.BRIGHT_GREEN}{prompt}{Colors.RESET}").strip()
        
        # Check if user wants help
        if cmd.lower() in ['?', 'help']:
            return '', True
        
        return cmd, False


class UI:
    """Common UI elements"""
    
    @staticmethod
    def print_header(title, project_name=None):
        """Print a full-width blue header"""
        rows, cols = Screen.get_size()
        
        print(f"\n{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")
        
        if project_name:
            header_text = f"  {title}: {project_name}"
        else:
            header_text = f"  {title}"
        
        padding = " " * (cols - len(header_text))
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}{header_text}{padding}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{Colors.BOLD}" + " "*cols + f"{Colors.RESET}")
    
    @staticmethod
    def print_separator(char="─"):
        """Print a separator line"""
        rows, cols = Screen.get_size()
        print(f"{Colors.DIM}{char * cols}{Colors.RESET}")
    
    @staticmethod
    def print_command_bar(commands):
        """
        Print a command bar with list of commands
        commands: list of tuples (key, suffix, description)
        Example: [("h", "a <name>", "heading"), ("q", "", "quit")]
        """
        rows, cols = Screen.get_size()
        
        cmd_parts = []
        for item in commands:
            if len(item) == 2:
                # Simple format: (key, description)
                key, desc = item
                cmd_parts.append(f"{Colors.BRIGHT_YELLOW}{key}{Colors.RESET}:{desc}")
            else:
                # Full format: (prefix, suffix, description)
                prefix, suffix, desc = item
                cmd_parts.append(f"{Colors.BRIGHT_YELLOW}{prefix}{suffix}{Colors.RESET}:{desc}")
        
        cmd_line = "  ".join(cmd_parts)
        
        print(f"\n{Colors.DIM}{'─' * cols}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLUE}{cmd_line}{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * cols}{Colors.RESET}")
    
    @staticmethod
    def print_context(heading_name=None, heading_key=None, subheading_name=None, subheading_key=None):
        """Print current context (selected heading/subheading)"""
        context_parts = []
        
        if heading_name and heading_key:
            context_parts.append(f"Heading: {Colors.BRIGHT_BLUE}[{heading_key}]{Colors.RESET} {Colors.BRIGHT_WHITE}{heading_name}{Colors.RESET}")
        
        if subheading_name and subheading_key:
            context_parts.append(f"Subheading: {Colors.CYAN}[{subheading_key}]{Colors.RESET} {Colors.BRIGHT_CYAN}{subheading_name}{Colors.RESET}")
        
        if context_parts:
            context = " | ".join(context_parts)
        else:
            context = f"{Colors.DIM}No heading selected{Colors.RESET}"
        
        print(f"{context}")
    
    @staticmethod
    def success(message):
        """Print a success message"""
        print(f"\n{Colors.GREEN}✓{Colors.RESET} {message}")
    
    @staticmethod
    def error(message):
        """Print an error message"""
        print(f"\n{Colors.RED}Error:{Colors.RESET} {message}")
    
    @staticmethod
    def info(message):
        """Print an info message"""
        print(f"\n{Colors.CYAN}ℹ{Colors.RESET} {message}")
    
    @staticmethod
    def warning(message):
        """Print a warning message"""
        print(f"\n{Colors.YELLOW}⚠{Colors.RESET} {message}")
