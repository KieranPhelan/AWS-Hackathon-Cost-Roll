# SAP Material Database Monitor

A Python agent that monitors the `sap_material_data` table for changes and outputs detected changes to the console in real-time.

## Features

- 🔍 Real-time monitoring of database changes
- ➕ Detects added rows
- ➖ Detects deleted rows
- ✏️ Detects modified rows with field-level change tracking
- 📊 Row count tracking
- ⏱️ Configurable polling interval
- 🎨 Clean, formatted console output

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Configuration

Set the following environment variables in `.env`:

- `DB_HOST`: Database host (default: localhost)
- `DB_NAME`: Database name (default: sap_materials)
- `DB_USER`: Database user (default: root)
- `DB_PASSWORD`: Database password
- `DB_PORT`: Database port (default: 3306)
- `POLL_INTERVAL`: Seconds between checks (default: 5)

## Usage

### Basic Usage
```bash
python db_monitor.py
```

### With Environment Variables
```bash
DB_HOST=localhost DB_NAME=sap_materials DB_USER=admin DB_PASSWORD=secret python db_monitor.py
```

### Using .env file
```bash
# Load .env automatically with python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()" && python db_monitor.py
```

Or modify the script to load .env:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Output Example

```
================================================================================
🔍 SAP Material Database Monitor Started
================================================================================
Database: sap_materials
Table: sap_material_data
Poll Interval: 5 seconds
Started at: 2026-03-12 14:30:00
================================================================================

Press Ctrl+C to stop monitoring

📸 Taking initial snapshot...
✓ Initial snapshot: 1250 rows

⏱️  14:30:15 - No changes detected

================================================================================
🔔 CHANGE DETECTED at 2026-03-12 14:30:25
================================================================================

📊 Row Count: 1250 → 1252
   (+2 rows added)

➕ Added Rows: 2
   • Material: 12345, Plant: GB45, Description: NEW COMPONENT PART A
   • Material: 12346, Plant: US45, Description: NEW COMPONENT PART B

✏️  Modified Rows: 1
   • Material: 1, Plant: GB45
     Changed fields: standard_price, moving_average_price_periodic_unit_price

================================================================================
```

## How It Works

1. **Initial Snapshot**: Takes a snapshot of the entire table including row count and data hash
2. **Polling**: Checks the database at regular intervals (default 5 seconds)
3. **Change Detection**: Compares new snapshot with previous one
4. **Detailed Analysis**: Identifies specific rows that were added, deleted, or modified
5. **Console Output**: Displays changes in a formatted, readable way

## Performance Considerations

- For large tables (>100k rows), consider increasing `POLL_INTERVAL`
- The monitor loads all rows into memory for comparison
- For very large datasets, consider implementing incremental change detection using timestamps or triggers

## Testing the Monitor

Two test scripts are provided to verify the monitor is working:

### Quick Test (Single Insert)
```bash
python quick_test.py
```
Immediately inserts one test row into the database.

### Interactive Test Tool
```bash
python test_insert.py
```
Provides a menu to:
1. Insert a single test row
2. Insert multiple test rows
3. Update an existing row (to test modification detection)
4. Delete a row (to test deletion detection)

### Testing Workflow
1. Start the monitor in one terminal:
   ```bash
   python db_monitor.py
   ```

2. In another terminal, run test operations:
   ```bash
   python quick_test.py
   # or
   python test_insert.py
   ```

3. Watch the monitor terminal for change notifications

## Stopping the Monitor

Press `Ctrl+C` to gracefully stop the monitoring agent.

## Troubleshooting

### Connection Issues
- Verify database credentials in `.env`
- Check that MySQL server is running
- Ensure user has SELECT permissions on `sap_material_data` table

### Performance Issues
- Increase `POLL_INTERVAL` for large tables
- Add indexes to the table if not already present
- Consider using database triggers for change tracking instead

### Memory Issues
- For very large tables, modify the script to use cursor-based pagination
- Implement incremental change detection using `modeldata_timestamp` field

## Advanced Usage

### Custom Monitoring Logic

You can extend the `DatabaseMonitor` class to add custom logic:

```python
class CustomMonitor(DatabaseMonitor):
    def print_changes(self, changes: Dict):
        # Custom change notification logic
        super().print_changes(changes)
        
        # Send email, webhook, etc.
        if changes['has_changes']:
            self.send_notification(changes)
```

### Filtering Specific Changes

Modify the `detect_changes` method to filter for specific materials or plants:

```python
# Only monitor specific plants
if row['plant'] in ['GB45', 'US45']:
    changes['added_rows'].append(row)
```

## License

This monitoring agent is provided as-is for use with the SAP Material Management database.
