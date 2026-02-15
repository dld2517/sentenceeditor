# Installation Guide

## Quick Installation

### Step 1: Extract Files

Extract the archive to your desired location:

**For .tar.gz:**
```bash
tar -xzf outline_manager_v2.tar.gz
cd outline_app_package
```

**For .zip:**
```bash
unzip outline_manager_v2.zip
cd outline_app_package
```

### Step 2: Install Dependencies

Install the required Python package:

```bash
pip3 install -r requirements.txt
```

Or install manually:

```bash
pip3 install python-docx
```

### Step 3: Run the Application

```bash
python3 main.py
```

## System Requirements

- **Python**: Version 3.7 or higher
- **Operating System**: Linux, macOS, or Windows with WSL
- **Terminal**: Any terminal emulator with ANSI color support
- **Disk Space**: Minimal (< 1 MB for application, database grows with content)

## Verifying Installation

After installation, run:

```bash
python3 --version
```

Should show Python 3.7 or higher.

Then run:

```bash
python3 -c "import docx; print('Dependencies OK')"
```

Should print "Dependencies OK" without errors.

## First Run

On first run:

1. The application will create `project_outlines.db` in the current directory
2. You'll be prompted to create a new project or select an existing one
3. Follow the on-screen prompts to start creating your outline

## Optional: Make Executable

For easier launching, make the main script executable:

```bash
chmod +x main.py
```

Then you can run it directly:

```bash
./main.py
```

## Troubleshooting

### "No module named 'docx'"

Install python-docx:
```bash
pip3 install python-docx
```

### "Permission denied"

Make the script executable:
```bash
chmod +x main.py
```

### Colors not displaying

Ensure your terminal supports ANSI colors. Try a different terminal emulator like:
- Linux: GNOME Terminal, Konsole, Alacritty
- macOS: Terminal.app, iTerm2
- Windows: Windows Terminal, WSL with any Linux terminal

### F1 key not working

Some terminals map F1 to help or other functions. The application detects common F1 escape sequences (`\x1bOP` and `\x1b[11~`). Check your terminal's keyboard settings.

## Uninstallation

To remove the application:

1. Delete the application directory
2. Optionally remove the database file (`project_outlines.db`) if you want to delete all your data
3. Uninstall the Python package if not needed elsewhere:
   ```bash
   pip3 uninstall python-docx
   ```

## Upgrading

To upgrade to a new version:

1. **Backup your database**: Copy `project_outlines.db` to a safe location
2. Extract the new version to a new directory
3. Copy your old `project_outlines.db` to the new directory
4. Run the new version

The application automatically handles database migrations.

## Getting Help

- Press **F1** in the application for context-sensitive help
- Read the **README.md** for detailed usage instructions
- Check the command bar at the bottom of each screen for available commands
