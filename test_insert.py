#!/usr/bin/env python3
"""
Test script to insert sample rows into sap_material_data table (PostgreSQL)
"""

import os
import random
from datetime import datetime
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MATERIAL_TYPES = ['ROH', 'HALB', 'FERT', 'DIEN']
PLANTS = ['GB45', 'US45', 'CA35', 'SG30', 'DE30']
PROCUREMENT_TYPES = ['External Procurement',
                     'In-House Production', 'Both Procurement Types']
DESCRIPTIONS = [
    'TEST COMPONENT ASSEMBLY',
    'TEST RAW MATERIAL PART',
    'TEST FINISHED PRODUCT',
    'TEST SERVICE ITEM',
    'TEST SEMI-FINISHED GOOD'
]


def connect_db():
    """Connect to PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'sap_materials'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', '5432'))
        )
        print(
            f"✓ Connected to database: {os.getenv('DB_NAME', 'sap_materials')}")
        return connection
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return None


def generate_test_row(material_number: str, plant: str):
    """Generate a test row with sample data"""
    return {
        'material_number': material_number,
        'plant': plant,
        'material_type': random.choice(MATERIAL_TYPES),
        'modeldata_timestamp': datetime.now(),
        'material_description': random.choice(DESCRIPTIONS),
        'material_base_unit_of_measure': 'EA',
        'procurement_type_planning': random.choice(PROCUREMENT_TYPES),
        'standard_price': round(random.uniform(10, 1000), 2),
        'moving_average_price_periodic_unit_price': round(random.uniform(10, 1000), 2),
        'stock_quantity_total': random.randint(0, 500),
        'value_of_total_valuated_stock': round(random.uniform(100, 50000), 2),
        'safety_stock': random.randint(10, 100),
        'mrp_type': 'MRP',
        'mrp_controller': 'Test Controller',
        'purchasing_group': 'Test Group',
        'material_created_on': datetime.now().date(),
        'material_name_of_person_responsible_for_creating_the_object': 'TEST_USER'
    }


def insert_row(connection, row_data):
    """Insert a row into the database"""
    try:
        cursor = connection.cursor()

        columns = ', '.join(row_data.keys())
        placeholders = ', '.join(['%s'] * len(row_data))
        query = f"INSERT INTO sap_material_data ({columns}) VALUES ({placeholders})"

        cursor.execute(query, list(row_data.values()))
        connection.commit()

        print(f"✓ Inserted: Material {row_data['material_number']}, "
              f"Plant {row_data['plant']}, "
              f"Description: {row_data['material_description']}")

        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Error inserting row: {e}")
        connection.rollback()
        return False


def update_row(connection, material_number, plant):
    """Update an existing row"""
    try:
        cursor = connection.cursor()

        new_price = round(random.uniform(10, 1000), 2)
        query = """
            UPDATE sap_material_data 
            SET standard_price = %s, 
                moving_average_price_periodic_unit_price = %s,
                modeldata_timestamp = %s
            WHERE material_number = %s AND plant = %s
        """

        cursor.execute(query, (new_price, new_price * 0.95,
                       datetime.now(), material_number, plant))
        connection.commit()

        if cursor.rowcount > 0:
            print(
                f"✓ Updated: Material {material_number}, Plant {plant}, New price: {new_price}")
            cursor.close()
            return True
        else:
            print(
                f"✗ No row found to update: Material {material_number}, Plant {plant}")
            cursor.close()
            return False
    except Exception as e:
        print(f"✗ Error updating row: {e}")
        connection.rollback()
        return False


def delete_row(connection, material_number, plant):
    """Delete a row"""
    try:
        cursor = connection.cursor()

        query = "DELETE FROM sap_material_data WHERE material_number = %s AND plant = %s"
        cursor.execute(query, (material_number, plant))
        connection.commit()

        if cursor.rowcount > 0:
            print(f"✓ Deleted: Material {material_number}, Plant {plant}")
            cursor.close()
            return True
        else:
            print(
                f"✗ No row found to delete: Material {material_number}, Plant {plant}")
            cursor.close()
            return False
    except Exception as e:
        print(f"✗ Error deleting row: {e}")
        connection.rollback()
        return False


def main():
    """Main menu"""
    connection = connect_db()
    if not connection:
        return

    print("\n" + "="*60)
    print("SAP Material Database Test Tool (PostgreSQL)")
    print("="*60)
    print("\nOptions:")
    print("1. Insert a new test row")
    print("2. Insert multiple test rows")
    print("3. Update an existing row")
    print("4. Delete a row")
    print("5. Exit")
    print("="*60)

    try:
        while True:
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                material_num = f"TEST{random.randint(10000, 99999)}"
                plant = random.choice(PLANTS)
                row_data = generate_test_row(material_num, plant)
                insert_row(connection, row_data)

            elif choice == '2':
                count = input("How many rows to insert? (default 3): ").strip()
                count = int(count) if count.isdigit() else 3
                for i in range(count):
                    material_num = f"TEST{random.randint(10000, 99999)}"
                    plant = random.choice(PLANTS)
                    row_data = generate_test_row(material_num, plant)
                    insert_row(connection, row_data)

            elif choice == '3':
                material_num = input(
                    "Enter material number to update: ").strip()
                plant = input("Enter plant code: ").strip()
                update_row(connection, material_num, plant)

            elif choice == '4':
                material_num = input(
                    "Enter material number to delete: ").strip()
                plant = input("Enter plant code: ").strip()
                delete_row(connection, material_num, plant)

            elif choice == '5':
                print("\n✓ Exiting...")
                break

            else:
                print("✗ Invalid choice. Please enter 1-5.")

    except KeyboardInterrupt:
        print("\n\n✓ Exiting...")
    finally:
        if connection:
            connection.close()
            print("✓ Database connection closed\n")


if __name__ == '__main__':
    main()
