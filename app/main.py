# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.db.init_db import create_db_and_tables
from app.routers.category_router import router as category_router
from app.routers.product_router import router as product_router
from app.routers.order_router import router as order_router
from app.routers.auth_router import router as auth_router
from app.routers.admin_router import router as admin_router

app = FastAPI(title="Morine Gypsum API")

# ============================================
# FRONTEND (React) CORS CONFIGURATION ✅
# ============================================
# Read allowed origins from environment (comma-separated), fall back to defaults
allowed = os.getenv("ALLOWED_ORIGINS", "")
if allowed:
    origins = [o.strip() for o in allowed.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# DATABASE INITIALIZATION
# ============================================
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ============================================
# ROUTERS
# ============================================
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(auth_router)
app.include_router(admin_router)

# ============================================
# STATIC FILES
# ============================================
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
def root():
    return {"message": "Welcome to Morine Gypsum API"}
