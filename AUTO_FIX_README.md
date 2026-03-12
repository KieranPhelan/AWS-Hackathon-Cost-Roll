# Auto-Fix for Blocked Materials

## Overview
The database monitor now includes an automatic fix feature for blocked materials. When a material with a blocked status code is detected, the monitor can automatically clear the problematic date field to resolve the cost-roll error.

## How It Works

### Detection
The monitor checks the `material_cross_plant_material_status` field for these blocked status codes:
- **07**: Blocked-Shell/Pre-release
- **08**: Matl under Construction
- **AB**: All Blocks
- **BE**: Block all except service
- **CC**: Blocked- Costing Cleanse
- **CP**: Blocked in Closed Plant
- **DG**: Blocked for Cleanse - GDG
- **MC**: Blocked- Material Cleanse
- **ZW**: Workflow Block

### Auto-Fix Action
When a blocked material is detected, the monitor automatically:
1. Identifies the material_number and plant
2. Executes an UPDATE query to:
   - Set `material_cross_plant_material_status` to NULL (removes the blocked status code)
   - Set `material_date_from_which_the_cross_plant_material_status_is_valid` to NULL (removes the date)
3. Reports the number of materials fixed with detailed logs for each fix

### Configuration

Enable or disable auto-fix in your `.env` file:

```bash
# Enable auto-fix (default)
AUTO_FIX_BLOCKED=true

# Disable auto-fix (detection only)
AUTO_FIX_BLOCKED=false
```

## Example Output

### With Auto-Fix Enabled
```
================================================================================
⚠️  COST-ROLL ERRORS DETECTED: 3 materials blocked
================================================================================

❌ Material: BLOCK1234 | Plant: GB45
   Status Code: AB
   Error: All Blocks
   Description: TEST BLOCKED MATERIAL - All Blocks
   Type: ROH | Group: TEST_GROUP

❌ Material: BLOCK5678 | Plant: US45
   Status Code: CC
   Error: Blocked- Costing Cleanse
   Description: TEST BLOCKED MATERIAL - Costing Cleanse
   Type: HALB | Group: TEST_GROUP

================================================================================

🔧 Attempting to fix blocked materials...
   🔧 Fixed Material BLOCK1234 | Plant GB45
      ↳ Cleared status code: AB (All Blocks)
      ↳ Cleared date field: material_date_from_which_the_cross_plant_material_status_is_valid
   🔧 Fixed Material BLOCK5678 | Plant US45
      ↳ Cleared status code: CC (Blocked- Costing Cleanse)
      ↳ Cleared date field: material_date_from_which_the_cross_plant_material_status_is_valid
   🔧 Fixed Material BLOCK9012 | Plant CA35
      ↳ Cleared status code: ZW (Workflow Block)
      ↳ Cleared date field: material_date_from_which_the_cross_plant_material_status_is_valid
✅ Fixed 3 blocked material(s)
   Cleared status codes and date fields

================================================================================
```

### With Auto-Fix Disabled
```
================================================================================
⚠️  COST-ROLL ERRORS DETECTED: 3 materials blocked
================================================================================

❌ Material: BLOCK1234 | Plant: GB45
   Status Code: AB
   Error: All Blocks
   Description: TEST BLOCKED MATERIAL - All Blocks
   Type: ROH | Group: TEST_GROUP

================================================================================
```

## Testing the Auto-Fix

1. Start the monitor with auto-fix enabled:
```bash
# Make sure AUTO_FIX_BLOCKED=true in .env
python db_monitor.py
```

2. In another terminal, insert a blocked material:
```bash
python test_blocked_material.py
```

3. Watch the monitor automatically detect and fix the blocked material

## Manual Fix

If you prefer to fix blocked materials manually, you can:

1. Set `AUTO_FIX_BLOCKED=false` in `.env`
2. Run the monitor to detect blocked materials
3. Manually execute the fix query:

```sql
UPDATE sap_material_data 
SET material_cross_plant_material_status = NULL,
    material_date_from_which_the_cross_plant_material_status_is_valid = NULL
WHERE material_cross_plant_material_status IN ('07', '08', 'AB', 'BE', 'CC', 'CP', 'DG', 'MC', 'ZW');
```

## Safety Considerations

- The auto-fix clears both the status code and the date field
- Changes are committed immediately to the database
- The monitor logs each fix operation with detailed information
- You can disable auto-fix at any time by setting `AUTO_FIX_BLOCKED=false`
- Each material fix is logged individually showing what was cleared

## Troubleshooting

### Auto-fix not working
- Check that `AUTO_FIX_BLOCKED=true` in your `.env` file
- Verify the monitor has write permissions to the database
- Check the console output for error messages

### Too many materials being fixed
- Review the blocked status codes list
- Consider disabling auto-fix and reviewing materials manually first
- Check if the status codes are being set correctly in your data source
