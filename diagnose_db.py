#!/usr/bin/env python3
"""
Diagnostic script to check database path and size WITHOUT initializing it
"""

import os
from config import DB_PATH, get_config

print("=" * 70)
print("Database Path Diagnostic")
print("=" * 70)

# Get config
config = get_config()
db_home = config.get('database-home')

print(f"\n1. Raw config value for 'database-home':")
print(f"   '{db_home}'")
print(f"   (length: {len(db_home)} chars)")

print(f"\n2. After expanduser:")
expanded = os.path.expanduser(db_home)
print(f"   '{expanded}'")
print(f"   (length: {len(expanded)} chars)")

print(f"\n3. Final DB_PATH constant:")
print(f"   '{DB_PATH}'")
print(f"   (length: {len(DB_PATH)} chars)")

print(f"\n4. Check if file exists BEFORE opening:")
if os.path.exists(DB_PATH):
    size = os.path.getsize(DB_PATH)
    print(f"   ✓ File exists")
    print(f"   Size: {size} bytes ({size/1024:.1f} KB)")
else:
    print(f"   ✗ File does NOT exist")
    print(f"   (Database() would create a new empty one)")

# Check for backslashes in path
if '\\' in DB_PATH:
    print(f"\n5. WARNING: Path contains backslashes!")
    print(f"   This might cause issues on some systems")
    print(f"   Backslash count: {DB_PATH.count(chr(92))}")
    
    # Show the path with backslashes interpreted
    print(f"\n6. Path interpretation:")
    print(f"   Raw string: {repr(DB_PATH)}")
    print(f"   Display:    {DB_PATH}")

print("\n" + "=" * 70)
