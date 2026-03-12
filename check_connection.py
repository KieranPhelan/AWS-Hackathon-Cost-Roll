#!/usr/bin/env python3
"""
PostgreSQL RDS connection diagnostic tool
"""

import os
import socket

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

print("="*60)
print("PostgreSQL RDS Connection Diagnostics")
print("="*60)

# Check configuration
host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', '5432'))
database = os.getenv('DB_NAME', 'sap_materials')
user = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASSWORD', '')

print(f"\n📋 Configuration:")
print(f"   Host: {host}")
print(f"   Port: {port}")
print(f"   Database: {database}")
print(f"   User: {user}")
print(f"   Password: {'*' * len(password) if password else '(empty)'}")

# Test network connectivity
print(f"\n🔌 Testing network connectivity to {host}:{port}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()

    if result == 0:
        print(f"   ✓ Port {port} is open and reachable")
    else:
        print(f"   ✗ Cannot connect to port {port}")
        print(f"   → Is PostgreSQL RDS instance running?")
        print(f"   → Check security group rules")
        print(f"   → Verify VPC and network settings")
except socket.gaierror:
    print(f"   ✗ Cannot resolve hostname: {host}")
except Exception as e:
    print(f"   ✗ Network error: {e}")

# Try PostgreSQL connection
print(f"\n🔐 Testing PostgreSQL connection...")
try:
    import psycopg2

    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=10
    )

    print(f"   ✓ Successfully connected to PostgreSQL Server")

    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   ✓ PostgreSQL version: {version.split(',')[0]}")

    cursor.execute("SELECT current_database();")
    db = cursor.fetchone()[0]
    print(f"   ✓ Connected to database: {db}")

    # Check if table exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'sap_material_data'
    """)

    table_exists = cursor.fetchone()[0]
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM sap_material_data")
        row_count = cursor.fetchone()[0]
        print(f"   ✓ Table 'sap_material_data' exists with {row_count} rows")
    else:
        print(f"   ⚠️  Table 'sap_material_data' does not exist")
        print(f"   → Run the schema SQL to create the table")

    cursor.close()
    connection.close()

    print("\n✅ All checks passed! Database is ready.")

except ImportError:
    print("   ✗ psycopg2 not installed")
    print("   → Run: pip install -r requirements.txt")
except Exception as e:
    print(f"   ✗ PostgreSQL Error: {e}")

    error_str = str(e)
    if "password authentication failed" in error_str:
        print("\n💡 Troubleshooting:")
        print("   → Check username and password in .env file")
    elif "database" in error_str and "does not exist" in error_str:
        print("\n💡 Troubleshooting:")
        print("   → Database doesn't exist. Create it in RDS console or via psql")
    elif "timeout" in error_str or "could not connect" in error_str:
        print("\n💡 Troubleshooting:")
        print("   → Check RDS security group allows inbound on port 5432")
        print("   → Verify RDS instance is publicly accessible (if needed)")
        print("   → Check VPC and subnet configuration")

print("\n" + "="*60)
