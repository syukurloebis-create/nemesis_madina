#!/usr/bin/env python3
"""
Migrasi import evidence dari absolut ke relative/backend.

Menjalankan:
    python migrate_evidence_imports.py

Akan memperbaiki semua file yang memiliki import 'from evidence...'
"""

import os
import re
from pathlib import Path
from typing import List


class EvidenceImportMigrator:
    """
    Migrator untuk import evidence.
    """

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.evidence_dir = self.root / "backend" / "evidence"
        self.backend_dir = self.root / "backend"

        # Statistik
        self.files_fixed = 0
        self.files_skipped = 0
        self.errors = []

    def find_files_with_evidence_imports(self) -> List[Path]:
        """
        Cari semua file yang memiliki import 'from evidence...'
        """
        results = []

        for py_file in self.backend_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(r'from evidence\.', content) or re.search(r'from evidence import', content):
                        results.append(py_file)
            except Exception as e:
                self.errors.append(f"Error reading {py_file}: {e}")

        return results

    def is_inside_evidence(self, filepath: Path) -> bool:
        """Cek apakah file berada di dalam backend/evidence/"""
        return str(filepath).startswith(str(self.evidence_dir))

    def fix_file(self, filepath: Path) -> bool:
        """
        Perbaiki import di satu file.
        Returns True jika ada perubahan.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            is_inside = self.is_inside_evidence(filepath)

            if is_inside:
                # ============================================================
                # TIPE A: File di dalam backend/evidence/
                # Gunakan relative import
                # ============================================================

                # 1. from evidence.xxx → from .xxx
                content = re.sub(
                    r'from evidence\.([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from .\1',
                    content
                )

                # 2. from evidence.xxx.yyy → from .xxx.yyy
                content = re.sub(
                    r'from evidence\.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from .\1',
                    content
                )

                # 3. import evidence.xxx → import .xxx
                content = re.sub(
                    r'import evidence\.([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'import .\1',
                    content
                )

                # 4. from evidence import xxx → from . import xxx
                content = re.sub(
                    r'from evidence import ([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from . import \1',
                    content
                )

                # 5. import evidence → import .
                content = re.sub(
                    r'^import evidence$',
                    r'import .',
                    content,
                    flags=re.MULTILINE
                )
                content = re.sub(
                    r'import evidence\.',
                    r'import .',
                    content
                )

            else:
                # ============================================================
                # TIPE B: File di luar backend/evidence/
                # Gunakan from backend.evidence...
                # ============================================================

                # 1. from evidence.xxx → from backend.evidence.xxx
                content = re.sub(
                    r'from evidence\.([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from backend.evidence.\1',
                    content
                )

                # 2. from evidence.xxx.yyy → from backend.evidence.xxx.yyy
                content = re.sub(
                    r'from evidence\.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from backend.evidence.\1',
                    content
                )

                # 3. from evidence import xxx → from backend.evidence import xxx
                content = re.sub(
                    r'from evidence import ([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'from backend.evidence import \1',
                    content
                )

                # 4. import evidence → import backend.evidence
                content = re.sub(
                    r'^import evidence$',
                    r'import backend.evidence',
                    content,
                    flags=re.MULTILINE
                )
                content = re.sub(
                    r'import evidence\.',
                    r'import backend.evidence.',
                    content
                )

            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            self.errors.append(f"Error fixing {filepath}: {e}")
            return False

    def run(self):
        """Jalankan migrasi."""
        print("=" * 80)
        print("🔍 EVIDENCE IMPORT MIGRATOR")
        print("=" * 80)
        print(f"📁 Root: {self.root}")
        print(f"📁 Evidence dir: {self.evidence_dir}")
        print("=" * 80)

        print("\n🔍 Mencari file dengan import evidence...")
        files = self.find_files_with_evidence_imports()

        if not files:
            print("✅ Tidak ada file yang perlu diperbaiki.")
            return

        print(f"📄 Ditemukan {len(files)} file:")
        for f in files:
            print(f"  - {f.relative_to(self.root)}")

        print("\n🔧 Memperbaiki file...")

        for filepath in sorted(files):
            rel_path = filepath.relative_to(self.root)
            is_inside = self.is_inside_evidence(filepath)
            file_type = "📦 INSIDE" if is_inside else "📁 OUTSIDE"

            if self.fix_file(filepath):
                self.files_fixed += 1
                print(f"  ✅ [{file_type}] {rel_path}")
            else:
                self.files_skipped += 1
                print(f"  ⏭️ [{file_type}] {rel_path} (no changes)")

        print("\n" + "=" * 80)
        print("📊 LAPORAN")
        print("=" * 80)
        print(f"✅ Total file diperbaiki: {self.files_fixed}")
        print(f"⏭️ Total file dilewati: {self.files_skipped}")

        if self.errors:
            print(f"\n❌ Error ({len(self.errors)}):")
            for err in self.errors:
                print(f"  - {err}")

        print("=" * 80)

        if self.files_fixed > 0:
            print("\n🔍 Memverifikasi sisa import evidence...")
            remaining = self.find_files_with_evidence_imports()
            if remaining:
                print(f"⚠️ Masih ada {len(remaining)} file yang perlu diperbaiki:")
                for f in remaining:
                    print(f"  - {f.relative_to(self.root)}")
            else:
                print("✅ Semua import evidence telah diperbaiki!")


def main():
    """Main function."""
    script_dir = Path(__file__).parent if "__file__" in dir() else Path.cwd()

    root = script_dir
    while root != root.parent:
        if (root / "backend").exists():
            break
        root = root.parent

    migrator = EvidenceImportMigrator(str(root))
    migrator.run()


if __name__ == "__main__":
    main()