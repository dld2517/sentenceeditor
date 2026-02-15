# Outline Management System

A Python-based hierarchical outline and project management application with a modern terminal UI. Create structured documents with headings, subheadings, and sentences, then export to text or APA7-formatted Word documents.

## Features

- **Hierarchical Structure**: Organize content into headings → subheadings → sentences
- **Vim-Style Editing**: Inline editor with familiar vim commands for natural text editing
- **Collapsible Sections**: Use @a, @b toggles to collapse/expand headings for better focus
- **Modern Terminal UI**: Color-coded interface with blue headers, bright yellow commands, cyan highlights
- **Multiple Projects**: Manage multiple independent projects in a single database
- **Sentence Management**: Copy and move sentences between projects with tree view navigation
- **Export Options**: Export to plain text or APA7-formatted Word documents (.docx)
- **Comprehensive Help**: Press F1 key for context-sensitive help with dynamic paging
- **Smart Navigation**: Single-key commands and paging (h/l) for efficient workflow

## Installation

### Requirements

- Python 3.7 or higher
- Terminal with ANSI color support
- Unix-like environment (Linux, macOS, WSL on Windows)

### Setup

1. Extract all files to a directory
2. Install dependencies:

```bash
pip3 install -r requirements.txt
```

Or install manually:

```bash
pip3 install python-docx
```

3. Make the main script executable (optional):

```bash
chmod +x main.py
```

## Quick Start

Run the application:

```bash
python3 main.py
```

From the main menu, you can:
- **1**: Open Outline Editor (create and edit content)
- **2**: Manage Projects (view, switch, or delete projects)
- **3**: Sentence Maintenance (copy/move sentences between projects)
- **4**: Export to Text (plain text format)
- **5**: Export to Word (APA7-formatted .docx)
- **Q**: Quit

## Using the Outline Editor

### Creating Structure

Create headings in sequence:
```
> ha Introduction
> hb Methods
> hc Results
```

Create subheadings under a heading:
```
> ha1 Background
> ha2 Purpose
```

### Adding Content

Select a heading or subheading, then add sentences:
```
> ha              (select heading A)
> + This is a sentence directly under the heading.
> ha1             (select subheading A1)
> + This is a sentence under subheading A1.
```

### Editing Commands

- `+ <text>` - Add new sentence
- `i <#> <text>` - Insert sentence before line number
- `e <#>` - Edit sentence (opens vim-style editor)
- `d <#>` - Delete sentence
- `@a`, `@b` - Toggle collapse/expand headings
- `p` - Refresh display
- `F1` - Show help (press the F1 key)
- `q` - Quit to main menu

### Vim-Style Inline Editor

When editing a sentence with `e <#>`:

**Normal Mode** (white cursor):
- `i` - Insert at cursor
- `a` - Append after cursor
- `A` - Append at end of line
- `I` - Insert at beginning
- `h`/`l` - Move cursor left/right
- `0`/`$` - Jump to start/end
- `x` - Delete character
- `d` - Delete word
- `ESC` or `Enter` - Save and exit
- `q` - Cancel without saving

**Insert Mode** (red cursor):
- Type normally to insert text
- `Backspace` - Delete previous character
- `ESC` - Return to normal mode
- `Enter` - Save and exit

## Sentence Maintenance

View all projects and sentences in a collapsible tree structure. Copy or move sentences between any locations:

- `@a`, `@b` - Toggle project collapse/expand
- `h`/`l` - Navigate pages (5 projects per page)
- `c <sentence_id> <target_sc_id>` - Copy sentence
- `m <sentence_id> <target_sc_id>` - Move sentence
- `F1` - Show help
- `q` - Quit

IDs are displayed in bright yellow when projects are expanded:
- `mc_id` - Major category (heading) ID
- `sc_id` - Subcategory (subheading) ID
- `[###]` - Sentence ID (in green brackets)

## Export Formats

### Plain Text Export

Exports the outline structure as plain text with hierarchical indentation.

### APA7 Word Export

Creates a professionally formatted Word document with:
- Times New Roman 12pt font
- Double-spacing throughout
- Left-justified paragraphs
- Plain formatting (no bold/italic headings)
- Proper paragraph spacing

## Database

All data is stored in `project_outlines.db` (SQLite3). The database structure:

- **projects** - Top-level projects
- **major_categories** - Headings within projects
- **subcategories** - Subheadings within headings
- **sentences** - Content items within subcategories

The database file is automatically excluded from git via `.gitignore`.

## File Structure

```
outline_manager/
├── main.py                      # Main launcher
├── outline_editor.py            # Outline editing module
├── project_outline_manager.py   # Project management module
├── sentence_maintenance.py      # Sentence copy/move module
├── export_to_text.py           # Export functionality
├── inline_editor.py            # Vim-style inline editor
├── help.py                     # Help system with F1 support
├── project_state.py            # Shared state management
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Tips and Best Practices

1. **Start with Structure**: Create all your headings first, then fill in content
2. **Use Collapse**: Collapse sections you're not working on to reduce visual clutter
3. **Direct Sentences**: Headings can have both direct sentences and named subheadings
4. **Case Sensitivity**: Heading and subheading names are case-sensitive
5. **Line Numbers**: Line numbers in the editor are sequential across the entire document
6. **F1 Help**: Press F1 anytime for context-sensitive help with dynamic paging
7. **Single Keys**: In help screens, use h/l/q without pressing Enter

## Keyboard Shortcuts Summary

### Outline Editor
- `F1` - Help
- `ha <name>` - Create/rename heading A
- `ha1 <name>` - Create/rename subheading A1
- `+ <text>` - Add sentence
- `e <#>` - Edit sentence
- `@a` - Toggle collapse heading A
- `q` - Quit

### Sentence Maintenance
- `F1` - Help
- `@a` - Toggle project A
- `h`/`l` - Previous/next page
- `c <id> <id>` - Copy sentence
- `m <id> <id>` - Move sentence
- `q` - Quit

### Help System
- `h` - Previous page (no Enter)
- `l` - Next page (no Enter)
- `q` - Quit help (no Enter)

## Troubleshooting

**Colors not displaying**: Ensure your terminal supports ANSI colors. Most modern terminals do.

**F1 key not working**: Some terminal emulators map F1 differently. The system detects both `\x1bOP` and `\x1b[11~` sequences.

**Database locked**: Only one instance should access the database at a time. Close other instances.

**Terminal size detection**: The help system automatically detects terminal size. If it fails, it defaults to 24x80.

## Git Integration

The included `.gitignore` excludes:
- `*.db` - Database files
- `*.db-journal` - SQLite journal files
- `.project_state.json` - Active project state
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files

This allows you to version control your code while keeping project data local.

## License

This is free and unencumbered software released into the public domain.

## Version

Version 2.0 - Updated with dynamic help system, F1 key support, and adaptive terminal sizing.
