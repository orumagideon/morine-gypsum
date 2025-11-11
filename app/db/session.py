# app/db/session.py
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()  # Load .env variables

# PostgreSQL database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://oruma:oruma@localhost:5432/gypsum_data"
)

# Normalise the scheme so SQLAlchemy loads the correct dialect plugin.
# Accept common variants and trim whitespace to be robust against different
# secret encodings or accidental surrounding whitespace.
if DATABASE_URL:
    # Trim surrounding whitespace and perform a case-insensitive prefix match so
    # variants like 'Postgres://' or leading newlines won't bypass normalization.
    DATABASE_URL = DATABASE_URL.strip()
    low = DATABASE_URL.lower()
    if low.startswith("postgres://"):
        # Simple and safe replacement of the scheme to include the psycopg2 driver
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif low.startswith("postgresql://"):
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
# Debug info (will appear in Fly logs) to help diagnose hostname parsing issues
raw_db = os.getenv("DATABASE_URL")
print("DEBUG: raw DATABASE_URL present:", bool(raw_db))
print("DEBUG: parsed DB hostname:", db_hostname)

if db_hostname and db_hostname not in ("localhost", "127.0.0.1", "::1"):
    print("DEBUG: using sslmode=require for DB connection")
    engine = create_engine(DATABASE_URL, echo=True, connect_args={"sslmode": "require"})
else:
    print("DEBUG: connecting without sslmode")
    engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
