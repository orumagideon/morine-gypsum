# app/db/init_db.py
from app.db.session import engine
from app.models import *  # Import all models so SQLModel can create tables
from sqlmodel import SQLModel
from sqlalchemy import text
import time
import logging
from sqlalchemy.exc import OperationalError

logger = logging.getLogger("morine.init_db")


def _ensure_category_parent_column():
    """Ensure the `parent_id` column exists on `category` table and try to add a FK.

    We add the column if missing (ALTER TABLE ... ADD COLUMN IF NOT EXISTS) and
    attempt to add a foreign key constraint. This is a small, idempotent migration
    helper to keep the DB and models in sync without a full migration tool.
    """
    # Use a transaction so DDL is applied and visible to subsequent connections
    with engine.begin() as conn:
        # Check if column exists
        col_check = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'category' AND column_name = 'parent_id'"
            )
        )
        if not col_check.first():
            # Add the column if missing; use IF NOT EXISTS for idempotency
            conn.execute(text("ALTER TABLE category ADD COLUMN IF NOT EXISTS parent_id integer"))
        # Try to add FK constraint (ignore errors if it already exists)
        # Try to add FK constraint. Some Postgres versions allow IF NOT EXISTS for constraints
        # but to be portable we catch and ignore errors if it already exists.
        try:
            conn.execute(
                text(
                    "ALTER TABLE category ADD CONSTRAINT fk_category_parent_id FOREIGN KEY (parent_id) REFERENCES category(id) ON DELETE SET NULL"
                )
            )
        except Exception:
            # Constraint may already exist or the DB may reject; ignore to keep startup robust
            pass


def _ensure_admin_email_column():
    """Ensure `email` column exists on `adminuser` table.

    Adds the column if missing. We avoid adding or altering data and keep this
    idempotent and non-destructive.
    """
    with engine.begin() as conn:
        col_check = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'adminuser' AND column_name = 'email'"
            )
        )
        if not col_check.first():
            # Add the column if missing; use IF NOT EXISTS for idempotency
            conn.execute(text("ALTER TABLE adminuser ADD COLUMN IF NOT EXISTS email varchar"))
        # We won't attempt to add a unique constraint automatically here since
        # that can fail if duplicate data exists. Leave to Alembic or manual migration.


def create_db_and_tables(retries: int = 5, backoff: float = 2.0):
    """Create missing tables and run idempotent DDL helpers.

    To make containerised deployments more resilient, this function will
    retry connecting to the database a few times with exponential backoff
    before giving up. If the DB remains unreachable we log an error and
    return without raising so the process doesn't crash immediately; this
    makes it easier to debug environment/secret issues in hosting platforms.
    """

    # Try to connect/create tables with retries to handle transient network
    # failures or the DB coming up slightly later than the app container.
    attempt = 0
    while attempt < retries:
        try:
            # Create any missing tables first
            SQLModel.metadata.create_all(engine)
            break
        except OperationalError as exc:
            attempt += 1
            wait = backoff * (2 ** (attempt - 1))
            logger.warning(
                "Database unreachable (attempt %d/%d): %s — retrying in %.1fs",
                attempt,
                retries,
                str(exc).splitlines()[0],
                wait,
            )
            time.sleep(wait)
    else:
        logger.error(
            "Could not connect to the database after %d attempts. "
            "Check DATABASE_URL and network access. Skipping create_all.",
            retries,
        )
        # Avoid raising so the app can start and the logs make the problem clear.
        return

    # Ensure specific columns/constraints that SQLModel.create_all can't add to existing tables
    try:
        _ensure_category_parent_column()
    except Exception:
        # Keep startup robust: log to stdout but don't crash the app here
        print("Warning: failed to ensure category.parent_id column or constraint")
    try:
        _ensure_admin_email_column()
    except Exception:
        print("Warning: failed to ensure adminuser.email column")
    try:
        # Ensure mpesa_request_id column on orders table for tracking STK push requests
        with engine.begin() as conn:
            col_check = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'order' AND column_name = 'mpesa_request_id'"
                )
            )
            if not col_check.first():
                conn.execute(text("ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS mpesa_request_id varchar"))
    except Exception:
        print("Warning: failed to ensure order.mpesa_request_id column")
    try:
        # Ensure shipping columns on orders table
        with engine.begin() as conn:
            col_check = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'order' AND column_name = 'tracking_number'"
                )
            )
            if not col_check.first():
                conn.execute(text("ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS tracking_number varchar"))
            col_check2 = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'order' AND column_name = 'shipping_provider'"
                )
            )
            if not col_check2.first():
                conn.execute(text("ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS shipping_provider varchar"))
            col_check3 = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'order' AND column_name = 'shipped_at'"
                )
            )
            if not col_check3.first():
                conn.execute(text("ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS shipped_at timestamp"))
    except Exception:
        print("Warning: failed to ensure order.shipping columns")
