# app/db/session.py
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in your .env file")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
