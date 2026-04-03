from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(64) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
                """
            )
        )
        applied = {row[0] for row in conn.execute(text("SELECT version FROM schema_migrations"))}
        for path in migration_files:
            if path.name in applied:
                continue
            sql = path.read_text(encoding="utf-8")
            conn.execute(text(sql))
            conn.execute(
                text("INSERT INTO schema_migrations(version) VALUES (:version)"),
                {"version": path.name},
            )
