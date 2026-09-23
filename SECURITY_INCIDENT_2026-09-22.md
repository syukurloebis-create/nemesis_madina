# 🚨 SECURITY INCIDENT — 2026-09-22

## Summary
Automated sweep found literal credentials (`Admin123`, `nemesis123`)
in ~60 tracked files, expanding beyond the 12-file scope of the
2026-09-21 incident.

## Scope
- Total files with credential-like strings: ~60
- Reported in: git ls-files (all tracked)
- Detected by: grep -E 'Admin123|nemesis123'

## Classification

### 🔴 CRITICAL (production config)
- .env.production
- docker-compose.prod.yml

### 🟠 HIGH (core runtime)
- docker-compose.yml
- backend/security/auth.py
- backend/services/password_validator.py

### 🟡 MEDIUM (tooling)
- backend/migrations/*.py
- scripts/*.py (~30 files)

### 🟢 LOW (dev/test)
- .env.development
- tests/debug/*.py

## Status
- NOT cleaned in this session (Phase D scope)
- Requires dedicated security sprint
- Next session priority: HIGH

## Required Actions
1. Audit per-file: real credential vs documented example
2. Rotate any exposed credentials (verify with SECURITY.md)
3. Migrate .env* to gitignore + secrets management
4. Add pre-commit hook: block credential patterns
5. Regression test: services still functional post-cleanup

## Reference
- Prior incident: SECURITY.md BAGIAN 11.1 (2026-09-21)
- Prior fix commits: 7bd39ea, ca1a79f, da9cb33, 3e56542, 5c478a2, b580266
- This sweep commits: NONE (findings only)
