#!/usr/bin/env python3
"""
Export Project Outline Database to Plain Text File
"""

import sqlite3
import os
import sys


def list_projects(db_path):
    """List all projects in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at FROM projects ORDER BY created_at DESC")
    projects = cursor.fetchall()
    
    conn.close()
    return projects


def export_project_to_text(db_path, project_id, output_file):
    """Export a project to a plain text file"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get project info
    cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    
    if not project:
        print(f"Error: Project with ID {project_id} not found.")
        conn.close()
        return False
    
    project_name = project[0]
    
    # Open output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write project header
        f.write(f"PROJECT: {project_name}\n")
        f.write("=" * 80 + "\n\n")
        
        # Get all major categories
        cursor.execute("""
            SELECT id, name, sort_order 
            FROM major_categories 
            WHERE project_id = ? 
            ORDER BY sort_order
        """, (project_id,))
        
        major_categories = cursor.fetchall()
        
        for mc_id, mc_name, mc_order in major_categories:
            # Write major category header
            f.write(f"{mc_name}\n")
            f.write("-" * len(mc_name) + "\n")
            
            # Get all subcategories for this major category
            cursor.execute("""
                SELECT sc.id, sc.name, s.content
                FROM subcategories sc
                LEFT JOIN sentences s ON sc.id = s.subcategory_id
                WHERE sc.major_category_id = ?
                ORDER BY sc.sort_order
            """, (mc_id,))
            
            subcategories = cursor.fetchall()
            
            for sc_id, sc_name, content in subcategories:
                # Write subcategory and sentence with line feed
                sentence_text = content if content else "(empty)"
                f.write(f"{sc_name}. {sentence_text}\n\n")
            
            # Extra line feed after each major category
            f.write("\n")
    
    conn.close()
    return True


def main():
    """Main function"""
    db_path = "project_outlines.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        print("Make sure you're running this script in the same directory as your database.")
        sys.exit(1)
    
    # List available projects
    projects = list_projects(db_path)
    
    if not projects:
        print("No projects found in the database.")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("EXPORT PROJECT TO TEXT FILE")
    print("="*80)
    
    print("\nAvailable Projects:")
    for idx, (proj_id, proj_name, created_at) in enumerate(projects, 1):
        print(f"{idx}. {proj_name} (Created: {created_at})")
    
    # Select project
    while True:
        try:
            choice = input("\nEnter project number to export: ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(projects):
                project_id = projects[choice_num - 1][0]
                project_name = projects[choice_num - 1][1]
                break
            else:
                print("Invalid project number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get output filename
    default_filename = f"{project_name.replace(' ', '_')}.txt"
    output_file = input(f"\nEnter output filename (default: {default_filename}): ").strip()
    
    if not output_file:
        output_file = default_filename
    
    # Add .txt extension if not present
    if not output_file.endswith('.txt'):
        output_file += '.txt'
    
    # Export
    print(f"\nExporting project '{project_name}' to '{output_file}'...")
    
    if export_project_to_text(db_path, project_id, output_file):
        print(f"\n✓ Export successful!")
        print(f"File saved: {os.path.abspath(output_file)}")
    else:
        print("\n✗ Export failed.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExport cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
