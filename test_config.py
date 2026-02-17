#!/usr/bin/env python3
"""
Test script to verify configuration is being used correctly
"""

from config import DB_PATH, get_config
from database_utils import Database

print("=" * 60)
print("Configuration Test")
print("=" * 60)

# Test 1: Check DB_PATH constant
print(f"\n1. DB_PATH constant: {DB_PATH}")

# Test 2: Check config values
config = get_config()
print(f"2. Database home: {config.get('database-home')}")
print(f"3. Export directory: {config.get('export-directory')}")

# Test 3: Check Database class uses DB_PATH
db = Database()
print(f"4. Database instance path: {db.db_path}")

# Test 4: Verify they match
if db.db_path == DB_PATH:
    print("\n✓ SUCCESS: Database is using the configured path!")
else:
    print(f"\n✗ FAIL: Mismatch!")
    print(f"   DB_PATH: {DB_PATH}")
    print(f"   Database path: {db.db_path}")

# Test 5: Check file exists
import os
if os.path.exists(DB_PATH):
    size = os.path.getsize(DB_PATH)
    print(f"✓ Database file exists ({size} bytes)")
else:
    print(f"✗ Database file not found at {DB_PATH}")

db.close()

print("\n" + "=" * 60)
