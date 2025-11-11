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

# SQLAlchemy expects the dialect name 'postgresql' (or 'postgresql+psycopg2').
# Some providers give a URL that starts with 'postgres://' which maps to a
# non-existent 'postgres' dialect in SQLAlchemy 2.x. Normalize it here so
# create_engine can load the correct dialect plugin. (This is safe to do
# because the rest of the URL is unchanged.)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
