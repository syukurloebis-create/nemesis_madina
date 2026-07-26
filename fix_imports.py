#!/usr/bin/env python
"""
Fix all legacy imports in backend
"""
import os
import re
import shutil
from pathlib import Path

BACKEND_DIR = Path("backend")
BACKUP_DIR = Path("backup_import_fix_python")

# Buat backup
BACKUP_DIR.mkdir(exist_ok=True)

# Mapping import lama → import baru
IMPORT_MAPPING = [
    (r'^from database\.', 'from backend.database.'),
    (r'^from security\.', 'from backend.security.'),
    (r'^from config\.', 'from backend.config.'),
    (r'^from schemas\.', 'from backend.schemas.'),
    (r'^from core\.', 'from backend.core.'),
    (r'^from infrastructure\.', 'from backend.infrastructure.'),
    (r'^from utils\.', 'from backend.utils.'),
]

def fix_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    for pattern, replacement in IMPORT_MAPPING:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            changes += 1
            content = new_content
    
    if content != original:
        # Backup
        backup_path = BACKUP_DIR / filepath.name
        shutil.copy2(filepath, backup_path)
        
        # Write
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, 0

def main():
    """Main function"""
    print("🔧 Fixing imports...")
    print("=" * 40)
    
    total_files = 0
    total_changes = 0
    
    for root, dirs, files in os.walk(BACKEND_DIR):
        # Skip __pycache__
        if '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                fixed, changes = fix_file(filepath)
                if fixed:
                    total_files += 1
                    total_changes += changes
                    print(f"  ✅ Fixed: {filepath}")
    
    print("=" * 40)
    print(f"✅ Fixed {total_files} files, {total_changes} changes")

if __name__ == '__main__':
    main()
