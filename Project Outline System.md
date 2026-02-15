# Project Outline System

A comprehensive SQLite-based hierarchical outline management system with multiple interfaces.

## Quick Start

```bash
python3 main.py
```

## Components

### 1. Main Launcher (`main.py`)
Central hub that provides access to all tools:
- Outline Editor (modern interface)
- Project Manager (traditional menus)
- Export to Text (backup/sharing)

### 2. Outline Editor (`outline_editor.py`)
Modern word-processor style interface with:
- Color-coded display
- Command-based editing
- Three-level hierarchy: Headings → Subheadings → Sentences
- Real-time visual feedback

**Commands:**
- `ha <name>` - Create/edit heading A
- `ha1 <name>` - Create/edit subheading A1
- `+ <text>` - Add sentence
- `e <#> <text>` - Edit line
- `d <#>` - Delete line
- `p` - Refresh view
- `q` - Quit

### 3. Project Manager (`project_outline_manager.py`)
Traditional menu-driven interface for:
- Creating and managing projects
- Building hierarchical structures
- Organizing content systematically

### 4. Export Tool (`export_to_text.py`)
Export projects to plain text files:
- Preserves hierarchy
- Readable format
- Easy sharing

## Database

All tools share the same SQLite database: `project_outlines.db`

**Schema:**
- `projects` - Project names and metadata
- `major_categories` - Top-level headings
- `subcategories` - Subheadings under major categories
- `sentences` - Content for each subcategory

## Features

- **Persistent Storage** - All data saved to SQLite
- **Multiple Projects** - Manage many projects in one database
- **Hierarchical Structure** - Three levels: Major → Sub → Sentences
- **Color Interface** - Modern, readable display
- **Cross-Compatible** - All tools work with same data
- **Export Ready** - Easy backup and sharing

## Workflow Example

1. Run `python3 main.py`
2. Select **Outline Editor** (option 1)
3. Create or select a project
4. Build your outline:
   - `ha Before Class Reflection`
   - `ha1 Introduction`
   - `+ This is my first sentence`
   - `+ This is my second sentence`
5. Export when done (option 3 from main menu)

## Requirements

- Python 3.6+
- SQLite3 (included with Python)
- Terminal with ANSI color support
