#!/bin/bash
# ============================================================================
# NEMESIS FASE 0 - Emergency Rollback
# ============================================================================

source "$(dirname "$0")/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                  NEMESIS EMERGENCY ROLLBACK                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Parameter
ROLLBACK_VERSION="${1:-latest}"

if [ "$ROLLBACK_VERSION" == "latest" ]; then
    ROLLBACK_DIR="${BACKUP_BASE_DIR}/latest"
else
    ROLLBACK_DIR="${BACKUP_BASE_DIR}/${ROLLBACK_VERSION}"
fi

if [ ! -d "$ROLLBACK_DIR" ]; then
    log_error "Backup not found: ${ROLLBACK_DIR}"
    echo ""
    echo "Available backups:"
    ls -la "${BACKUP_BASE_DIR}/" 2>/dev/null | grep "^d" | awk '{print $9}'
    exit 1
fi

log_info "Rollback target: ${ROLLBACK_DIR}"
log_warning "This will RESTORE system to previous state!"

echo ""
read -p "Are you sure you want to proceed? (type 'RESTORE' to confirm): " CONFIRM

if [ "$CONFIRM" != "RESTORE" ]; then
    log_info "Rollback cancelled."
    exit 0
fi

# ============================================================================
# 1. Stop Services
# ============================================================================
log_info "Stopping services..."

# Detect service manager
if command -v systemctl &> /dev/null; then
    sudo systemctl stop nemesis-api 2>/dev/null
    sudo systemctl stop nemesis-worker 2>/dev/null
    sudo systemctl stop nemesis-websocket 2>/dev/null
elif command -v docker &> /dev/null; then
    docker stop $(docker ps -q --filter "name=nemesis") 2>/dev/null
fi

log_success "Services stopped"

# ============================================================================
# 2. Restore Code
# ============================================================================
log_info "Restoring source code..."

BACKUP_CODE="${ROLLBACK_DIR}/code/code_backup.tar.gz"

if [ -f "$BACKUP_CODE" ]; then
    # Backup current state before restore
    CURRENT_BACKUP="${BACKUP_BASE_DIR}/pre_rollback_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$CURRENT_BACKUP/code"
    
    # Backup current code
    tar -czf "${CURRENT_BACKUP}/code/current_code_backup.tar.gz" \
        -C "$PROJECT_ROOT" \
        --exclude=venv \
        --exclude=__pycache__ \
        --exclude=*.pyc \
        . 2>/dev/null
    
    # Restore
    rm -rf "${PROJECT_ROOT:?}"/* 2>/dev/null
    tar -xzf "$BACKUP_CODE" -C "$PROJECT_ROOT"
    
    log_success "Code restored from backup"
else
    log_error "Code backup not found: ${BACKUP_CODE}"
fi

# ============================================================================
# 3. Restore Database
# ============================================================================
log_info "Restoring database..."

BACKUP_DB="${ROLLBACK_DIR}/database/database.dump"

if [ -f "$BACKUP_DB" ] && command -v pg_restore &> /dev/null; then
    # Backup current database
    PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
        -d "$DB_NAME" -F c \
        -f "${CURRENT_BACKUP}/database/pre_rollback.dump" 2>/dev/null
    
    # Restore
    PGPASSWORD="${DB_PASSWORD}" pg_restore \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
        -d "$DB_NAME" --clean --if-exists \
        "$BACKUP_DB" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Database restored from backup"
    else
        log_warning "Database restore may have issues"
    fi
else
    log_warning "Database backup not found or pg_restore not available"
fi

# ============================================================================
# 4. Restore Evidence
# ============================================================================
log_info "Restoring evidence data..."

for evidence_backup in "${ROLLBACK_DIR}"/evidence/*.tar.gz; do
    if [ -f "$evidence_backup" ]; then
        # Extract to evidence location
        tar -xzf "$evidence_backup" -C /data/ 2>/dev/null || \
        tar -xzf "$evidence_backup" -C "$PROJECT_ROOT/data/" 2>/dev/null
        
        log_success "Evidence restored from $(basename "$evidence_backup")"
        break
    fi
done

# ============================================================================
# 5. Restore Config
# ============================================================================
log_info "Restoring configuration files..."

if [ -d "${ROLLBACK_DIR}/config" ]; then
    cp -r "${ROLLBACK_DIR}/config"/* "${PROJECT_ROOT}/" 2>/dev/null
    log_success "Configuration restored"
fi

# ============================================================================
# 6. Start Services
# ============================================================================
log_info "Starting services..."

if command -v systemctl &> /dev/null; then
    sudo systemctl start nemesis-api 2>/dev/null
    sudo systemctl start nemesis-worker 2>/dev/null
    sudo systemctl start nemesis-websocket 2>/dev/null
elif command -v docker &> /dev/null; then
    docker-compose -f "${PROJECT_ROOT}/docker-compose.yml" up -d 2>/dev/null
fi

log_success "Services started"

# ============================================================================
# 7. Verification
# ============================================================================
log_info "Verifying rollback..."

# Wait for services
sleep 5

# Check health
if command -v curl &> /dev/null; then
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" 2>/dev/null)
    if [ "$HEALTH" = "200" ]; then
        log_success "Health check passed"
    else
        log_warning "Health check returned: ${HEALTH}"
    fi
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                        ROLLBACK COMPLETE                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "System rolled back to: ${ROLLBACK_DIR}"
log_info "Pre-rollback backup saved: ${CURRENT_BACKUP}"
echo ""

# Run verification
echo "Running verification..."
python "$(dirname "$0")/07_verify_cleanup.py"