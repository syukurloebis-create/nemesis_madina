"""
Backup & Recovery Script
"""
import os
import sys
import shutil
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import subprocess
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupManager:
    """
    Backup and Recovery Manager
    """

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self) -> Dict[str, Any]:
        """Create a full system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        logger.info(f"Creating backup at {backup_path}")

        backup_metadata = {
            "timestamp": datetime.now().isoformat(),
            "version": "8.1.0",
            "files": [],
            "database": None,
            "config": None
        }

        # 1. Backup database
        try:
            db_backup = self._backup_database(backup_path)
            backup_metadata["database"] = db_backup
        except Exception as e:
            logger.error(f"Database backup failed: {e}")

        # 2. Backup configuration
        try:
            config_backup = self._backup_config(backup_path)
            backup_metadata["config"] = config_backup
        except Exception as e:
            logger.error(f"Config backup failed: {e}")

        # 3. Backup critical files
        try:
            files_backup = self._backup_files(backup_path)
            backup_metadata["files"] = files_backup
        except Exception as e:
            logger.error(f"Files backup failed: {e}")

        # Save metadata
        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(backup_metadata, f, indent=2, default=str)

        logger.info(f"Backup completed: {backup_path}")
        return backup_metadata

    def _backup_database(self, backup_path: Path) -> str:
        """Backup database"""
        db_path = Path("nemesis.db")
        if not db_path.exists():
            logger.warning("Database file not found")
            return ""

        db_backup = backup_path / "nemesis.db"
        shutil.copy2(db_path, db_backup)

        # Also backup SQLite schema
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            schema = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()

            schema_file = backup_path / "schema.sql"
            with open(schema_file, "w") as f:
                for row in schema:
                    if row[0]:
                        f.write(f"{row[0]};\n\n")
            conn.close()
        except Exception as e:
            logger.error(f"Schema backup failed: {e}")

        return str(db_backup)

    def _backup_config(self, backup_path: Path) -> str:
        """Backup configuration"""
        config_files = [
            ".env",
            "backend/config.py",
            "backend/settings.py"
        ]

        config_dir = backup_path / "config"
        config_dir.mkdir(exist_ok=True)

        for file in config_files:
            src = Path(file)
            if src.exists():
                dst = config_dir / src.name
                shutil.copy2(src, dst)

        return str(config_dir)

    def _backup_files(self, backup_path: Path) -> List[str]:
        """Backup critical files"""
        critical_dirs = [
            "backend/intelligence",
            "backend/graph",
            "backend/evidence",
            "backend/audit",
            "frontend/src",
            "migrations"
        ]

        files_dir = backup_path / "files"
        files_dir.mkdir(exist_ok=True)

        backed_up = []

        for dir_path in critical_dirs:
            src = Path(dir_path)
            if src.exists():
                dst = files_dir / src.name
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    backed_up.append(str(dst))
                else:
                    shutil.copy2(src, dst)
                    backed_up.append(str(dst))

        return backed_up

    def restore_backup(self, backup_path: Path) -> bool:
        """Restore from backup"""
        metadata_file = backup_path / "metadata.json"
        if not metadata_file.exists():
            logger.error(f"Metadata file not found: {metadata_file}")
            return False

        with open(metadata_file) as f:
            metadata = json.load(f)

        logger.info(f"Restoring backup from {backup_path}")

        # 1. Restore database
        if metadata.get("database"):
            db_backup = Path(metadata["database"])
            if db_backup.exists():
                shutil.copy2(db_backup, "nemesis.db")
                logger.info("Database restored")

        # 2. Restore config
        if metadata.get("config"):
            config_dir = Path(metadata["config"])
            if config_dir.exists():
                for file in config_dir.iterdir():
                    shutil.copy2(file, Path.cwd() / file.name)
                logger.info("Configuration restored")

        # 3. Restore files
        files_dir = backup_path / "files"
        if files_dir.exists():
            for dir_path in files_dir.iterdir():
                dst = Path.cwd() / dir_path.name
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(dir_path, dst)
            logger.info("Files restored")

        logger.info("Restore completed")
        return True

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    backups.append({
                        "path": str(backup_dir),
                        "timestamp": metadata.get("timestamp"),
                        "version": metadata.get("version", "unknown")
                    })
        return backups


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NEMESIS Backup Manager")
    parser.add_argument("--create", action="store_true", help="Create backup")
    parser.add_argument("--list", action="store_true", help="List backups")
    parser.add_argument("--restore", type=str, help="Restore from backup path")
    args = parser.parse_args()

    manager = BackupManager()

    if args.create:
        result = manager.create_backup()
        print(f"✅ Backup created: {result['timestamp']}")
        print(f"   Path: {manager.backup_dir}/backup_{result['timestamp']}")

    elif args.list:
        backups = manager.list_backups()
        print("\n📋 Available Backups:")
        for backup in backups:
            print(f"  📁 {backup['path']}")
            print(f"     📅 {backup['timestamp']}")
            print(f"     📦 {backup['version']}")

    elif args.restore:
        backup_path = Path(args.restore)
        if manager.restore_backup(backup_path):
            print("✅ Restore completed successfully")
        else:
            print("❌ Restore failed")

    else:
        print("Usage:")
        print("  python backup.py --create")
        print("  python backup.py --list")
        print("  python backup.py --restore <backup_path>")