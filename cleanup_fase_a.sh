#!/bin/bash
# NEMESIS MADINA - CLEANUP SCRIPT FASE A
# Hapus file duplikat tanpa menyentuh struktur penting

set -e  # Hentikan jika error

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NEMESIS MADINA - CLEANUP FASE A                        ║${NC}"
echo -e "${BLUE}║     Hapus File Duplikat & Konsolidasi Struktur             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Buat backup timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="../nemesis_backup_${TIMESTAMP}"
echo -e "${YELLOW}[1/8] Membuat backup ke: ${BACKUP_DIR}${NC}"
mkdir -p "${BACKUP_DIR}"
cp -r . "${BACKUP_DIR}" 2>/dev/null || true
echo -e "${GREEN}✓ Backup selesai${NC}"
echo ""

# 2. Hapus file Python duplikat di ROOT
echo -e "${YELLOW}[2/8] Menghapus file Python duplikat di ROOT...${NC}"
FILES_TO_REMOVE=(
    "api.py" "api_backup.py" "api_backup_*.py" "api_backup_before_persistence.py"
    "api_backup_final.py" "api_backup_hash.py" "api_current.py" "api_fix.py"
    "api_fixed.py" "api_new.py" "api_patched.py" "api_to_fix.py"
    "api_updated.py" "api_with_endpoints.py" "api_without_hash.py"
    "__init__.py" "__init__backup.py" "__init__clean.py"
    "__init__correct.py" "__init__final.py"
    "hash_utils.py" "hash_utils_backup.py" "hash_utils_fixed.py"
    "event_store.py" "event_store_backup.py" "event_store_chain.py"
    "main.py" "main_new.py" "main_backup.py"
    "models.py" "models_backup.py" "models_fixed.py"
    "patch.py" "patch_*.py" "fix.py" "fix_*.py"
    "update_api.py" "test_*.py" "temp_*.py" "tmp_*.py"
)

for pattern in "${FILES_TO_REMOVE[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            rm -f "$file"
            echo -e "  ${GREEN}✓ Hapus:${NC} $file"
        fi
    done
done
echo -e "${GREEN}✓ File duplikat di ROOT dihapus${NC}"
echo ""

# 3. Hapus folder duplikat di ROOT (jika ada)
echo -e "${YELLOW}[3/8] Menghapus folder duplikat di ROOT...${NC}"
DUPLICATE_FOLDERS=("cases" "core" "events" "evidence" "graph" "infrastructure")

for folder in "${DUPLICATE_FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        # Cek apakah di backend/ juga ada folder yang sama
        if [ -d "backend/$folder" ]; then
            rm -rf "$folder"
            echo -e "  ${GREEN}✓ Hapus folder duplikat:${NC} $folder (sudah ada di backend/)"
        else
            echo -e "  ${YELLOW}⚠ Lewati:${NC} $folder (tidak ditemukan di backend/, mungkin penting)"
        fi
    fi
done
echo ""

# 4. Bersihkan file cache Python
echo -e "${YELLOW}[4/8] Membersihkan cache Python...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Cache Python dibersihkan${NC}"
echo ""

# 5. Perbaiki struktur infrastructure (pilih Opsi A atau B)
echo -e "${YELLOW}[5/8] Memeriksa struktur infrastructure...${NC}"
if [ -d "backend/infrastructure/database" ] && [ -f "backend/infrastructure/database.py" ]; then
    echo -e "  ${YELLOW}⚠ Konflik terdeteksi: Ada folder database/ DAN file database.py${NC}"
    echo -e "  ${BLUE}Memilih Opsi A (pakai file database.py, hapus folder)${NC}"
    rm -rf "backend/infrastructure/database"
    echo -e "  ${GREEN}✓ Folder database/ dihapus, file database.py tetap${NC}"
elif [ -d "backend/infrastructure/database" ]; then
    echo -e "  ${GREEN}✓ Hanya ada folder database/ (Opsi B)${NC}"
elif [ -f "backend/infrastructure/database.py" ]; then
    echo -e "  ${GREEN}✓ Hanya ada file database.py (Opsi A)${NC}"
else
    echo -e "  ${RED}✗ Tidak ditemukan infrastructure/database! Perlu dibuat ulang${NC}"
fi
echo ""

# 6. Buat file __init__.py yang diperlukan jika hilang
echo -e "${YELLOW}[6/8] Memastikan __init__.py yang diperlukan ada...${NC}"
ensure_init() {
    local dir="$1"
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
        echo -e "  ${GREEN}✓ Buat:${NC} $dir/__init__.py"
    fi
}

ensure_init "backend"
ensure_init "backend/cases"
ensure_init "backend/core"
ensure_init "backend/infrastructure"
ensure_init "backend/routers"
echo ""

# 7. Tampilkan ringkasan
echo -e "${YELLOW}[7/8] Ringkasan setelah cleanup:${NC}"
echo ""
echo -e "${BLUE}File yang tersisa di ROOT:${NC}"
ls -la *.py 2>/dev/null | awk '{print "  " $9}' || echo "  (tidak ada file .py di ROOT)"
echo ""
echo -e "${BLUE}Folder di ROOT:${NC}"
ls -d */ 2>/dev/null | grep -v "backend" | grep -v "venv" | grep -v "node_modules" | \
    awk '{print "  " $1}' || echo "  (hanya backend/ yang tersisa)"
echo ""

# 8. Verifikasi import structure
echo -e "${YELLOW}[8/8] Verifikasi struktur import...${NC}"
if [ -f "backend/infrastructure/database.py" ]; then
    if grep -q "Base = declarative_base" backend/infrastructure/database.py; then
        echo -e "  ${GREEN}✓ database.py memiliki Base${NC}"
    else
        echo -e "  ${RED}✗ database.py tidak memiliki Base declarative_base()${NC}"
    fi
fi

if [ -f "backend/cases/models.py" ]; then
    if grep -q "from backend.infrastructure" backend/cases/models.py; then
        echo -e "  ${GREEN}✓ models.py import dari backend.infrastructure${NC}"
    else
        echo -e "  ${YELLOW}⚠ models.py perlu dicek importnya${NC}"
    fi
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     CLEANUP FASE A SELESAI!                                 ║${NC}"
echo -e "${GREEN}║                                                             ║${NC}"
echo -e "${GREEN}║  Backup disimpan di: ${BACKUP_DIR}${NC}"
echo -e "${GREEN}║                                                             ║${NC}"
echo -e "${GREEN}║  Langkah selanjutnya:                                       ║${NC}"
echo -e "${GREEN}║  1. docker-compose down                                     ║${NC}"
echo -e "${GREEN}║  2. docker-compose up --build -d                            ║${NC}"
echo -e "${GREEN}║  3. curl http://localhost:8000/health                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"