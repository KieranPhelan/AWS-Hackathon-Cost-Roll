# SAP Material Management Database Schema Documentation

## Overview
This database schema is designed to store SAP material master data in a normalized relational structure. The schema separates concerns into logical tables for better data integrity, query performance, and maintainability.

## Schema Design Principles
- **Normalized Structure**: Data is organized into separate tables to reduce redundancy
- **Plant-Specific Data**: Many attributes are plant-specific, requiring composite keys
- **Referential Integrity**: Foreign key constraints ensure data consistency
- **Indexing Strategy**: Key fields are indexed for query performance

## Table Descriptions

### 1. materials (Core Material Master)
**Purpose**: Stores core material information that is consistent across all plants.

**Key Fields**:
- `material_number` (PK): Unique identifier for the material
- `material_type`: Classification (ROH=Raw Material, HALB=Semi-Finished, FERT=Finished Product, DIEN=Service)
- `material_description`: Human-readable description
- `material_group`: Grouping for reporting and analysis

**Relationships**: Parent table for all plant-specific data

---

### 2. material_plants
**Purpose**: Stores plant-specific material data and status information.

**Key Fields**:
- `material_number`, `plant` (Composite PK)
- `plant_specific_status`: Material status at this plant
- `profit_center`: Financial responsibility center
- `abc_indicator`: ABC classification for inventory management

**Relationships**: Links materials to specific plants; parent for plant-specific details

---

### 3. procurement
**Purpose**: Manages procurement and purchasing information.

**Key Fields**:
- `procurement_type_planning`: External, In-House, or Both
- `purchasing_group`: Responsible purchasing team
- `planned_delivery_time_days`: Lead time for procurement
- `country_of_origin`: Source country

**Use Cases**: Procurement planning, supplier management, lead time analysis

---

### 4. pricing
**Purpose**: Stores all pricing and cost-related information.

**Key Fields**:
- `standard_price`: Current standard cost
- `moving_average_price`: Weighted average cost
- `future_planned_price_*`: Planned future prices with validity dates
- `do_not_cost`: Flag to exclude from costing

**Use Cases**: Cost analysis, price planning, margin calculations

---

### 5. cost_estimates
**Purpose**: Tracks current and historical cost estimates.

**Key Fields**:
- `estimate_type`: CURRENT or PREVIOUS
- `fiscal_year`, `period`: Time period for the estimate
- `lot_size_product_costing`: Lot size used in costing
- `costing_overhead_group`: Overhead allocation group

**Use Cases**: Cost variance analysis, historical cost tracking

---

### 6. inventory
**Purpose**: Manages stock quantities and values.

**Key Fields**:
- `total_valuated_stock`: Physical stock quantity
- `value_of_total_valuated_stock`: Monetary value of stock
- `safety_stock`: Minimum stock level
- `lifo_fifo_relevant`: Inventory valuation method flag

**Use Cases**: Inventory reporting, stock valuation, working capital analysis

---

### 7. mrp_data
**Purpose**: Material Requirements Planning configuration and data.

**Key Fields**:
- `mrp_type`: Planning strategy (MRP, No Planning, etc.)
- `mrp_controller`: Person responsible for planning
- `lot_size_materials_planning`: Lot sizing method
- `minimum/maximum_lot_size`: Planning constraints
- `backflush_indicator`: Automatic goods issue flag

**Use Cases**: Production planning, inventory optimization, demand forecasting

---

### 8. storage_handling
**Purpose**: Storage, batch management, and shelf life information.

**Key Fields**:
- `batch_management_indicator`: Whether batch tracking is active
- `serial_number_profile`: Serial number tracking configuration
- `minimum_remaining_shelf_life`: Quality control parameter
- `storage_conditions`: Required storage environment
- `temperature_conditions`: Temperature requirements

**Use Cases**: Warehouse management, quality control, expiration tracking

---

### 9. foreign_trade
**Purpose**: International trade and customs information.

**Key Fields**:
- `commodity_code`: HS code for customs
- `country_of_origin`: Manufacturing country
- `component_scrap_percent`: Expected waste percentage

**Use Cases**: Import/export documentation, customs compliance, scrap analysis

---

## Views

### v_material_complete
Comprehensive view joining all major tables for easy querying of complete material information.

### v_inventory_by_plant
Aggregated inventory metrics by plant for reporting.

### v_materials_by_type_status
Summary statistics by material type and status.

---

## Common Query Patterns

### Find all materials at a specific plant
```sql
SELECT * FROM v_material_complete WHERE plant = 'GB45';
```

### Get inventory value by material type
```sql
SELECT 
    m.material_type,
    SUM(i.value_of_total_valuated_stock) as total_value
FROM materials m
JOIN inventory i ON m.material_number = i.material_number
GROUP BY m.material_type;
```

### Find materials with low stock
```sql
SELECT 
    m.material_number,
    m.material_description,
    i.stock_quantity_total,
    i.safety_stock
FROM materials m
JOIN inventory i ON m.material_number = i.material_number
WHERE i.stock_quantity_total < i.safety_stock;
```

### Materials by MRP controller
```sql
SELECT 
    mrp_controller,
    COUNT(*) as material_count
FROM mrp_data
WHERE mrp_type = 'MRP'
GROUP BY mrp_controller;
```

---

## Data Migration Notes

When loading data from the CSV:
1. Load `materials` table first (parent table)
2. Load `material_plants` table second (establishes plant relationships)
3. Load remaining tables in any order (all reference material_plants)
4. Handle NULL values appropriately (many fields are optional)
5. Convert boolean text values ("true"/"false") to proper boolean types
6. Parse date fields from DD/MM/YYYY format
7. Handle escaped quotes and special characters in descriptions

---

## Indexing Strategy

Indexes are created on:
- All primary keys (automatic)
- Foreign key columns for join performance
- Frequently filtered columns (material_type, plant, mrp_controller, etc.)
- Date columns used in range queries

---

## Future Enhancements

Potential additions to consider:
- Audit trail tables for tracking changes
- Material BOM (Bill of Materials) structure
- Vendor master data tables
- Purchase order history
- Production order linkage
- Quality inspection results
