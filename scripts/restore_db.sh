@echo off
REM Database Restore Script untuk Windows

if "%1"=="" (
    echo Usage: %0 ^<backup_file^>
    echo Example: %0 C:\nemesis_backups\nemesis_db_20260101_020000.sql
    exit /b 1
)

set BACKUP_FILE=%1

if not exist "%BACKUP_FILE%" (
    echo Error: Backup file not found: %BACKUP_FILE%
    exit /b 1
)

echo Restoring database from: %BACKUP_FILE%

REM Get container name
for /f %%i in ('docker ps --format "{{.Names}}" ^| findstr /i "postgres"') do set CONTAINER_NAME=%%i

if "%CONTAINER_NAME%"=="" (
    echo Error: PostgreSQL container not found
    exit /b 1
)

echo Found container: %CONTAINER_NAME%

REM Restore backup
type "%BACKUP_FILE%" | docker exec -i %CONTAINER_NAME% pg_restore -U nemesis -d nemesis_db --clean --if-exists --verbose

if %errorlevel% equ 0 (
    echo Restore completed successfully
) else (
    echo Restore failed
    exit /b 1
)