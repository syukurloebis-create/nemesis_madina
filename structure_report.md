# NEMESIS V8+ Structure Report
## Generated: Mon Jul 13 17:59:34 SEAST 2026

### 1. Project Structure
```
total 19695
drwxr-xr-x 1 LENOVO 197121       0 Jul 13 17:59 ./
drwxr-xr-x 1 LENOVO 197121       0 Jul 13 11:36 ../
drwxr-xr-x 1 LENOVO 197121       0 Jul 10 17:57 .backup/
-rw-r--r-- 1 LENOVO 197121     419 Jul  9 19:06 .dependency-cruiser.js
-rw-r--r-- 1 LENOVO 197121     766 Jun  4 19:09 .dockerignore
-rw-r--r-- 1 LENOVO 197121     354 Jun 12 15:21 .env
-rw-r--r-- 1 LENOVO 197121     190 Jun  9 15:53 .env.development
-rw-r--r-- 1 LENOVO 197121     503 Jun 23 15:04 .env.production
drwxr-xr-x 1 LENOVO 197121       0 Jun  2 17:50 .fase_status/
drwxr-xr-x 1 LENOVO 197121       0 Jul 12 19:22 .git/
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 13:47 .github/
-rw-r--r-- 1 LENOVO 197121    1702 Jun  7 11:31 .gitignore
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 10:46 .pytest_cache/
drwxr-xr-x 1 LENOVO 197121       0 Jun  1 23:21 .roadmap_status/
-rw-r--r-- 1 LENOVO 197121       5 Jun  1 20:59 .server.pid
-rw-r--r-- 1 LENOVO 197121       0 Jun 14 16:24 0
-rw-r--r-- 1 LENOVO 197121       0 Jun 14 18:22 0]
drwxr-xr-x 1 LENOVO 197121       0 Jun  6 20:04 C:nemesis_backups/
-rw-r--r-- 1 LENOVO 197121 1220949 Jun 12 23:04 DATA RUP MADINA 2025 2026.csv
-rw-r--r-- 1 LENOVO 197121  380872 Jun 12 23:03 DATA RUP MADINA 2025 2026.xlsx
-rw-r--r-- 1 LENOVO 197121     269 Jun 27 07:21 Dockerfile
-rw-r--r-- 1 LENOVO 197121     699 Jun  4 19:03 Dockerfile.prod
-rw-r--r-- 1 LENOVO 197121     562 Jun 23 15:04 Dockerfile.production
-rw-r--r-- 1 LENOVO 197121     266 Jun  7 09:14 Dockerfile.simple
-rw-r--r-- 1 LENOVO 197121    1019 Jun  1 15:07 README.md
-rw-r--r-- 1 LENOVO 197121  128831 May  5 14:09 RUP MADINA 2026.xlsx
-rw-r--r-- 1 LENOVO 197121  262444 May 14 23:36 RUP Penyedia 2025.xlsx
-rw-r--r-- 1 LENOVO 197121  936727 Jun  8 20:44 RUP_NORMALIZED.xlsx
-rw-r--r-- 1 LENOVO 197121 1080383 Jun 13 17:52 RUP_data_realisasi_2022_2026.csv
-rw-r--r-- 1 LENOVO 197121     742 Jun 13 23:04 alembic.ini
-rw-r--r-- 1 LENOVO 197121     740 Jun 13 23:04 alembic.ini.bak
-rw-r--r-- 1 LENOVO 197121    1945 Jun  9 07:51 all_endpoints.txt
-rw-r--r-- 1 LENOVO 197121    2969 Jun 14 17:15 analyze_rup_data.py
-rw-r--r-- 1 LENOVO 197121    3736 Jun  7 11:44 api_direct_fixed.py
-rw-r--r-- 1 LENOVO 197121    5249 Jun 23 15:47 app.log
-rw-r--r-- 1 LENOVO 197121   10768 Jun 23 15:42 app.py
-rw-r--r-- 1 LENOVO 197121    5338 Jun 23 15:22 app.py.backup_20260623_152206
-rw-r--r-- 1 LENOVO 197121   12975 Jun 23 15:30 app.py.backup_fixed
-rw-r--r-- 1 LENOVO 197121    5338 Jun 23 15:16 app.py.backup_gzip_20260623_151625
-rw-r--r-- 1 LENOVO 197121   12975 Jun 23 15:39 app.py.backup_json
-rw-r--r-- 1 LENOVO 197121   12975 Jun 23 15:38 app.py.backup_json_fix
-rw-r--r-- 1 LENOVO 197121   13512 Jun 23 15:42 app.py.backup_old
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 17:14 audit/
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 17:06 audit_evidence/
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 17:12 audit_report/
-rw-r--r-- 1 LENOVO 197121    1851 Jun 16 17:50 auth.py
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 07:02 backend/
-rw-r--r-- 1 LENOVO 197121   15919 Jun 12 08:01 backend_files.txt
-rw-r--r-- 1 LENOVO 197121   23351 Jun 12 08:15 backend_tree.txt
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 17:59 backup/
-rw-r--r-- 1 LENOVO 197121    6496 Jun 11 20:03 backup_after_auth_fix.sql
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 09:49 backup_auth_20260624_094936/
-rw-r--r-- 1 LENOVO 197121 2825405 Jun 16 16:53 backup_before_hybrid.sql
drwxr-xr-x 1 LENOVO 197121       0 Jun  4 13:11 backup_cases_20260604_131110/
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:54 backup_config_fix_20260624_235453/
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:41 backup_database_fix_20260624_234141/
-rw-r--r-- 1 LENOVO 197121 1765692 Jun 10 13:24 backup_db_20260610.sql
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:26 backup_final_import_fix_20260624_232618/
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:17 backup_import_final_20260624_231633/
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:05 backup_import_fix_20260624_230526/
drwxr-xr-x 1 LENOVO 197121       0 Jun 24 23:30 backup_import_fix_python/
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 15:24 backups/
-rw-r--r-- 1 LENOVO 197121    1326 Jun 23 15:04 benchmark.py
-rw-r--r-- 1 LENOVO 197121     405 Jun 12 16:44 benchmark_results_100.json
-rw-r--r-- 1 LENOVO 197121     406 Jun 12 16:44 benchmark_results_1000.json
-rw-r--r-- 1 LENOVO 197121     408 Jun 12 16:45 benchmark_results_10000.json
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 00:07 benchmarks/
-rw-r--r-- 1 LENOVO 197121     670 Jul 10 09:04 build-config.json
-rwxr-xr-x 1 LENOVO 197121    6866 Jun 10 03:33 cleanup_fase_a.sh*
-rw-r--r-- 1 LENOVO 197121   71239 Jul 12 13:08 collect.log
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 19:21 config/
-rw-r--r-- 1 LENOVO 197121 1020005 Jul 11 07:17 coverage.xml
-rw-r--r-- 1 LENOVO 197121  380872 Jun 13 10:15 data_rup_madina.xlsx
-rw-r--r-- 1 LENOVO 197121    4700 Jun 24 12:04 database.py.bak
-rw-r--r-- 1 LENOVO 197121    4700 Jun 24 11:57 database_legacy_backup.py
-rw-r--r-- 1 LENOVO 197121     743 Jun 16 22:19 default.conf
-rwxr-xr-x 1 LENOVO 197121    2581 Jun  9 15:52 deploy.sh*
-rw-r--r-- 1 LENOVO 197121    1516 Jun 10 17:34 docker-compose.direct.yml
-rw-r--r-- 1 LENOVO 197121    3824 Jun 12 07:30 docker-compose.lb.yml
-rw-r--r-- 1 LENOVO 197121    6660 Jun 11 14:23 docker-compose.lb.yml.backup
-rw-r--r-- 1 LENOVO 197121    6495 Jun 10 17:42 docker-compose.lb.yml.bak
-rw-r--r-- 1 LENOVO 197121    1583 Jun  5 22:20 docker-compose.observability.yml
-rw-r--r-- 1 LENOVO 197121    2596 Jun  9 15:52 docker-compose.prod.yml
-rw-r--r-- 1 LENOVO 197121    1686 Jun 10 17:27 docker-compose.simple.yml
-rw-r--r-- 1 LENOVO 197121    2045 Jun 21 18:13 docker-compose.yml
-rw-r--r-- 1 LENOVO 197121    1913 Jun 18 14:17 docker-compose.yml.bak
-rwxr-xr-x 1 LENOVO 197121     307 Jun 14 08:12 docker-entrypoint.sh*
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 19:50 docs/
-rw-r--r-- 1 LENOVO 197121     184 Jul 10 08:20 effective-tsconfig.json
-rw-r--r-- 1 LENOVO 197121     591 May 13 16:20 eslint.config.js
-rw-r--r-- 1 LENOVO 197121    5819 Jun 15 16:24 evidence.py
-rw-r--r-- 1 LENOVO 197121 1173849 Jun 12 16:55 evidence_package_18cea8e0-e9a0-474e-a7f0-e3af8181b1d5_20260612_095525.zip
-rw-r--r-- 1 LENOVO 197121    3710 Jun 23 15:39 file_processor.py
-rwxr-xr-x 1 LENOVO 197121    1947 Jun 24 23:43 fix_all_imports.py*
-rwxr-xr-x 1 LENOVO 197121    1592 Jun 24 23:47 fix_database_imports.py*
-rwxr-xr-x 1 LENOVO 197121    2663 Jun 11 07:03 fix_frontend_config.sh*
-rwxr-xr-x 1 LENOVO 197121    1347 Jun 24 11:35 fix_frontend_structure.sh*
-rwxr-xr-x 1 LENOVO 197121    2136 Jun 24 23:30 fix_imports.py*
-rwxr-xr-x 1 LENOVO 197121    3112 Jun 24 12:16 fix_infrastructure_imports.py*
-rwxr-xr-x 1 LENOVO 197121    1135 Jun 25 01:00 fix_main.py*
drwxr-xr-x 1 LENOVO 197121       0 Jul 10 17:58 frontend/
-rwxr-xr-x 1 LENOVO 197121    1756 Jun  9 01:50 full_dashboard_deploy.sh*
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 15:35 grafana/
drwxr-xr-x 1 LENOVO 197121       0 Jun  5 22:04 grafanadashboards/
drwxr-xr-x 1 LENOVO 197121       0 Jun  5 22:04 grafanadatasources/
-rw-r--r-- 1 LENOVO 197121    9322 Jun 15 22:33 graph.py.backup.20260616_064410
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 07:07 htmlcov/
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 00:07 infrastructure/
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 17:59 k8s/
-rw-r--r-- 1 LENOVO 197121  723205 Jun  1 09:45 laporan_struktur.txt
drwxr-xr-x 1 LENOVO 197121       0 Jun 25 14:26 logs/
-rw-r--r-- 1 LENOVO 197121     512 Jun 25 18:54 merge.js
-rw-r--r-- 1 LENOVO 197121    1699 Jun  7 12:57 metrics.py
drwxr-xr-x 1 LENOVO 197121       0 Jun  1 13:46 metrics_exports/
-rwxr-xr-x 1 LENOVO 197121    7871 Jul  4 07:15 migrate_evidence_imports.py*
drwxr-xr-x 1 LENOVO 197121       0 Jun  4 19:06 migrations/
drwxr-xr-x 1 LENOVO 197121       0 Jun  1 22:32 models/
-rwxr-xr-x 1 LENOVO 197121     817 Jun 23 15:04 monitor_performance.sh*
-rw-r--r-- 1 LENOVO 197121   28672 Jun 23 15:38 nemesis.db
-rw-r--r-- 1 LENOVO 197121    5497 Jun  7 12:49 nemesis_dashboard.json
-rw-r--r-- 1 LENOVO 197121    5493 Jun  8 22:05 nemesis_dashboard_clean.json
-rw-r--r-- 1 LENOVO 197121    2160 Jun  8 22:34 nemesis_dashboard_fixed.json
-rw-r--r-- 1 LENOVO 197121     927 Jun  8 22:38 nemesis_dashboard_import.json
-rw-r--r-- 1 LENOVO 197121   85580 Jun 27 02:48 nemesis_full_report.md
-rw-r--r-- 1 LENOVO 197121    9558 Jun 16 19:21 network_intelligence.py
drwxr-xr-x 1 LENOVO 197121       0 Jun 21 09:20 nginx/
-rw-r--r-- 1 LENOVO 197121    1570 Jun 23 15:04 nginx.conf
-rw-r--r-- 1 LENOVO 197121     976 Jun 17 00:03 nginx.conf.backup
-rw-r--r-- 1 LENOVO 197121     139 Jun 16 22:13 nginx.conf.bak
drwxr-xr-x 1 LENOVO 197121       0 Jul 10 08:23 node_modules/
-rw-r--r-- 1 LENOVO 197121       0 Jul  6 17:21 openapi.json
-rw-r--r-- 1 LENOVO 197121    1239 Jun  9 07:51 openapi_report.md
-rw-r--r-- 1 LENOVO 197121   28670 Jun 21 23:09 openapi_runtime.json
-rw-r--r-- 1 LENOVO 197121   80677 Jun 22 10:17 openapi_spec.json
-rw-r--r-- 1 LENOVO 197121  206137 Jul 10 09:00 package-lock.json
-rw-r--r-- 1 LENOVO 197121     382 Jul 10 08:23 package.json
drwxr-xr-x 1 LENOVO 197121       0 Jul 10 17:57 packages/
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 17:21 phase1_evidence_artifact/
-rw-r--r-- 1 LENOVO 197121     107 May 30 00:17 postcss.config.js
-rw-r--r-- 1 LENOVO 197121   23911 Jun  8 20:49 procurement_risk_analysis.xlsx
-rw-r--r-- 1 LENOVO 197121    1166 Jun 23 15:04 production_readiness.md
drwxr-xr-x 1 LENOVO 197121       0 Jun  6 21:25 prometheus/
drwxr-xr-x 1 LENOVO 197121       0 Jun 10 17:25 prometheus.yml/
-rw-r--r-- 1 LENOVO 197121     882 Jul 11 20:30 pytest.ini
-rwxr-xr-x 1 LENOVO 197121    4215 Jun  8 11:41 quick_diagnostic.sh*
-rwxr-xr-x 1 LENOVO 197121    1911 Jun 24 12:19 quick_fix_infrastructure.sh*
-rwxr-xr-x 1 LENOVO 197121     269 Jun 16 06:58 recovery.sh*
-rw-r--r-- 1 LENOVO 197121    2070 Jun  2 09:26 requirements.final.txt
-rw-r--r-- 1 LENOVO 197121    2070 Jun  1 22:55 requirements.lock.txt
-rw-r--r-- 1 LENOVO 197121    2126 Jun 20 10:49 requirements.txt
-rw-r--r-- 1 LENOVO 197121     237 Jun 14 08:34 requirements.txt.bak
-rwxr-xr-x 1 LENOVO 197121    1653 Jun 24 11:38 run_all_tests.sh*
-rw-r--r-- 1 LENOVO 197121    1001 Jun  7 21:58 run_backend.ps1
-rwxr-xr-x 1 LENOVO 197121    2789 Jun  8 11:40 run_debug_tests.sh*
-rwxr-xr-x 1 LENOVO 197121     410 Jun 24 11:37 run_frontend_tests.sh*
-rw-r--r-- 1 LENOVO 197121 2535424 Jun 15 14:52 rup_database.db
-rw-r--r-- 1 LENOVO 197121  275690 Jun 15 14:53 rup_export_test.csv
-rw-r--r-- 1 LENOVO 197121 1575887 Jun 14 11:17 rup_paket.csv
-rw-r--r-- 1 LENOVO 197121 1169649 Jun 14 17:13 rup_paket_detailed.csv
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 23:29 rup_upload_system/
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 19:46 scripts/
-rw-r--r-- 1 LENOVO 197121    8858 Jun  7 09:45 setup_api.ps1
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 23:31 static/
drwxr-xr-x 1 LENOVO 197121       0 Jun 14 11:46 storage/
-rw-r--r-- 1 LENOVO 197121    4353 Jul  3 12:31 structure_report.json
-rw-r--r-- 1 LENOVO 197121     106 Jul 13 17:59 structure_report.md
-rw-r--r-- 1 LENOVO 197121  587192 Jun 27 02:39 struktur_report.txt
drwxr-xr-x 1 LENOVO 197121       0 Jun  5 00:49 temp_migrations/
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 23:22 templates/
-rw-r--r-- 1 LENOVO 197121    1282 Jun  7 09:53 test_api.ps1
-rw-r--r-- 1 LENOVO 197121    1406 Jun 24 11:58 test_db_import.py
-rw-r--r-- 1 LENOVO 197121      37 Jun 12 16:04 test_evidence.txt
-rw-r--r-- 1 LENOVO 197121     624 Jun 23 14:21 test_frontend.html
drwxr-xr-x 1 LENOVO 197121       0 Jun  8 11:42 test_results/
-rwxr-xr-x 1 LENOVO 197121    1595 Jun 11 10:30 test_temporal.sh*
drwxr-xr-x 1 LENOVO 197121       0 Jul 11 15:50 tests/
-rw-r--r-- 1 LENOVO 197121    1483 Jun  8 10:52 timeline_event.py
-rw-r--r-- 1 LENOVO 197121   18979 Jul 10 10:23 trace.txt
-rw-r--r-- 1 LENOVO 197121    1535 Jul 10 16:03 tsconfig.base.json
-rw-r--r-- 1 LENOVO 197121     436 Jul 10 07:25 tsconfig.build.json
-rw-r--r-- 1 LENOVO 197121     436 Jul 10 17:05 tsconfig.json
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 23:48 uploads/
-rw-r--r-- 1 LENOVO 197121    2657 Jun 14 01:17 vendors.csv
drwxr-xr-x 1 LENOVO 197121       0 Jun 14 08:55 venv/
drwxr-xr-x 1 LENOVO 197121       0 Jun 12 11:28 verifier/
-rw-r--r-- 1 LENOVO 197121   13563 Jul  3 12:30 verify_structure.py
-rwxr-xr-x 1 LENOVO 197121    1905 Jun 12 16:57 verify_temp.py*
drwxr-xr-x 1 LENOVO 197121       0 Jun  9 02:32 web/
```

### 2. Backend Source Structure
```
```

### 3. Database Schema
```
CREATE TABLE rup_paket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_id VARCHAR(50) UNIQUE NOT NULL,
                nama_paket TEXT NOT NULL,
                pagu DECIMAL(20,2),
                jenis VARCHAR(50),
                tahun INTEGER,
                kategori VARCHAR(100),
                metode VARCHAR(100),
                bulan VARCHAR(50),
                lokasi VARCHAR(100),
                instansi VARCHAR(200),
                hash_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , status TEXT DEFAULT 'Dalam Proses');
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE upload_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255),
                file_size INTEGER,
                total_records INTEGER,
                new_records INTEGER,
                duplicate_records INTEGER,
                status VARCHAR(50),
                error_message TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE INDEX idx_nomor_id ON rup_paket(nomor_id);
CREATE INDEX idx_tahun ON rup_paket(tahun);
CREATE INDEX idx_instansi ON rup_paket(instansi);
CREATE INDEX idx_rup_nomor_id ON rup_paket(nomor_id);
CREATE INDEX idx_rup_tahun ON rup_paket(tahun);
CREATE INDEX idx_rup_jenis ON rup_paket(jenis);
```

### 4. Package Dependencies
```
```
