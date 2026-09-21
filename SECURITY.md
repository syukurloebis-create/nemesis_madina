# NEMESIS Security Notes

**Last updated:** 2026-09-21

## 2026-09-21 — Security Incident Log

### Track 9 — CLOSED

Symptom: Browser 401 on /api/v1/dashboard/intelligence/{case_id}

Root cause: Stale browser token (from failed password rotation) + bundle cache + nginx cache policy.

Resolution verified:
- Browser token: 388 chars, valid JWT (3 segments)
- Manual fetch from browser console: 200
- Total findings: 9

### Incidents Resolved

1. Credential Exposure (P0) — RESOLVED — commits 7bd39ea, ca1a79f, da9cb33, 3e56542
2. Broken Password Rotation (P1) — RESOLVED — re-rotation with alphanumeric
3. Empty Password Acceptance (P2) — HARDENED — commit 5c478a2
4. Nginx Cache Defect (P2) — FIXED — commit 11a7359
5. Dead Code Removal (P3) — DONE — commit da9cb33
6. Docker-compose Regression (P3) — FIXED — commit 494cb41
7. F3.7 Cleanup (P3) — DONE — commit a641e94

### Required Environment Variables

- NEMESIS_TEST_USERNAME
- NEMESIS_TEST_PASSWORD
- NEMESIS_API_URL (default: http://127.0.0.1:8000)

Location: ~/.nemesis_env (chmod 600, NOT tracked in git)

### Password Rotation Procedure

Use alphanumeric-only password to avoid shell escaping issues.

1. Generate: NEW_PW=$(python -c "import secrets,string;print(chr(39).join([secrets.choice(string.ascii_letters+string.digits) for _ in range(32)]))")
2. Verify not empty: if [ -z "$NEW_PW" ]; then echo ERROR; exit 1; fi
3. Generate hash via container (passlib bcrypt)
4. Update DB: docker exec postgres psql -c "UPDATE users SET password_hash=..."
5. Save to ~/.nemesis_env with chmod 600

### Known Issues

- Git history contains legacy credentials (before 2026-09-21)
- Rotated credentials INVALID but visible in git log
- History rewrite NOT performed (forensic-dirty repo)

### Do NOT

- Hardcode credentials in any tracked file
- Commit .env or ~/.nemesis_env
- Use test credentials in production

### Baseline Reference (FROZEN)

- Risk: 47.58 MEDIUM
- Graph: 4177 entities / 2424 relationships
- Case ID: b4897392-87ab-4e7a-84b6-90228f3d1eb9
- Boundary: Risk Engine v3 NOT TOUCHED

---

*This file is intentionally public within the project. Do not add secrets here.*
