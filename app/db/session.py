# app/db/session.py
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

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
    DATABASE_URL = DATABASE_URL.strip()
    # legacy shorthand 'postgres://' should be mapped to SQLAlchemy dialect
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        # prefer explicit driver so SQLAlchemy picks up psycopg2
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
