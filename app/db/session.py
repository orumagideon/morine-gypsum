# app/db/session.py
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import logging

load_dotenv()  # Load .env variables

logger = logging.getLogger("morine.db")

# PostgreSQL database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://oruma:oruma@localhost:5432/gypsum_data"
)

# Normalise the scheme so SQLAlchemy loads the correct dialect plugin.
# Accept common variants and trim whitespace to be robust against different
# secret encodings or accidental surrounding whitespace.
if DATABASE_URL:
    # Trim surrounding whitespace and perform a case-insensitive prefix match
    DATABASE_URL = DATABASE_URL.strip()
    low = DATABASE_URL.lower()
    if low.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif low.startswith("postgresql://") and "psycopg2" not in low:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# If the database is remote (not localhost) require SSL. Some providers
# (like Supabase) require TLS connections; passing connect_args ensures
# psycopg2 negotiates SSL mode correctly.
db_hostname = None
try:
    parsed = urlparse(DATABASE_URL)
    db_hostname = parsed.hostname
except Exception:
    db_hostname = None

raw_db = os.getenv("DATABASE_URL")
logger.debug("raw DATABASE_URL present: %s", bool(raw_db))
logger.debug("parsed DB hostname: %s", db_hostname)

# Use pool_pre_ping to avoid stale connection errors in long-running apps
connect_args = {}
if db_hostname and db_hostname not in ("localhost", "127.0.0.1", "::1"):
    logger.debug("using sslmode=require for DB connection")
    connect_args = {"sslmode": "require"}

# Keep SQL logging off by default in production; echo can be enabled with
# an env var if needed (e.g. DEBUG_SQL=true)
echo = os.getenv("DEBUG_SQL", "false").lower() in ("1", "true", "yes")

engine = create_engine(DATABASE_URL, echo=echo, connect_args=connect_args, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session
