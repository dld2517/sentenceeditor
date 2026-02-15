# Vim-Style Editing Guide

## Overview

When you edit a line in the Outline Editor, it uses a vim-style inline editor that pulls the sentence to the cursor area for editing.

## How to Edit

1. Type `e 3` to edit line 3
2. The sentence appears at the cursor with vim-style commands
3. Edit the text using vim commands
4. Press ESC or Enter to save, or 'q' to cancel

## Vim Commands

### Modes

**Normal Mode** (default)
- Command mode for navigation and manipulation
- Shows `-- NORMAL --` indicator

**Insert Mode**
- Text entry mode
- Shows `-- INSERT --` indicator in green

### Normal Mode Commands

**Enter Insert Mode:**
- `i` - Insert at cursor
- `a` - Append after cursor
- `A` - Append at end of line
- `I` - Insert at beginning of line

**Navigation:**
- `h` - Move left (or left arrow)
- `l` - Move right (or right arrow)
- `0` - Jump to beginning of line
- `$` - Jump to end of line

**Deletion:**
- `x` - Delete character at cursor
- `d` - Delete word at cursor

**Save/Exit:**
- `ESC` - Save and exit
- `Enter` - Save and exit
- `q` - Cancel without saving

### Insert Mode Commands

**Text Entry:**
- Type normally to insert text
- `Backspace` - Delete previous character

**Exit Insert Mode:**
- `ESC` - Return to normal mode
- `Enter` - Save and exit

## Example Workflow

```
> e 3
Editing line 3
Commands: i=insert, a=append, x=delete char, d=delete word, ESC=save, q=cancel

[3] This is my sentence to edit  -- NORMAL --
```

**To change "my" to "your":**
1. Press `l` to move right to "m"
2. Press `d` to delete "my "
3. Press `i` to enter insert mode
4. Type "your "
5. Press `ESC` to save

**Result:** `This is your sentence to edit`

## Tips

- The cursor is shown as a highlighted character
- In normal mode, use navigation commands to position cursor
- In insert mode, type freely
- ESC always saves your changes
- Press 'q' in normal mode to cancel without saving
- The line number is shown in green for reference
