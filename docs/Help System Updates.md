# Help System Updates

## Changes Made

### 1. Dynamic Content Chunking Based on Terminal Height

The help system now automatically detects terminal height and chunks content to fit the available screen space:

- Uses `get_terminal_size()` to detect terminal dimensions
- Reserves 7 lines for headers and navigation bars
- Automatically calculates how many content lines fit per page
- Works with both horizontal and vertical monitors

**Implementation:**
- Added `chunk_content()` function that splits content into pages based on available lines
- Each page displays maximum content without scrolling
- Page count dynamically adjusts based on terminal size

### 2. Single-Key Navigation (No Enter Required)

Navigation in the help system now uses single keypresses:

- **h** - Previous page (no Enter needed)
- **l** - Next page (no Enter needed)  
- **q** - Quit help (no Enter needed)

**Implementation:**
- Added `getch()` function using `termios` and `tty` modules
- Reads single characters without waiting for Enter
- Provides immediate response to navigation commands

### 3. F1 Key Detection

Both `outline_editor.py` and `sentence_maintenance.py` now detect the actual F1 key:

- Pressing F1 key immediately opens help (no typing required)
- Detects F1 escape sequences: `\x1bOP` or `\x1b[11~`
- Works across different terminal emulators

**Implementation:**
- Added `getch()` function to both modules
- Modified command input loop to check first character for escape sequences
- If F1 detected, immediately shows help
- Otherwise, continues with normal command input

## Files Modified

1. **help.py**
   - Added `get_terminal_size()` for dynamic sizing
   - Added `getch()` for single-key input
   - Added `chunk_content()` for dynamic pagination
   - Updated `show_paged_help()` to use dynamic chunking and single-key navigation

2. **outline_editor.py**
   - Added `tty` and `termios` imports
   - Added `getch()` function
   - Modified command input loop to detect F1 keypress

3. **sentence_maintenance.py**
   - Added `sys`, `tty`, and `termios` imports
   - Added `getch()` function
   - Modified command input loop to detect F1 keypress

## User Experience Improvements

- **Adaptive Display**: Help content automatically adjusts to screen size
- **Faster Navigation**: No need to press Enter for h/l/q commands in help
- **Intuitive Help Access**: Press F1 key directly instead of typing "F1" + Enter
- **Better Space Utilization**: More content visible on larger screens, appropriate chunking on smaller screens
