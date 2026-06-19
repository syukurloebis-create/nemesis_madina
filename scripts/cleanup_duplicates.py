#!/usr/bin/env python3
"""
Cleanup script for Nemesis Madina - Menghapus file duplikat dan tidak terpakai
WAJIB: Backup dulu sebelum running!
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# ============================================
# KONFIGURASI
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent
BACKUP_DIR = PROJECT_ROOT / f"../nemesis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# File yang TIDAK boleh dihapus di root
PROTECTED_ROOT_FILES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    ".env",
    ".env.production",
    "README.md",
    "alembic.ini",
    "requirements.txt",
    "pyproject.toml",
    "pytest.ini",
    ".gitignore",
    ".dockerignore",
    "prometheus.yml",
    "openapi.json",
}

# File duplikat yang HARUS dihapus dari root
DUPLICATE_ROOT_PATTERNS = [
    "api*.py",           # api_backup, api_fix, api_new, dll
    "__init__*.py",      # __init__backup, __init__clean, dll
    "hash_utils*.py",    # hash_utils_old, hash_utils_new, dll
    "event_store*.py",   # event_store di root
    "main*.py",          # main_new, main_backup, dll
    "models*.py",        # models_backup, models_fixed, dll
    "patch*.py",         # patch_api, patch_cases, dll
    "fix*.py",           # fix_api, fix_model, dll
    "update*.py",        # update_api, dll
    "canonical*.py",     # canonical.py di root
    "case_repository*.py",
    "persistence*.py",
    "scheduler*.py",
    "worker_outbox.py",
]

# Folder duplikat di root yang HARUS dihapus
DUPLICATE_ROOT_FOLDERS = [
    "cases/",      # karena sudah ada di backend/
    "core/",       # karena sudah ada di backend/
    "events/",     # karena sudah ada di backend/
    "evidence/",   # karena sudah ada di backend/
    "graph/",      # karena sudah ada di backend/
    "infrastructure/",  # conflict dengan backend/infrastructure/
    "lineage/",    # karena sudah ada di backend/
    "ml/",         # karena sudah ada di backend/
    "security/",   # karena sudah ada di backend/
    "websocket/",  # karena sudah ada di backend/
    "scripts/",    # JANGAN hapus? Ini folder penting
    "tests/",      # JANGAN hapus?
]

# Folder yang HARUS dipertahankan (jangan disentuh)
PROTECTED_FOLDERS = {
    "backend/",
    "frontend/",
    "venv/",
    "node_modules/",
    ".git/",
    ".github/",
    ".fase_status/",
    ".roadmap_status/",
    "backups/",
    "logs/",
    "reports/",
    "snapshots/",
    "grafana/",
    "k8s/",
    "migrations/",
    "alembic/",
    "htmlcov/",
    "metrics_exports/",
    "scripts/",      # keep scripts folder
    "tests/",        # keep tests folder
}

# File yang akan dipindahkan ke backup (bukan dihapus langsung)
FILES_TO_BACKUP_FIRST = [
    "api.py",
    "__init__.py",
    "main.py",
    "event_store.py",
    "hash_utils.py",
    "canonical.py",
]


# ============================================
# FUNCTIONS
# ============================================

def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_warning(text: str):
    print(f"⚠️  {text}")

def print_success(text: str):
    print(f"✅ {text}")

def print_info(text: str):
    print(f"📁 {text}")

def print_error(text: str):
    print(f"❌ {text}")

def create_backup_dir() -> bool:
    """Create backup directory"""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print_success(f"Backup directory created: {BACKUP_DIR}")
        return True
    except Exception as e:
        print_error(f"Cannot create backup dir: {e}")
        return False

def backup_file(file_path: Path) -> bool:
    """Backup a single file"""
    try:
        dest = BACKUP_DIR / file_path.name
        shutil.copy2(file_path, dest)
        return True
    except Exception as e:
        print_warning(f"Cannot backup {file_path}: {e}")
        return False

def find_files_to_cleanup() -> List[Path]:
    """Find duplicate files in root directory"""
    files_to_remove = []
    root_files = list(PROJECT_ROOT.glob("*.py"))
    
    for py_file in root_files:
        filename = py_file.name
        
        # Skip protected files
        if filename in PROTECTED_ROOT_FILES:
            continue
        
        # Check patterns
        for pattern in DUPLICATE_ROOT_PATTERNS:
            import fnmatch
            if fnmatch.fnmatch(filename, pattern):
                files_to_remove.append(py_file)
                break
    
    return files_to_remove

def find_folders_to_cleanup() -> List[Path]:
    """Find duplicate folders in root directory"""
    folders_to_remove = []
    
    for folder_name in DUPLICATE_ROOT_FOLDERS:
        folder_path = PROJECT_ROOT / folder_name.rstrip('/')
        if folder_path.exists() and folder_path.is_dir():
            # Skip if it's a protected folder
            if folder_name in PROTECTED_FOLDERS:
                continue
            folders_to_remove.append(folder_path)
    
    return folders_to_remove

def confirm_action(description: str, items: List) -> bool:
    """Ask for user confirmation"""
    if not items:
        return True
    
    print(f"\n📋 {description}: {len(items)} item(s)")
    for item in items[:10]:  # Show first 10 only
        print(f"   - {item}")
    if len(items) > 10:
        print(f"   ... and {len(items) - 10} more")
    
    response = input("\n❓ Apakah Anda ingin melanjutkan? (y/N): ").strip().lower()
    return response == 'y'

def cleanup_files(files: List[Path], dry_run: bool = True) -> Tuple[int, int]:
    """Remove duplicate files"""
    removed = 0
    failed = 0
    
    for file_path in files:
        try:
            if not dry_run:
                # Backup first
                backup_file(file_path)
                # Remove file
                file_path.unlink()
                print_success(f"Removed: {file_path.name}")
            else:
                print_info(f"Would remove: {file_path.name}")
            removed += 1
        except Exception as e:
            print_error(f"Failed to remove {file_path.name}: {e}")
            failed += 1
    
    return removed, failed

def cleanup_folders(folders: List[Path], dry_run: bool = True) -> Tuple[int, int]:
    """Remove duplicate folders"""
    removed = 0
    failed = 0
    
    for folder_path in folders:
        try:
            if not dry_run:
                # Backup folder contents first? Too big, just warn
                print_warning(f"Removing entire folder: {folder_path}")
                shutil.rmtree(folder_path)
                print_success(f"Removed folder: {folder_path}")
            else:
                print_info(f"Would remove folder: {folder_path}")
            removed += 1
        except Exception as e:
            print_error(f"Failed to remove {folder_path}: {e}")
            failed += 1
    
    return removed, failed

def fix_infrastructure_conflict():
    """Fix infrastructure/database conflict"""
    infra_dir = PROJECT_ROOT / "backend" / "infrastructure"
    db_folder = infra_dir / "database"
    db_file = infra_dir / "database.py"
    
    print_header("Fixing infrastructure conflict")
    
    if db_folder.exists() and db_folder.is_dir():
        print_info(f"Found folder: {db_folder}")
        if db_file.exists():
            print_info(f"Found file: {db_file} (will keep this)")
            # Optionally backup and remove folder
            response = input("\n❓ Hapus folder database/ dan gunakan database.py? (y/N): ")
            if response.lower() == 'y':
                backup_path = BACKUP_DIR / "database_folder_backup"
                shutil.copytree(db_folder, backup_path)
                print_success(f"Backed up folder to: {backup_path}")
                shutil.rmtree(db_folder)
                print_success(f"Removed folder: {db_folder}")
    elif db_file.exists():
        print_success(f"database.py exists (good)")
    else:
        print_warning("No infrastructure/database found - will create new")


# ============================================
# MAIN
# ============================================

def main():
    print_header("NEMESIS MADINA - CLEANUP SCRIPT")
    print_warning("PASTIKAN ANDA SUDAH MEMBUAT BACKUP MANUAL SEBELUM INI!")
    print_info(f"Backup akan dibuat di: {BACKUP_DIR}")
    
    # Check if running from correct directory
    if not (PROJECT_ROOT / "backend").exists():
        print_error("Script harus dijalankan dari root proyek Nemesis!")
        print_info(f"Current dir: {PROJECT_ROOT}")
        print_info("Silakan cd ke root proyek dulu")
        return
    
    response = input("\n❓ Lanjutkan cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print_info("Cleanup dibatalkan.")
        return
    
    # Create backup directory
    if not create_backup_dir():
        print_error("Cannot create backup. Aborting.")
        return
    
    # Find files to cleanup
    files = find_files_to_cleanup()
    folders = find_folders_to_cleanup()
    
    # Preview
    print_header("PREVIEW - DRY RUN")
    print_warning("Ini hanya preview, tidak ada yang dihapus")
    
    if files:
        print(f"\n📄 File yang akan dihapus ({len(files)}):")
        for f in files[:20]:
            print(f"   - {f.name}")
        if len(files) > 20:
            print(f"   ... dan {len(files)-20} file lainnya")
    
    if folders:
        print(f"\n📁 Folder yang akan dihapus ({len(folders)}):")
        for f in folders:
            print(f"   - {f}")
    
    # Ask for real cleanup
    print_header("REAL CLEANUP")
    response = input("❓ Apakah Anda yakin ingin menghapus file-file di atas? (y/N): ")
    if response.lower() != 'y':
        print_info("Cleanup dibatalkan.")
        return
    
    # Execute cleanup
    print_info("Menjalankan cleanup...")
    
    removed_files, failed_files = cleanup_files(files, dry_run=False)
    removed_folders, failed_folders = cleanup_folders(folders, dry_run=False)
    
    # Fix infrastructure conflict
    fix_infrastructure_conflict()
    
    # Clear cache
    print_info("Membersihkan __pycache__...")
    for pycache in PROJECT_ROOT.glob("**/__pycache__"):
        if "venv" not in str(pycache) and "node_modules" not in str(pycache):
            shutil.rmtree(pycache)
            print_success(f"Removed: {pycache}")
    
    # Summary
    print_header("CLEANUP SUMMARY")
    print_success(f"Files removed: {removed_files}")
    if failed_files > 0:
        print_warning(f"Files failed: {failed_files}")
    print_success(f"Folders removed: {removed_folders}")
    if failed_folders > 0:
        print_warning(f"Folders failed: {failed_folders}")
    
    print_success(f"\nBackup tersimpan di: {BACKUP_DIR}")
    print_warning("RESTART DOCKER untuk melihat perubahan")
    print_info("docker-compose down && docker-compose up --build")


if __name__ == "__main__":
    main()