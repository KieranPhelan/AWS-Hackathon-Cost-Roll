#!/usr/bin/env python3
"""
Load SAP data from CSV into PostgreSQL RDS
"""

import os
import csv
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Column mapping from CSV to database
COLUMN_MAPPING = {
    'Material Material Type': 'material_type',
    'Modeldata_Timestamp': 'modeldata_timestamp',
    'Procurement Type Planning': 'procurement_type_planning',
    'Special procurement type': 'special_procurement_type',
    'Special Procurement Type for Costing': 'special_procurement_type_for_costing',
    'Vendor Language Key': 'vendor_language_key',
    'Material Description': 'material_description',
    'Future Planned Price 2': 'future_planned_price_2',
    'Date from Which Future Planned Price 2 Is Valid': 'date_from_which_future_planned_price_2_is_valid',
    'Future Planned Price 3': 'future_planned_price_3',
    'Date from Which Future Planned Price 3 Is Valid': 'date_from_which_future_planned_price_3_is_valid',
    'Material Cross-Plant Material Status': 'material_cross_plant_material_status',
    'Plant-Specific Material Status': 'plant_specific_material_status',
    'Indicator: Bulk Material': 'indicator_bulk_material',
    'Price Unit': 'price_unit',
    'Do Not Cost': 'do_not_cost',
    'Moving Average Price/Periodic Unit Price': 'moving_average_price_periodic_unit_price',
    'Standard price': 'standard_price',
    'Lot Size for Product Costing': 'lot_size_for_product_costing',
    'Material Base Unit of Measure': 'material_base_unit_of_measure',
    'Period of Current Standard Cost Estimate': 'period_of_current_standard_cost_estimate',
    'Fiscal Year of Current Standard Cost Estimate': 'fiscal_year_of_current_standard_cost_estimate',
    'Period of Previous Standard Cost Estimate': 'period_of_previous_standard_cost_estimate',
    'Fiscal Year of Previous Standard Cost Estimate': 'fiscal_year_of_previous_standard_cost_estimate',
    'Previous planned price': 'previous_planned_price',
    'Material Product Hierarchy': 'material_product_hierarchy',
    'Material External Material Group': 'material_external_material_group',
    'Costing Overhead Group': 'costing_overhead_group',
    'Material Date from which the X-distr.-chain material status is valid': 'material_date_from_which_the_x_distr_chain_material_status_is_valid',
    'Total Valuated Stock': 'total_valuated_stock',
    'Value of Total Valuated Stock': 'value_of_total_valuated_stock',
    'LIFO/FIFO-Relevant': 'lifo_fifo_relevant',
    'Profit Center': 'profit_center',
    'Material Material Group': 'material_group',
    'Safety Stock': 'safety_stock',
    'Material Name of Person Responsible for Creating the Object': 'material_name_of_person_responsible_for_creating_the_object',
    'Material Created On': 'material_created_on',
    'Standard price in the previous period': 'standard_price_in_the_previous_period',
    'MRP Group': 'mrp_group',
    'Minimum Lot Size': 'minimum_lot_size',
    'Maximum Lot Size': 'maximum_lot_size',
    'Fixed lot size': 'fixed_lot_size',
    'Country of origin of the material': 'country_of_origin_of_the_material',
    'MRP Type': 'mrp_type',
    'MRP Controller': 'mrp_controller',
    'Purchasing Group': 'purchasing_group',
    'Financial Value Stocks': 'financial_value_stocks',
    'Stock Quantity Total': 'stock_quantity_total',
    'Flag Material for Deletion at Plant Level': 'flag_material_for_deletion_at_plant_level',
    'Material Old material number': 'material_old_material_number',
    'Material Document version (without Document Management system)': 'material_document_version',
    'Material Cross-distribution-chain material status': 'material_cross_distribution_chain_material_status',
    'Material Date from which the cross-plant material status is valid': 'material_date_from_which_the_cross_plant_material_status_is_valid',
    'Material Minimum Remaining Shelf Life': 'material_minimum_remaining_shelf_life',
    'Material Total shelf life': 'material_total_shelf_life',
    'Material Period Indicator for Shelf Life Expiration Date': 'material_period_indicator_for_shelf_life_expiration_date',
    'Material General item category group': 'material_general_item_category_group',
    'Batch management indicator (internal)': 'batch_management_indicator_internal',
    'ABC Indicator': 'abc_indicator',
    'Planned Delivery Time in Days': 'planned_delivery_time_in_days',
    'Lot size (materials planning)': 'lot_size_materials_planning',
    'Indicator: Backflush': 'indicator_backflush',
    'Production Supervisor': 'production_supervisor',
    'Maximum Storage Period': 'maximum_storage_period',
    'Unit for maximum storage period': 'unit_for_maximum_storage_period',
    'Checking Group for Availability Check': 'checking_group_for_availability_check',
    'Commodity Code/Import Code Number for Foreign Trade': 'commodity_code_import_code_number_for_foreign_trade',
    'Region of origin of material (non-preferential origin)': 'region_of_origin_of_material',
    'Component scrap in percent': 'component_scrap_in_percent',
    'Physical inventory indicator for cycle counting': 'physical_inventory_indicator_for_cycle_counting',
    'Serial Number Profile': 'serial_number_profile',
    'Valuation Class': 'valuation_class',
    'Origin Group as Subdivision of Cost Element': 'origin_group_as_subdivision_of_cost_element',
    'Material-related origin': 'material_related_origin',
    'Material Storage conditions': 'material_storage_conditions',
    'Material Temperature conditions indicator': 'material_temperature_conditions_indicator',
    'Date from which the plant-specific material status is valid': 'date_from_which_the_plant_specific_material_status_is_valid',
    'Future planned price': 'future_planned_price',
    'Material Is Costed with Quantity Structure': 'material_is_costed_with_quantity_structure',
    'Material Flag Material for Deletion at Client Level': 'material_flag_material_for_deletion_at_client_level',
    'Material Number': 'material_number',
    'Plant': 'plant',
    'Material Batch management requirement indicator': 'material_batch_management_requirement_indicator',
    'Material Country of origin of the material': 'material_country_of_origin_of_the_material'
}


def parse_value(value, field_name):
    """Parse and convert CSV values to appropriate types"""
    if not value or value.strip() == '':
        return None

    value = value.strip()

    # Boolean fields
    if 'indicator' in field_name.lower() or 'flag' in field_name.lower():
        return value.lower() == 'true'

    # Date fields
    if 'date' in field_name.lower() or 'created_on' in field_name.lower():
        try:
            return datetime.strptime(value, '%d/%m/%Y').date()
        except:
            return None

    # Timestamp fields
    if 'timestamp' in field_name.lower():
        try:
            return datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
        except:
            return None

    # Numeric fields
    if any(x in field_name.lower() for x in ['price', 'stock', 'value', 'size', 'period', 'year', 'time', 'percent', 'scrap']):
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value) if value else None
        except:
            return None

    return value


def load_csv_to_rds(csv_file, batch_size=1000):
    """Load CSV data into PostgreSQL RDS"""
    print("="*60)
    print("CSV Data Loader for PostgreSQL RDS")
    print("="*60)

    # Connection details
    host = os.getenv('DB_HOST', 'localhost')
    database = os.getenv('DB_NAME', 'sap_materials')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    port = int(os.getenv('DB_PORT', '5432'))

    print(f"\n📋 Configuration:")
    print(f"   CSV File: {csv_file}")
    print(f"   Database: {database}")
    print(f"   Host: {host}")
    print(f"   Batch Size: {batch_size}")

    try:
        # Connect to database
        print("\n🔌 Connecting to database...")
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("✓ Connected")

        # Read CSV
        print(f"\n📖 Reading CSV file...")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)

        print(f"✓ Found {len(rows)} rows in CSV")

        # Prepare data for insertion
        print("\n🔄 Processing data...")
        processed_rows = []
        errors = 0

        for idx, row in enumerate(rows):
            try:
                processed_row = {}
                for csv_col, db_col in COLUMN_MAPPING.items():
                    if csv_col in row:
                        processed_row[db_col] = parse_value(
                            row[csv_col], db_col)

                processed_rows.append(processed_row)

                if (idx + 1) % 1000 == 0:
                    print(
                        f"   Processed {idx + 1}/{len(rows)} rows...", end='\r')
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"\n   ⚠️  Error processing row {idx + 1}: {e}")

        print(f"\n✓ Processed {len(processed_rows)} rows ({errors} errors)")

        # Insert data in batches
        print(f"\n💾 Inserting data into database...")
        cursor = connection.cursor()

        # Get all column names from first row
        if processed_rows:
            columns = list(processed_rows[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"""
                INSERT INTO sap_material_data ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (material_number, plant) DO NOTHING
            """

            # Prepare values
            values = []
            for row in processed_rows:
                values.append(tuple(row.get(col) for col in columns))

            # Insert in batches
            inserted = 0
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                execute_batch(cursor, insert_query, batch)
                connection.commit()
                inserted += len(batch)
                print(
                    f"   Inserted {inserted}/{len(values)} rows...", end='\r')

            print(f"\n✓ Inserted {inserted} rows")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM sap_material_data")
        total_count = cursor.fetchone()[0]
        print(f"✓ Total rows in database: {total_count}")

        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("✅ Data loaded successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python check_connection.py")
        print("2. Run: python db_monitor.py")
        print("3. Test with: python quick_test.py")

    except FileNotFoundError:
        print(f"\n✗ Error: CSV file not found: {csv_file}")
        print("   Make sure 'main SAP Data.csv' is in the current directory")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys

    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'main SAP Data.csv'
    load_csv_to_rds(csv_file)
