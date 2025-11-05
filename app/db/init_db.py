# app/db/init_db.py
from app.db.session import engine
from app.models import *  # Import all models so SQLModel can create tables
from sqlmodel import SQLModel

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
