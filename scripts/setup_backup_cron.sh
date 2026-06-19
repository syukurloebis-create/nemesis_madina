@echo off
REM Database Backup Script untuk Windows
REM Menggunakan Task Scheduler

setlocal enabledelayedexpansion

REM Configuration
set BACKUP_DIR=C:\nemesis_backups
set RETENTION_DAYS=30
set TIMESTAMP=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\nemesis_db_%TIMESTAMP%.sql
set LOG_FILE=%BACKUP_DIR%\backup.log

REM Create backup directory
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo %DATE% %TIME% - Starting database backup... >> "%LOG_FILE%"

REM Get container name
for /f %%i in ('docker ps --format "{{.Names}}" ^| findstr /i "postgres"') do set CONTAINER_NAME=%%i

if "%CONTAINER_NAME%"=="" (
    echo %DATE% %TIME% - ERROR: PostgreSQL container not found >> "%LOG_FILE%"
    exit /b 1
)

echo %DATE% %TIME% - Found container: %CONTAINER_NAME% >> "%LOG_FILE%"

REM Perform backup
docker exec %CONTAINER_NAME% pg_dump -U nemesis -d nemesis_db --format=custom --compress=9 --no-owner --no-privileges > "%BACKUP_FILE%" 2>> "%LOG_FILE%"

if %errorlevel% equ 0 (
    echo %DATE% %TIME% - Backup completed: %BACKUP_FILE% >> "%LOG_FILE%"
    
    REM Create backup info
    echo Backup File: %BACKUP_FILE% > "%BACKUP_FILE%.info"
    echo Time: %DATE% %TIME% >> "%BACKUP_FILE%.info"
    echo Container: %CONTAINER_NAME% >> "%BACKUP_FILE%.info"
    
    REM Clean old backups
    echo %DATE% %TIME% - Cleaning backups older than %RETENTION_DAYS% days >> "%LOG_FILE%"
    forfiles /p "%BACKUP_DIR%" /m "nemesis_db_*.sql" /d -%RETENTION_DAYS% /c "cmd /c del @file" 2>nul
    forfiles /p "%BACKUP_DIR%" /m "*.info" /d -%RETENTION_DAYS% /c "cmd /c del @file" 2>nul
) else (
    echo %DATE% %TIME% - ERROR: Backup failed >> "%LOG_FILE%"
    exit /b 1
)

echo %DATE% %TIME% - Backup completed successfully >> "%LOG_FILE%"