#!/bin/bash
# config.sh - Konfigurasi global untuk semua script Fase 0

# ============================================================================
# PATHS
# ============================================================================
PROJECT_ROOT="/c/Users/$(whoami)/nemesis-project"  # Sesuaikan dengan path proyek Anda
BACKUP_BASE_DIR="/c/backup/nemesis"
LOG_DIR="${PROJECT_ROOT}/fase0_logs"

# ============================================================================
# DATABASE CONFIGURATION (Sesuaikan dengan environment Anda)
# ============================================================================
DB_NAME="nemesis_db"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
# PGPASSWORD sebaiknya di-set via environment variable, jangan hardcode di sini

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
API_URL="http://localhost:8000"
WS_URL="ws://localhost:8000/ws"

# ============================================================================
# THRESHOLDS & TARGETS
# ============================================================================
TARGET_STARTUP_SECONDS=5
TARGET_WS_LATENCY_MS=100
TARGET_COVERAGE_PERCENT=90

# ============================================================================
# FLAGS (0=disabled, 1=enabled)
# ============================================================================
BACKUP_DATABASE=1
BACKUP_CODE=1
BACKUP_EVIDENCE=1
CLEANUP_DRY_RUN=0  # Set ke 1 untuk simulasi tanpa hapus
CREATE_BASELINE=1

# ============================================================================
# COLORS FOR OUTPUT
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_DIR}/execution.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_DIR}/execution.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_DIR}/execution.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "${LOG_DIR}/execution.log"
}

ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        log_info "Created directory: $1"
    fi
}

# Load custom environment if exists
if [ -f "${PROJECT_ROOT}/.env.fase0" ]; then
    source "${PROJECT_ROOT}/.env.fase0"
    log_info "Loaded custom environment from .env.fase0"
fi