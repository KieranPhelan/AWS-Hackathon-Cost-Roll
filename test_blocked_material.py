#!/usr/bin/env python3
"""
Test script to insert materials with blocked status codes
to test cost-roll error detection
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

# Blocked status codes
BLOCKED_CODES = {
    '07': 'Blocked-Shell/Pre-release',
    '08': 'Matl under Construction',
    'AB': 'All Blocks',
    'BE': 'Block all except service',
    'CC': 'Blocked- Costing Cleanse',
    'CP': 'Blocked in Closed Plant',
    'DG': 'Blocked for Cleanse - GDG',
    'MC': 'Blocked- Material Cleanse',
    'ZW': 'Workflow Block'
}


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
        print(f"✓ Connected to database")
        return connection
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return None


def insert_blocked_material(connection, status_code):
    """Insert a material with a blocked status code"""
    try:
        cursor = connection.cursor()

        material_number = f"BLOCK{random.randint(1000, 9999)}"
        plant = random.choice(['GB45', 'US45', 'CA35'])

        query = """
            INSERT INTO sap_material_data 
            (material_number, plant, material_type, modeldata_timestamp,
             material_description, material_base_unit_of_measure,
             material_cross_plant_material_status, standard_price,
             stock_quantity_total, material_created_on, material_group)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            material_number,
            plant,
            'ROH',
            datetime.now(),
            f'TEST BLOCKED MATERIAL - {BLOCKED_CODES[status_code]}',
            'EA',
            status_code,  # This will trigger cost-roll error
            round(random.uniform(10, 1000), 2),
            random.randint(0, 500),
            datetime.now().date(),
            'TEST_GROUP'
        )

        cursor.execute(query, values)
        connection.commit()

        print(f"✓ Inserted blocked material:")
        print(f"  Material: {material_number}")
        print(f"  Plant: {plant}")
        print(f"  Status Code: {status_code}")
        print(f"  Error: {BLOCKED_CODES[status_code]}")

        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Error inserting material: {e}")
        connection.rollback()
        return False


def main():
    print("="*60)
    print("Blocked Material Test Tool")
    print("="*60)
    print("\nThis will insert materials with blocked status codes")
    print("to test cost-roll error detection in the monitor.\n")

    connection = connect_db()
    if not connection:
        return

    print("Available blocked status codes:")
    for code, message in BLOCKED_CODES.items():
        print(f"  {code}: {message}")

    print("\nOptions:")
    print("1. Insert one blocked material (random code)")
    print("2. Insert multiple blocked materials")
    print("3. Insert specific status code")
    print("4. Exit")

    try:
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                code = random.choice(list(BLOCKED_CODES.keys()))
                insert_blocked_material(connection, code)

            elif choice == '2':
                count = input("How many? (default 3): ").strip()
                count = int(count) if count.isdigit() else 3
                for i in range(count):
                    code = random.choice(list(BLOCKED_CODES.keys()))
                    insert_blocked_material(connection, code)

            elif choice == '3':
                code = input(
                    "Enter status code (e.g., AB, CC, ZW): ").strip().upper()
                if code in BLOCKED_CODES:
                    insert_blocked_material(connection, code)
                else:
                    print(
                        f"✗ Invalid code. Must be one of: {', '.join(BLOCKED_CODES.keys())}")

            elif choice == '4':
                print("\n✓ Exiting...")
                break

            else:
                print("✗ Invalid choice. Please enter 1-4.")

    except KeyboardInterrupt:
        print("\n\n✓ Exiting...")
    finally:
        if connection:
            connection.close()
            print("✓ Database connection closed\n")


if __name__ == '__main__':
    main()
