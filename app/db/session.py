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

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
