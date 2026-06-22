#!/bin/bash

echo "🔧 MENGUBAH SEMUA IMPORT DARI types/evidence KE services/evidenceApi..."

# Cari semua file yang mengimport dari types/evidence
for file in $(grep -l "from.*types/evidence" --include="*.ts" --include="*.tsx" src/ 2>/dev/null); do
  echo "  Memperbaiki: $file"
  sed -i 's|from.*types/evidence|from "../services/evidenceApi"|g' "$file"
  sed -i 's|from.*types/evidence|from "../../services/evidenceApi"|g' "$file"
  sed -i 's|from.*types/evidence|from "../../../services/evidenceApi"|g' "$file"
done

echo "✅ Selesai!"
