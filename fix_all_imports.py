#!/usr/bin/env python
"""
Fix all legacy imports
"""
import os
import re
from pathlib import Path

BACKEND_DIR = Path("backend")

# Mapping import lama → import baru
MAPPINGS = [
    (r'^from database\.', 'from backend.database.'),
    (r'^from security\.', 'from backend.security.'),
    (r'^from config\.', 'from backend.config.'),
    (r'^from cases\.', 'from backend.cases.'),
    (r'^from services\.', 'from backend.services.'),
    (r'^from routers\.', 'from backend.routers.'),
    (r'^from models\.', 'from backend.models.'),
    (r'^from schemas\.', 'from backend.schemas.'),
    (r'^from core\.', 'from backend.core.'),
    (r'^from infrastructure\.', 'from backend.infrastructure.'),
]

def fix_file(filepath):
    """Fix imports in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    for pattern, replacement in MAPPINGS:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            changes += 1
            content = new_content
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    return False, 0

def main():
    print("🧹 Cleaning imports...")
    print("=" * 40)
    
    total_files = 0
    total_changes = 0
    
    for root, dirs, files in os.walk(BACKEND_DIR):
        if '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                fixed, changes = fix_file(filepath)
                if fixed:
                    total_files += 1
                    total_changes += changes
                    print(f"  ✅ {filepath}")
    
    print("=" * 40)
    print(f"✅ Fixed {total_files} files, {total_changes} changes")

if __name__ == '__main__':
    main()
