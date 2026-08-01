import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DEFAULT_SQLITE_URL = "sqlite:///./sarthi.db"


def get_database_url() -> str:
    """Return the configured database URL, defaulting to a local SQLite file.

    Managed Postgres providers hand out `postgres://` URLs, which SQLAlchemy
    no longer recognises, so they are normalised to `postgresql://`.
    """
    url = os.getenv("DATABASE_URL", "").strip() or DEFAULT_SQLITE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    import db_models  # noqa: F401  (registers the mapped classes on Base)

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
