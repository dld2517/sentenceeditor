# Sentence Editor - Usage Guide

## Quick Start

```bash
python3 main.py
```

## System Overview

The Project Outline System consists of four integrated modules that share a common database and active project state.

### Main Launcher (`main.py`)

The central hub displays the active project and provides access to all tools. When you select a project in the Project Manager, it becomes the active project for the Outline Editor.

### Outline Editor (`outline_editor.py`)

Modern word-processor interface with commands at the bottom of the screen.

**Workflow:**
1. Launch from main menu or run directly
2. Select or create a project (uses active project if set)
3. Build your outline using commands

**Commands:**
- `ha <name>` - Create/edit heading A
- `ha1 <name>` - Create/edit subheading A1 under heading A
- `+ <text>` - Add sentence to current subheading
- `e 3 New text` - Edit line 3
- `d 5` - Delete line 5
- `p` - Refresh display
- `q` - Quit

**Color Scheme:**
- Blue header bar - Project name
- Bright cyan - Section titles
- Bright blue - Major headings [a], [b]
- Cyan - Subheadings [a1], [a2]
- Green - Line numbers
- Bright white - Content text
- Bright yellow - Command keys
- Red - Errors

### Project Manager (`project_outline_manager.py`)

Traditional menu interface for project management.

**Features:**
- Create new projects
- Select project (sets as active for Editor)
- List all projects
- Delete projects

**Integration:**
When you select a project here, it automatically becomes the active project. The next time you open the Outline Editor, it will use this project.

### Export Tool (`export_to_text.py`)

Export any project to a plain text file.

**Output Format:**
```
PROJECT: Your Project Name
================================================================================

Before Class Reflection
-----------------------
Introduction. First sentence here

Main Points. Another sentence here


After Class Reflection
----------------------
Summary. Final thoughts here
```

## Typical Workflow

1. **First Time Setup**
   ```bash
   python3 main.py
   # Select option 2 (Project Manager)
   # Create a new project
   # It will ask if you want to set it as active - say yes
   ```

2. **Daily Writing**
   ```bash
   python3 main.py
   # Select option 1 (Outline Editor)
   # Your active project loads automatically
   # Start writing with commands
   ```

3. **Switch Projects**
   ```bash
   python3 main.py
   # Select option 2 (Project Manager)
   # Select a different project
   # Return to Outline Editor - new project is now active
   ```

4. **Export Work**
   ```bash
   python3 main.py
   # Select option 3 (Export to Text)
   # Choose project and filename
   ```

## Database

All data is stored in `project_outlines.db` (SQLite).

**Active Project State:**
Stored in `.project_state.json` - tracks which project is currently active.

## Tips

- No need to press Enter twice - commands execute immediately
- Standard text uses bright white for better readability
- All tools share the same database
- Active project persists between sessions
- You can run tools directly without the main launcher
