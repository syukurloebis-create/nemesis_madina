from pathlib import Path

for f in Path("backend/graph/infrastructure").rglob("*.py"):
    try:
        f.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        print(f"{f} -> {e}")