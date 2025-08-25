import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / "usage.db"
print(f"DB path: {db_path}")
if not db_path.exists():
    print("DB not found")
    raise SystemExit(1)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

print("Tables/Views:")
objects = cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
for name, typ in objects:
    print(f" - {typ}: {name}")

def describe(name: str):
    try:
        cols = cur.execute(f"PRAGMA table_info({name})").fetchall()
        count = cur.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"\n[{name}] columns:")
        for _, col, ctype, notnull, dflt, pk in cols:
            print(f"  - {col} {ctype} NOTNULL={notnull} PK={pk} DEFAULT={dflt}")
        print(f"rows: {count}")
    except Exception as e:
        print(f"describe error for {name}: {e}")

for name, typ in objects:
    if typ == 'table':
        describe(name)

conn.close()
