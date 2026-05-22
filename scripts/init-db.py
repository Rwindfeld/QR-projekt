"""Create QR database and apply schema.sql + seed.sql (no psql required)."""
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    conn = psycopg2.connect(
        host="localhost", port=5432, user="postgres", password="1590", dbname="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("QR",))
    if not cur.fetchone():
        cur.execute('CREATE DATABASE "QR"')
        print("Created database QR")
    conn.close()

    conn = psycopg2.connect(
        host="localhost", port=5432, user="postgres", password="1590", dbname="QR"
    )
    conn.autocommit = True
    cur = conn.cursor()
    for name in ("schema.sql", "seed.sql"):
        cur.execute((ROOT / name).read_text(encoding="utf-8"))
        print(f"Applied {name}")
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
