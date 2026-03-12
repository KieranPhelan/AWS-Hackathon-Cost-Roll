#!/usr/bin/env python3
"""
Seed PostgreSQL RDS with the SAP material database schema
"""

import os
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# PostgreSQL schema (converted from MySQL)
SCHEMA_SQL = """
-- SAP Material Management Database Schema
-- Single table design with all columns from CSV

DROP TABLE IF EXISTS sap_material_data CASCADE;

CREATE TABLE sap_material_data (
    -- Primary identifiers
    material_number VARCHAR(50),
    plant VARCHAR(10),
    
    -- Material basic info
    material_type VARCHAR(10),
    modeldata_timestamp TIMESTAMP,
    material_description TEXT,
    material_base_unit_of_measure VARCHAR(10),
    material_group VARCHAR(50),
    material_external_material_group VARCHAR(50),
    material_product_hierarchy VARCHAR(50),
    material_old_material_number VARCHAR(50),
    material_document_version VARCHAR(50),
    material_general_item_category_group VARCHAR(50),
    
    -- Procurement
    procurement_type_planning VARCHAR(100),
    special_procurement_type VARCHAR(100),
    special_procurement_type_for_costing VARCHAR(100),
    vendor_language_key VARCHAR(10),
    purchasing_group VARCHAR(100),
    planned_delivery_time_in_days INTEGER,
    country_of_origin_of_the_material VARCHAR(10),
    region_of_origin_of_material VARCHAR(50),
    
    -- Pricing
    future_planned_price_2 DECIMAL(15,2),
    date_from_which_future_planned_price_2_is_valid DATE,
    future_planned_price_3 DECIMAL(15,2),
    date_from_which_future_planned_price_3_is_valid DATE,
    price_unit DECIMAL(15,2),
    do_not_cost VARCHAR(10),
    moving_average_price_periodic_unit_price DECIMAL(15,2),
    standard_price DECIMAL(15,2),
    standard_price_in_the_previous_period DECIMAL(15,2),
    previous_planned_price DECIMAL(15,2),
    future_planned_price DECIMAL(15,2),
    
    -- Status fields
    material_cross_plant_material_status VARCHAR(50),
    plant_specific_material_status VARCHAR(50),
    material_cross_distribution_chain_material_status VARCHAR(50),
    material_date_from_which_the_x_distr_chain_material_status_is_valid DATE,
    material_date_from_which_the_cross_plant_material_status_is_valid DATE,
    date_from_which_the_plant_specific_material_status_is_valid DATE,
    
    -- Indicators and flags
    indicator_bulk_material BOOLEAN,
    flag_material_for_deletion_at_plant_level BOOLEAN,
    material_flag_material_for_deletion_at_client_level BOOLEAN,
    batch_management_indicator_internal BOOLEAN,
    material_batch_management_requirement_indicator BOOLEAN,
    indicator_backflush BOOLEAN,
    material_is_costed_with_quantity_structure BOOLEAN,
    lifo_fifo_relevant VARCHAR(5),
    
    -- Cost estimates
    lot_size_for_product_costing DECIMAL(15,2),
    period_of_current_standard_cost_estimate INTEGER,
    fiscal_year_of_current_standard_cost_estimate INTEGER,
    period_of_previous_standard_cost_estimate INTEGER,
    fiscal_year_of_previous_standard_cost_estimate INTEGER,
    costing_overhead_group VARCHAR(100),
    origin_group_as_subdivision_of_cost_element VARCHAR(100),
    material_related_origin VARCHAR(100),
    
    -- Inventory
    total_valuated_stock DECIMAL(15,2),
    value_of_total_valuated_stock DECIMAL(15,2),
    stock_quantity_total DECIMAL(15,2),
    financial_value_stocks DECIMAL(15,2),
    safety_stock DECIMAL(15,2),
    
    -- Organization
    profit_center VARCHAR(50),
    abc_indicator VARCHAR(10),
    valuation_class VARCHAR(50),
    
    -- MRP (Material Requirements Planning)
    mrp_type VARCHAR(50),
    mrp_group VARCHAR(100),
    mrp_controller VARCHAR(100),
    lot_size_materials_planning VARCHAR(50),
    minimum_lot_size DECIMAL(15,2),
    maximum_lot_size DECIMAL(15,2),
    fixed_lot_size DECIMAL(15,2),
    production_supervisor VARCHAR(100),
    checking_group_for_availability_check VARCHAR(100),
    
    -- Storage and handling
    material_storage_conditions VARCHAR(100),
    material_temperature_conditions_indicator VARCHAR(100),
    material_minimum_remaining_shelf_life INTEGER,
    material_total_shelf_life INTEGER,
    material_period_indicator_for_shelf_life_expiration_date VARCHAR(50),
    maximum_storage_period INTEGER,
    unit_for_maximum_storage_period VARCHAR(50),
    physical_inventory_indicator_for_cycle_counting VARCHAR(100),
    serial_number_profile VARCHAR(100),
    
    -- Foreign trade
    commodity_code_import_code_number_for_foreign_trade VARCHAR(100),
    component_scrap_in_percent DECIMAL(5,2),
    material_country_of_origin_of_the_material VARCHAR(10),
    
    -- Audit fields
    material_name_of_person_responsible_for_creating_the_object VARCHAR(100),
    material_created_on DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (material_number, plant)
);

-- Create indexes for common queries
CREATE INDEX idx_material_type ON sap_material_data(material_type);
CREATE INDEX idx_material_group ON sap_material_data(material_group);
CREATE INDEX idx_plant ON sap_material_data(plant);
CREATE INDEX idx_profit_center ON sap_material_data(profit_center);
CREATE INDEX idx_mrp_controller ON sap_material_data(mrp_controller);
CREATE INDEX idx_purchasing_group ON sap_material_data(purchasing_group);
CREATE INDEX idx_created_on ON sap_material_data(material_created_on);
CREATE INDEX idx_updated_at ON sap_material_data(updated_at);

-- Create trigger to automatically update updated_at on row changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sap_material_data_updated_at
    BEFORE UPDATE ON sap_material_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


def main():
    print("="*60)
    print("PostgreSQL RDS Schema Seeder")
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

    # Confirm
    response = input(
        "\n⚠️  This will DROP and recreate the table. Continue? (yes/no): ")
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

        # Execute schema
        print("\n📝 Creating schema...")
        cursor = connection.cursor()
        cursor.execute(SCHEMA_SQL)
        connection.commit()
        print("✓ Schema created successfully")

        # Verify table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sap_material_data'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"\n✓ Table created with {len(columns)} columns")

        # Check row count
        cursor.execute("SELECT COUNT(*) FROM sap_material_data")
        count = cursor.fetchone()[0]
        print(f"✓ Current row count: {count}")

        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("✅ Schema seeded successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Load data from CSV (if needed)")
        print("2. Run: python check_connection.py")
        print("3. Run: python db_monitor.py")
        print("4. Test with: python quick_test.py")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   → Check your .env file has correct RDS credentials")
        print("   → Verify RDS security group allows your IP on port 5432")
        print("   → Ensure database exists (create it in RDS console if needed)")


if __name__ == '__main__':
    main()
