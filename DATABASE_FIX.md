# Database Migration Instructions

## Issues Fixed

1. **Removed `customer_id` from Order model** - This column doesn't exist in your database
2. **Fixed bcrypt password hashing** - Added fallback for version compatibility
3. **Created migration script** - To add new columns to existing `order` table

## Steps to Fix

### Option 1: Automatic Migration (Recommended)

The migration will run automatically when you restart the server. The startup event will attempt to add missing columns.

### Option 2: Manual Migration

Run the migration script manually:

```bash
cd /home/oruma/morine-gypsum
python migrate_database.py
```

Or run it directly:

```bash
python -m app.db.migrate_order_table
```

### Option 3: SQL Migration (If script fails)

Connect to your PostgreSQL database and run:

```sql
-- Add missing columns to order table
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS customer_email VARCHAR(255);
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS mpesa_code VARCHAR(20);
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS payment_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS total_amount NUMERIC(10, 2);
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS shipping_cost NUMERIC(10, 2) DEFAULT 500.0;
ALTER TABLE "order" ADD COLUMN IF NOT EXISTS notes TEXT;

-- Update status default
ALTER TABLE "order" ALTER COLUMN status SET DEFAULT 'pending';
```

## After Migration

1. Restart your FastAPI server
2. The application should now work correctly
3. Test by creating an order through the frontend

## Notes

- The `customer_id` column has been removed from the Order model to match your existing database schema
- Password hashing now has a fallback for bcrypt version compatibility
- All new order fields are optional and will be added automatically

