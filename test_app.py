#!/usr/bin/env python3
"""
Test script for Project Outline Manager
"""

import os
import sys
from project_outline_manager import ProjectOutlineManager

def test_application():
    """Test the basic functionality of the application"""
    
    # Use a test database
    test_db = "test_project_outlines.db"
    
    # Remove existing test database
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("="*80)
    print("Testing Project Outline Manager")
    print("="*80)
    
    # Initialize manager
    print("\n1. Initializing database...")
    manager = ProjectOutlineManager(test_db)
    print("   ✓ Database initialized")
    
    # Create a project
    print("\n2. Creating test project...")
    project_id = manager.create_project("Test Reflective Journal")
    if project_id:
        print(f"   ✓ Project created with ID: {project_id}")
    else:
        print("   ✗ Failed to create project")
        return False
    
    # Add major categories
    print("\n3. Adding major categories...")
    categories = [
        "Before Class Reflection",
        "After Class Reflection",
        "What is the method?"
    ]
    
    category_ids = []
    for cat_name in categories:
        cat_id = manager.add_major_category(project_id, cat_name)
        if cat_id:
            category_ids.append(cat_id)
            print(f"   ✓ Added: {cat_name}")
        else:
            print(f"   ✗ Failed to add: {cat_name}")
    
    # Add subcategories and sentences
    print("\n4. Adding subcategories and sentences...")
    
    # For first major category
    if len(category_ids) > 0:
        for i in range(1, 4):
            subcat_id = manager.add_subcategory(category_ids[0], str(i))
            if subcat_id:
                sentence = f"This is test sentence {i} for {categories[0]}"
                manager.update_sentence(subcat_id, sentence)
                print(f"   ✓ Added subcategory {i} with sentence")
    
    # For second major category
    if len(category_ids) > 1:
        for i in range(1, 3):
            subcat_id = manager.add_subcategory(category_ids[1], str(i))
            if subcat_id:
                sentence = f"This is test sentence {i} for {categories[1]}"
                manager.update_sentence(subcat_id, sentence)
                print(f"   ✓ Added subcategory {i} with sentence")
    
    # Display structure
    print("\n5. Displaying project structure...")
    manager.display_project_structure(project_id)
    
    # Test sentence update
    print("\n6. Testing sentence update...")
    sentences = manager.get_all_sentence_ids(project_id)
    if sentences:
        first_sentence_id = sentences[0][0]
        new_content = "This sentence has been updated successfully!"
        if manager.update_sentence(first_sentence_id, new_content):
            print(f"   ✓ Updated sentence ID {first_sentence_id}")
            updated_content = manager.get_sentence(first_sentence_id)
            print(f"   New content: {updated_content}")
        else:
            print("   ✗ Failed to update sentence")
    
    # List projects
    print("\n7. Listing all projects...")
    projects = manager.list_projects()
    for proj_id, proj_name, created_at in projects:
        print(f"   - {proj_name} (ID: {proj_id})")
    
    # Close connection
    manager.close()
    print("\n" + "="*80)
    print("All tests completed successfully!")
    print("="*80)
    print(f"\nTest database created: {test_db}")
    print("You can inspect it or delete it manually.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_application()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
