"""
Real migration runner.

Railway's managed Postgres does NOT run Postgres's docker-entrypoint-initdb.d
convention — that only fires for a fresh container created from the postgres
image itself, which is what docker-compose.yml uses for local dev. Against a
real managed database (Railway, Supabase's own Postgres, RDS, etc.) nothing
would ever apply these .sql files without this script.

Usage:
    python scripts/migrate.py

Reads DATABASE_URL from the environment (same variable the app uses),
applies every backend/migrations/*.sql file in filename order that hasn't
already been applied, and records each one in a schema_migrations table.
Safe to run on every deploy — already-applied files are skipped.
"""

import os
import sys
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set.", file=sys.stderr)
        sys.exit(1)
    # the app uses the SQLAlchemy "postgresql+psycopg://" form; psycopg itself
    # wants a plain "postgresql://" DSN.
    return url.replace("postgresql+psycopg://", "postgresql://")


def main() -> None:
    dsn = get_database_url()
    conn = psycopg.connect(dsn, autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            conn.commit()

            cur.execute("SELECT filename FROM schema_migrations")
            applied = {row[0] for row in cur.fetchall()}

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not migration_files:
            print("No migration files found.")
            return

        for path in migration_files:
            if path.name in applied:
                print(f"skip  {path.name} (already applied)")
                continue
            print(f"apply {path.name}")
            sql = path.read_text()
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)", (path.name,)
                )
            conn.commit()

        print("Migrations complete.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
