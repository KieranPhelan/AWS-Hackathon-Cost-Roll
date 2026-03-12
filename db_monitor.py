#!/usr/bin/env python3
"""
SAP Material Database Monitor - PostgreSQL Version
Monitors the sap_material_data table for changes and outputs them to console
"""

import time
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseMonitor:
    # Cost-roll error codes and messages
    BLOCKED_STATUS_CODES = {
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

    def __init__(self, host: str, database: str, user: str, password: str,
                 port: int = 5432, poll_interval: int = 5, auto_fix_blocked: bool = True):
        """Initialize the database monitor for PostgreSQL"""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.poll_interval = poll_interval
        self.auto_fix_blocked = auto_fix_blocked
        self.connection = None
        self.last_check_time = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print(f"✓ Connected to PostgreSQL database: {self.database}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def get_table_snapshot(self) -> Optional[Dict]:
        """Get current snapshot of the table"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)

            # Get row count
            cursor.execute("SELECT COUNT(*) as count FROM sap_material_data")
            count_result = cursor.fetchone()
            row_count = count_result['count']

            # Get all data ordered consistently for hashing
            cursor.execute("""
                SELECT * FROM sap_material_data 
                ORDER BY material_number, plant
            """)
            rows = cursor.fetchall()

            # Convert to list of dicts for JSON serialization
            rows_list = [dict(row) for row in rows]

            # Create hash of all data
            data_str = json.dumps(rows_list, default=str, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()

            cursor.close()

            return {
                'row_count': row_count,
                'data_hash': data_hash,
                'timestamp': datetime.now(),
                'rows': rows_list
            }
        except Exception as e:
            print(f"✗ Error getting table snapshot: {e}")
            return None

    def detect_changes(self, old_snapshot: Dict, new_snapshot: Dict) -> Dict:
        """Detect what changed between snapshots"""
        changes = {
            'has_changes': False,
            'row_count_changed': False,
            'data_modified': False,
            'old_count': old_snapshot['row_count'],
            'new_count': new_snapshot['row_count'],
            'added_rows': [],
            'deleted_rows': [],
            'modified_rows': []
        }

        # Check if row count changed
        if old_snapshot['row_count'] != new_snapshot['row_count']:
            changes['has_changes'] = True
            changes['row_count_changed'] = True

        # Check if data hash changed
        if old_snapshot['data_hash'] != new_snapshot['data_hash']:
            changes['has_changes'] = True
            changes['data_modified'] = True

            # Detailed change detection
            old_rows = {(r['material_number'], r['plant']): r
                        for r in old_snapshot['rows']}
            new_rows = {(r['material_number'], r['plant']): r
                        for r in new_snapshot['rows']}

            # Find added rows
            for key in new_rows:
                if key not in old_rows:
                    changes['added_rows'].append(new_rows[key])

            # Find deleted rows
            for key in old_rows:
                if key not in new_rows:
                    changes['deleted_rows'].append(old_rows[key])

            # Find modified rows
            for key in old_rows:
                if key in new_rows and old_rows[key] != new_rows[key]:
                    changes['modified_rows'].append({
                        'key': key,
                        'old': old_rows[key],
                        'new': new_rows[key]
                    })

        return changes

    def check_cost_roll_errors(self, rows: list) -> list:
        """Check for cost-roll errors based on material status codes"""
        errors = []

        for row in rows:
            status = row.get('material_cross_plant_material_status', '')
            if status and status in self.BLOCKED_STATUS_CODES:
                errors.append({
                    'material_number': row.get('material_number'),
                    'plant': row.get('plant'),
                    'material_description': row.get('material_description'),
                    'status_code': status,
                    'error_message': self.BLOCKED_STATUS_CODES[status],
                    'material_type': row.get('material_type'),
                    'material_group': row.get('material_group')
                })

        return errors

    def fix_blocked_materials(self, errors: list) -> int:
        """
        Fix blocked materials by clearing the material_date_from_which_the_cross_plant_material_status_is_valid field
        Returns the number of materials fixed
        """
        if not errors:
            return 0

        fixed_count = 0

        try:
            cursor = self.connection.cursor()

            for error in errors:
                material_number = error['material_number']
                plant = error['plant']
                status_code = error['status_code']

                # Clear both the date field and status code to fix the blocked status
                query = """
                    UPDATE sap_material_data 
                    SET material_date_from_which_the_cross_plant_material_status_is_valid = NULL,
                        material_cross_plant_material_status = NULL
                    WHERE material_number = %s AND plant = %s
                """

                cursor.execute(query, (material_number, plant))

                if cursor.rowcount > 0:
                    fixed_count += 1
                    # Log each fix
                    print(
                        f"   🔧 Fixed Material {material_number} | Plant {plant}")
                    print(
                        f"      ↳ Cleared status code: {status_code} ({self.BLOCKED_STATUS_CODES[status_code]})")
                    print(
                        f"      ↳ Cleared date field: material_date_from_which_the_cross_plant_material_status_is_valid")

            self.connection.commit()
            cursor.close()

        except Exception as e:
            print(f"\n✗ Error fixing blocked materials: {e}")
            self.connection.rollback()

        return fixed_count

    def print_cost_roll_errors(self, errors: list, auto_fix: bool = True):
        """Print cost-roll errors to console"""
        if not errors:
            return

        print("\n" + "="*80)
        print(
            f"⚠️  COST-ROLL ERRORS DETECTED: {len(errors)} materials blocked")
        print("="*80)

        for error in errors[:10]:  # Show first 10
            print(
                f"\n❌ Material: {error['material_number']} | Plant: {error['plant']}")
            print(f"   Status Code: {error['status_code']}")
            print(f"   Error: {error['error_message']}")
            if error['material_description']:
                desc = error['material_description'][:60]
                print(f"   Description: {desc}")
            print(
                f"   Type: {error['material_type']} | Group: {error['material_group']}")

        if len(errors) > 10:
            print(f"\n   ... and {len(errors) - 10} more blocked materials")

        print("\n" + "="*80)

        # Auto-fix blocked materials
        if auto_fix:
            print("\n🔧 Attempting to fix blocked materials...")
            fixed_count = self.fix_blocked_materials(errors)

            if fixed_count > 0:
                print(f"✅ Fixed {fixed_count} blocked material(s)")
                print(
                    "   Cleared status codes and date fields")
            else:
                print("⚠️  No materials were fixed")

        print("\n" + "="*80 + "\n")

    def print_changes(self, changes: Dict):
        """Print detected changes to console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print("\n" + "="*80)
        print(f"🔔 CHANGE DETECTED at {timestamp}")
        print("="*80)

        if changes['row_count_changed']:
            print(
                f"\n📊 Row Count: {changes['old_count']} → {changes['new_count']}")
            delta = changes['new_count'] - changes['old_count']
            if delta > 0:
                print(f"   (+{delta} rows added)")
            else:
                print(f"   ({delta} rows removed)")

        if changes['added_rows']:
            print(f"\n➕ Added Rows: {len(changes['added_rows'])}")
            for row in changes['added_rows'][:5]:
                desc = row.get('material_description', 'N/A')
                desc_str = desc[:50] if desc else 'N/A'
                print(f"   • Material: {row['material_number']}, "
                      f"Plant: {row['plant']}, "
                      f"Description: {desc_str}")
            if len(changes['added_rows']) > 5:
                print(f"   ... and {len(changes['added_rows']) - 5} more")

        if changes['deleted_rows']:
            print(f"\n➖ Deleted Rows: {len(changes['deleted_rows'])}")
            for row in changes['deleted_rows'][:5]:
                desc = row.get('material_description', 'N/A')
                desc_str = desc[:50] if desc else 'N/A'
                print(f"   • Material: {row['material_number']}, "
                      f"Plant: {row['plant']}, "
                      f"Description: {desc_str}")
            if len(changes['deleted_rows']) > 5:
                print(f"   ... and {len(changes['deleted_rows']) - 5} more")

        if changes['modified_rows']:
            print(f"\n✏️  Modified Rows: {len(changes['modified_rows'])}")
            for mod in changes['modified_rows'][:3]:
                print(
                    f"   • Material: {mod['key'][0]}, Plant: {mod['key'][1]}")
                old_row = mod['old']
                new_row = mod['new']
                changed_fields = []
                for key in old_row:
                    if old_row[key] != new_row[key]:
                        changed_fields.append(key)
                print(f"     Changed fields: {', '.join(changed_fields[:5])}")
                if len(changed_fields) > 5:
                    print(
                        f"     ... and {len(changed_fields) - 5} more fields")
            if len(changes['modified_rows']) > 3:
                print(f"   ... and {len(changes['modified_rows']) - 3} more")

        print("\n" + "="*80 + "\n")

    def monitor(self):
        """Main monitoring loop"""
        print("\n" + "="*80)
        print("🔍 SAP Material Database Monitor Started (PostgreSQL)")
        print("="*80)
        print(f"Database: {self.database}")
        print(f"Host: {self.host}")
        print(f"Table: sap_material_data")
        print(f"Poll Interval: {self.poll_interval} seconds")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print("\nPress Ctrl+C to stop monitoring\n")

        if not self.connect():
            return

        try:
            # Get initial snapshot
            print("📸 Taking initial snapshot...")
            self.last_snapshot = self.get_table_snapshot()
            if self.last_snapshot:
                print(
                    f"✓ Initial snapshot: {self.last_snapshot['row_count']} rows")

                # Check for cost-roll errors in initial snapshot
                print("\n🔍 Checking for cost-roll errors...")
                cost_roll_errors = self.check_cost_roll_errors(
                    self.last_snapshot['rows'])
                if cost_roll_errors:
                    self.print_cost_roll_errors(
                        cost_roll_errors, auto_fix=self.auto_fix_blocked)
                else:
                    print("✓ No cost-roll errors found in current data")
            else:
                print("✗ Failed to get initial snapshot")
                return

            # Monitoring loop
            while True:
                time.sleep(self.poll_interval)

                # Get new snapshot
                new_snapshot = self.get_table_snapshot()
                if not new_snapshot:
                    continue

                # Detect changes
                changes = self.detect_changes(self.last_snapshot, new_snapshot)

                if changes['has_changes']:
                    self.print_changes(changes)

                    # Check for cost-roll errors in changed rows
                    rows_to_check = []
                    rows_to_check.extend(changes['added_rows'])
                    rows_to_check.extend([mod['new']
                                         for mod in changes['modified_rows']])

                    if rows_to_check:
                        cost_roll_errors = self.check_cost_roll_errors(
                            rows_to_check)
                        if cost_roll_errors:
                            self.print_cost_roll_errors(
                                cost_roll_errors, auto_fix=self.auto_fix_blocked)

                    self.last_snapshot = new_snapshot
                else:
                    # Heartbeat
                    print(
                        f"⏱️  {datetime.now().strftime('%H:%M:%S')} - No changes", end='\r')

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    import os

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'sap_materials'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '5432')),
        'poll_interval': int(os.getenv('POLL_INTERVAL', '5')),
        'auto_fix_blocked': os.getenv('AUTO_FIX_BLOCKED', 'true').lower() == 'true'
    }

    monitor = DatabaseMonitor(**config)
    monitor.monitor()


if __name__ == '__main__':
    main()
