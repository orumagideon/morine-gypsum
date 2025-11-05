# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db.init_db import create_db_and_tables
from app.routers.category_router import router as category_router
from app.routers.product_router import router as product_router

app = FastAPI(title="Morine Gypsum API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Routers
app.include_router(category_router)
app.include_router(product_router)

# Static files (for image access)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Morine Gypsum API"}
