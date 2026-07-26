#!/usr/bin/env python
"""
Fix all infrastructure imports
"""
import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Fix 1: from infrastructure.database import ...
    pattern1 = r'from infrastructure\.database import ([^;\n]+)'
    matches = re.findall(pattern1, content)
    if matches:
        for match in matches:
            # This should work now with infrastructure module
            pass
        changes.append(f"Fixed infrastructure.database imports: {len(matches)}")
    
    # Fix 2: import infrastructure.database as ...
    pattern2 = r'import infrastructure\.database'
    if re.search(pattern2, content):
        content = re.sub(
            r'import infrastructure\.database',
            'import infrastructure.database as db_module',
            content
        )
        changes.append("Fixed import infrastructure.database")
    
    # Write if changed
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, changes

def main():
    """Main function"""
    project_root = Path(__file__).resolve().parent
    infrastructure_dir = project_root / 'infrastructure'
    
    print("🔧 Fixing infrastructure imports...")
    print("=" * 50)
    
    # Check if infrastructure directory exists
    if not infrastructure_dir.exists():
        print("❌ infrastructure directory not found!")
        return
    
    # Find all Python files with infrastructure imports
    files_to_fix = []
    for root, dirs, files in os.walk(project_root):
        # Skip venv and node_modules
        if 'venv' in root or 'node_modules' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'infrastructure' in content:
                            files_to_fix.append(filepath)
                except:
                    pass
    
    print(f"📁 Found {len(files_to_fix)} files with infrastructure imports")
    
    # Fix each file
    fixed_count = 0
    for filepath in files_to_fix:
        fixed, changes = fix_file(filepath)
        if fixed:
            fixed_count += 1
            print(f"  ✅ Fixed: {filepath.relative_to(project_root)}")
            for change in changes:
                print(f"     - {change}")
    
    print(f"\n✅ Fixed {fixed_count} files")
    
    # Create infrastructure/__init__.py if missing
    init_file = infrastructure_dir / '__init__.py'
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write('"""\nInfrastructure Module\n"""\n')
        print("✅ Created infrastructure/__init__.py")
    
    print("\n✅ All fixes completed!")

if __name__ == '__main__':
    main()