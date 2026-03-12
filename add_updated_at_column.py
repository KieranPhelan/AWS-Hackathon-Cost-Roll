#!/usr/bin/env python3
"""
Migration script to add updated_at column to existing table
"""

import os
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MIGRATION_SQL = """
-- Add updated_at column with default value
ALTER TABLE sap_material_data 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Set updated_at for existing rows (use modeldata_timestamp if available, otherwise now)
UPDATE sap_material_data 
SET updated_at = COALESCE(modeldata_timestamp, CURRENT_TIMESTAMP)
WHERE updated_at IS NULL;

-- Create index on updated_at for efficient queries
CREATE INDEX IF NOT EXISTS idx_updated_at ON sap_material_data(updated_at);

-- Create trigger function to automatically update updated_at on row changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if it exists and recreate it
DROP TRIGGER IF EXISTS update_sap_material_data_updated_at ON sap_material_data;

CREATE TRIGGER update_sap_material_data_updated_at
    BEFORE UPDATE ON sap_material_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


def main():
    print("="*60)
    print("Add updated_at Column Migration")
    print("="*60)

    # Get connection details
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '5432'))
    database = os.getenv('DB_NAME', 'sap_materials')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')

    print(f"\n📋 Target Database:")
    print(f"   Host: {host}")
    print(f"   Database: {database}")
    print(f"   User: {user}")

    print("\n📝 This migration will:")
    print("   1. Add 'updated_at' column to sap_material_data table")
    print("   2. Set initial values from modeldata_timestamp")
    print("   3. Create index on updated_at for performance")
    print("   4. Create trigger to auto-update on changes")

    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Aborted")
        return

    try:
        # Connect
        print("\n🔌 Connecting to database...")
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("✓ Connected")

        # Execute migration
        print("\n📝 Running migration...")
        cursor = connection.cursor()
        cursor.execute(MIGRATION_SQL)
        connection.commit()
        print("✓ Migration completed successfully")

        # Verify
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'sap_material_data' 
            AND column_name = 'updated_at'
        """)
        result = cursor.fetchone()

        if result:
            print(f"\n✓ Column 'updated_at' added:")
            print(f"   Type: {result[1]}")
            print(f"   Default: {result[2]}")

        # Check trigger
        cursor.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE event_object_table = 'sap_material_data'
            AND trigger_name = 'update_sap_material_data_updated_at'
        """)
        trigger = cursor.fetchone()

        if trigger:
            print(f"✓ Trigger created: {trigger[0]}")

        # Check index
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'sap_material_data'
            AND indexname = 'idx_updated_at'
        """)
        index = cursor.fetchone()

        if index:
            print(f"✓ Index created: {index[0]}")

        # Get sample data
        cursor.execute("""
            SELECT material_number, plant, updated_at 
            FROM sap_material_data 
            LIMIT 3
        """)
        samples = cursor.fetchall()

        print(f"\n✓ Sample data:")
        for sample in samples:
            print(f"   {sample[0]} | {sample[1]} | {sample[2]}")

        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. The monitor will now use updated_at for efficient change detection")
        print("2. Run: python db_monitor.py")
        print("3. Test with: python quick_test.py")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
