#!/usr/bin/env python
"""
Fix main.py - remove duplicate router registration
"""
import re
from pathlib import Path

main_file = Path("backend/main.py")

with open(main_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Cari blok yang mengandung include_router yang sudah di-register di api/v1
# Kita comment out router registrasi yang double

# Pola yang akan di-comment
patterns = [
    r'(from routers\.cases import router as cases_router\n\s*app\.include_router\(cases_router, prefix="/api/v1/cases", tags=\["Cases"\]\))',
    r'(from routers\.fraud import router as fraud_router\n\s*app\.include_router\(fraud_router, prefix="/api/v1/fraud", tags=\["Fraud"\]\))',
    r'(from routers\.risk import router as risk_router\n\s*app\.include_router\(risk_router, prefix="/api/v1/risk", tags=\["Risk"\]\))',
]

# Ganti dengan commented
for pattern in patterns:
    content = re.sub(
        pattern,
        r'# \1  # ← DIPINDAHKAN KE API V1 ROUTER',
        content
    )

# Tulis kembali
with open(main_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ main.py fixed - duplicate registrations commented")
