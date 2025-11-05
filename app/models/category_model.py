# app/models/category_model.py
from sqlmodel import SQLModel, Field
from typing import Optional

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    description: Optional[str] = None
