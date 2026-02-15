#!/usr/bin/env python3
"""Quick test of the outline editor"""

import os
from outline_editor import OutlineEditor

# Remove test database if exists
test_db = "test_editor.db"
if os.path.exists(test_db):
    os.remove(test_db)

print("Testing Outline Editor...")
print("="*80)

# Create editor
editor = OutlineEditor(test_db)

# Create project
print("\n1. Creating project...")
project_id = editor.create_project("Test Journal")
print(f"   Project ID: {project_id}")

# Add major category
print("\n2. Adding major category...")
mc_id = editor.get_or_create_major_category(project_id, "Before Class Reflection")
print(f"   Major Category ID: {mc_id}")

# Add sentences
print("\n3. Adding sentences...")
editor.add_sentence(mc_id, "This is the first sentence.")
editor.add_sentence(mc_id, "This is the second sentence.")
editor.add_sentence(mc_id, "This is the third sentence.")
print("   Added 3 sentences")

# Add another major category
print("\n4. Adding another major category...")
mc_id2 = editor.get_or_create_major_category(project_id, "After Class Reflection")
editor.add_sentence(mc_id2, "Post-class sentence one.")
editor.add_sentence(mc_id2, "Post-class sentence two.")
print("   Added 2 more sentences")

# Get all lines
print("\n5. Retrieving all lines...")
lines = editor.get_all_lines(project_id)
print(f"   Total lines: {len(lines)}")

print("\n6. Displaying outline:")
print("="*80)
current_major = None
for idx, (s_id, major_cat, subcat, content, mc_order, sc_order) in enumerate(lines, 1):
    if major_cat != current_major:
        if current_major is not None:
            print()
        print(f"\n{major_cat}")
        print("-" * len(major_cat))
        current_major = major_cat
    print(f"[{idx}] {content}")
print("="*80)

# Test update
print("\n7. Testing update...")
first_sentence_id = lines[0][0]
editor.update_sentence(first_sentence_id, "This sentence has been UPDATED!")
print(f"   Updated sentence ID {first_sentence_id}")

# Verify update
lines = editor.get_all_lines(project_id)
print(f"   New content: {lines[0][3]}")

editor.close()
print("\n✓ All tests passed!")
print(f"\nTest database: {test_db}")
