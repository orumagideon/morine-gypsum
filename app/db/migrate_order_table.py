# app/db/migrate_order_table.py
"""
Migration script to add new columns to the existing 'order' table.
Run this once to update your database schema.
"""
from sqlalchemy import text, inspect
from app.db.session import engine

def migrate_order_table():
    """Add new columns to the order table if they don't exist."""
    try:
        with engine.begin() as conn:  # Use begin() for transaction management
            # Check and add columns one by one
            columns_to_add = [
                ("customer_email", "VARCHAR(255)"),
                ("payment_method", "VARCHAR(50)"),
                ("payment_status", "VARCHAR(50) DEFAULT 'pending'"),
                ("mpesa_code", "VARCHAR(20)"),
                ("payment_verified", "BOOLEAN DEFAULT FALSE"),
                ("total_amount", "NUMERIC(10, 2)"),
                ("shipping_cost", "NUMERIC(10, 2) DEFAULT 500.0"),
                ("notes", "TEXT"),
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    # Check if column exists (PostgreSQL)
                    check_query = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'order' AND column_name = :col_name
                    """)
                    result = conn.execute(check_query, {"col_name": column_name})
                    if result.fetchone() is None:
                        # Column doesn't exist, add it
                        alter_query = text(f'ALTER TABLE "order" ADD COLUMN {column_name} {column_type}')
                        conn.execute(alter_query)
                        print(f"✓ Added column: {column_name}")
                    else:
                        print(f"  Column {column_name} already exists")
                except Exception as e:
                    print(f"✗ Error adding column {column_name}: {e}")
                    # Continue with other columns
            
            # Update status column default if needed
            try:
                update_status = text('ALTER TABLE "order" ALTER COLUMN status SET DEFAULT \'pending\'')
                conn.execute(update_status)
                print("✓ Updated status column default")
            except Exception as e:
                print(f"  Status column update (may already be set): {e}")
            
            print("\nMigration completed successfully!")
    except Exception as e:
        print(f"Migration error: {e}")
        print("You may need to run this manually or check database permissions.")

if __name__ == "__main__":
    migrate_order_table()

