# SAP Material Management Database Schema Documentation

## Overview
This database schema stores SAP material master data in a single denormalized table containing all columns from the source CSV file. This design prioritizes simplicity and ease of data loading over normalization.

## Schema Design Principles
- **Single Table Design**: All data in one table for straightforward querying
- **Composite Primary Key**: Material number + plant uniquely identifies each row
- **Direct CSV Mapping**: Column names closely match the CSV headers
- **Indexing Strategy**: Key fields are indexed for query performance

## Table Description

## Table Description

### sap_material_data
**Purpose**: Stores all SAP material master data from the CSV export.

**Primary Key**: Composite key of `material_number` + `plant`

**Column Groups**:

#### Identifiers
- `material_number`: Unique material identifier
- `plant`: Plant/facility code
- `material_type`: Material classification (ROH, HALB, FERT, DIEN, ZUNT)

#### Basic Material Info
- `material_description`: Text description of the material
- `material_base_unit_of_measure`: Base unit (EA, KG, etc.)
- `material_group`: Material grouping code
- `material_external_material_group`: External classification
- `material_product_hierarchy`: Product hierarchy code

#### Procurement
- `procurement_type_planning`: External/In-House/Both
- `special_procurement_type`: Special procurement indicator
- `purchasing_group`: Responsible purchasing team
- `planned_delivery_time_in_days`: Lead time
- `country_of_origin_of_the_material`: Source country

#### Pricing & Costing
- `standard_price`: Current standard cost
- `moving_average_price_periodic_unit_price`: Moving average price
- `future_planned_price`, `future_planned_price_2`, `future_planned_price_3`: Planned future prices
- `previous_planned_price`: Historical price
- `price_unit`: Pricing unit quantity
- `do_not_cost`: Costing exclusion flag

#### Inventory
- `total_valuated_stock`: Physical stock quantity
- `value_of_total_valuated_stock`: Stock value
- `stock_quantity_total`: Total stock
- `financial_value_stocks`: Financial stock value
- `safety_stock`: Minimum stock level

#### MRP (Material Requirements Planning)
- `mrp_type`: Planning method
- `mrp_controller`: Responsible planner
- `mrp_group`: Planning group
- `minimum_lot_size`, `maximum_lot_size`, `fixed_lot_size`: Lot size constraints
- `indicator_backflush`: Automatic consumption flag

#### Storage & Handling
- `batch_management_indicator_internal`: Batch tracking enabled
- `serial_number_profile`: Serial number configuration
- `material_storage_conditions`: Storage requirements
- `material_temperature_conditions_indicator`: Temperature requirements
- `material_minimum_remaining_shelf_life`: Shelf life minimum
- `material_total_shelf_life`: Total shelf life

#### Status & Flags
- `material_cross_plant_material_status`: Cross-plant status
- `plant_specific_material_status`: Plant-specific status
- `flag_material_for_deletion_at_plant_level`: Deletion flag (plant)
- `material_flag_material_for_deletion_at_client_level`: Deletion flag (client)

#### Organization
- `profit_center`: Financial responsibility center
- `abc_indicator`: ABC classification
- `valuation_class`: Valuation grouping

#### Audit
- `material_name_of_person_responsible_for_creating_the_object`: Creator
- `material_created_on`: Creation date
- `modeldata_timestamp`: Last update timestamp

---

## Common Query Patterns

### Find all materials at a specific plant
```sql
SELECT * FROM sap_material_data WHERE plant = 'GB45';
```

### Get inventory value by material type
```sql
SELECT 
    material_type,
    SUM(value_of_total_valuated_stock) as total_value,
    SUM(stock_quantity_total) as total_quantity
FROM sap_material_data
GROUP BY material_type;
```

### Find materials with low stock
```sql
SELECT 
    material_number,
    material_description,
    plant,
    stock_quantity_total,
    safety_stock
FROM sap_material_data
WHERE stock_quantity_total < safety_stock
  AND safety_stock > 0;
```

### Materials by MRP controller
```sql
SELECT 
    mrp_controller,
    COUNT(*) as material_count,
    SUM(value_of_total_valuated_stock) as total_inventory_value
FROM sap_material_data
WHERE mrp_type = 'MRP'
GROUP BY mrp_controller;
```

### Price variance analysis
```sql
SELECT 
    material_number,
    material_description,
    plant,
    standard_price,
    moving_average_price_periodic_unit_price,
    (standard_price - moving_average_price_periodic_unit_price) as price_variance
FROM sap_material_data
WHERE standard_price > 0 
  AND moving_average_price_periodic_unit_price > 0
ORDER BY ABS(standard_price - moving_average_price_periodic_unit_price) DESC;
```

### Materials by procurement type
```sql
SELECT 
    procurement_type_planning,
    COUNT(*) as count,
    AVG(planned_delivery_time_in_days) as avg_lead_time
FROM sap_material_data
GROUP BY procurement_type_planning;
```

---

## Data Migration Notes

When loading data from the CSV:
1. Parse the semicolon-delimited CSV file
2. Handle quoted fields that may contain special characters
3. Convert boolean text values ("true"/"false") to proper boolean types
4. Parse date fields from DD/MM/YYYY format to proper DATE type
5. Convert numeric fields with proper decimal precision
6. Handle empty strings as NULL values where appropriate
7. Escape backslashes in plant codes and other fields (e.g., "GB45\")
8. The composite key (material_number, plant) must be unique

### Sample Data Load Script (Python/Pandas)
```python
import pandas as pd

# Read CSV with proper delimiter
df = pd.read_csv('main SAP Data.csv', sep=';', encoding='utf-8')

# Convert boolean columns
bool_columns = ['indicator_bulk_material', 'flag_material_for_deletion_at_plant_level', 
                'batch_management_indicator_internal', 'indicator_backflush']
for col in bool_columns:
    df[col] = df[col].map({'true': True, 'false': False, '': None})

# Convert date columns
date_columns = ['material_created_on', 'date_from_which_future_planned_price_2_is_valid']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')

# Load to database
df.to_sql('sap_material_data', engine, if_exists='append', index=False)
```

---

## Indexing Strategy

Indexes are created on:
- Primary key: (material_number, plant) - automatic
- material_type - for filtering by material classification
- material_group - for grouping and reporting
- plant - for plant-specific queries
- profit_center - for financial reporting
- mrp_controller - for planning workload distribution
- purchasing_group - for procurement analysis
- material_created_on - for temporal queries

Additional indexes can be added based on query patterns.

---

## Advantages of Single Table Design

- Simple data loading from CSV
- No complex joins required for queries
- Easy to understand and maintain
- Direct mapping to source data
- Good for analytical queries that need many columns

## Considerations

- Data redundancy if material info is repeated across plants
- Larger table size compared to normalized design
- Updates to material-level data require updating multiple rows
- Consider partitioning by plant for very large datasets

---

## Future Enhancements

Potential additions to consider:
- Partitioning by plant or material_type for performance
- Materialized views for common aggregations
- Audit trail table for tracking changes
- Archive table for historical/deleted materials
- Additional indexes based on query performance analysis
