#!/usr/bin/env python3
"""
Database Migration Script
Run this script to update your existing database schema with new columns.

Usage:
    python migrate_database.py
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.migrate_order_table import migrate_order_table

if __name__ == "__main__":
    print("Starting database migration...")
    print("=" * 50)
    migrate_order_table()
    print("=" * 50)
    print("Migration script completed!")
    print("\nYou can now restart your FastAPI server.")

