"""
Database connection setup.

Why this file exists:
    This is the ONLY file that knows how to talk to the database engine
    itself (connection string, session lifecycle). Models import `Base`
    from here to register themselves; routers get a `Session` via
    `get_db()` through FastAPI's dependency injection. No other file
    creates a session or an engine directly.

Key pieces:
    engine       — the SQLAlchemy connection pool to MySQL, built once
                   from settings.DATABASE_URL
    SessionLocal — a factory that creates a new DB session per request
    Base         — the declarative base class every model inherits from
    get_db()     — a FastAPI dependency that yields one session per
                   request and guarantees it's closed afterward, even
                   if the request raises an exception
"""

from sqlalchemy import create_engine, BigInteger, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # checks connection is alive before using it;
                           # avoids "MySQL server has gone away" errors
                           # after periods of idle time
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Shared primary-key column type for every model.
#
# Production (MySQL) always gets a real BIGINT, as designed in
# database/init.sql. When the same models are pointed at a SQLite
# database instead — used for fast local testing (see Phase 15) rather
# than requiring a running MySQL server — SQLite only auto-generates
# row IDs for a column typed exactly INTEGER, not BIGINT. with_variant
# lets one column declaration mean "BIGINT on MySQL, INTEGER on
# SQLite" without weakening or changing anything about the production
# schema. This is a testing convenience, not a production compromise.
BigIntegerPK = BigInteger().with_variant(Integer, "sqlite")


def get_db():
    """
    FastAPI dependency: yields one DB session per request.

    Usage in a router:
        @router.get("/employees")
        def list_employees(db: Session = Depends(get_db)):
            ...

    The try/finally guarantees the session is closed after the request
    completes, whether it succeeded or raised an exception — this is
    the standard SQLAlchemy + FastAPI pattern for per-request sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
