-- SAP Material Management Database Schema
-- Generated from main SAP Data.csv
-- Normalized design with separate tables for different entity types

-- ============================================
-- Core Material Table
-- ============================================
CREATE TABLE materials (
    material_number VARCHAR(50) PRIMARY KEY,
    material_type VARCHAR(10) NOT NULL,
    material_description TEXT,
    base_unit_of_measure VARCHAR(10),
    material_group VARCHAR(50),
    external_material_group VARCHAR(50),
    product_hierarchy VARCHAR(50),
    old_material_number VARCHAR(50),
    document_version VARCHAR(50),
    general_item_category_group VARCHAR(50),
    created_by VARCHAR(100),
    created_on DATE,
    deletion_flag_client_level BOOLEAN DEFAULT FALSE,
    cross_plant_status VARCHAR(10),
    cross_plant_status_valid_from DATE,
    cross_distribution_chain_status VARCHAR(10),
    x_distribution_chain_status_valid_from DATE,
    modeldata_timestamp TIMESTAMP,
    INDEX idx_material_type (material_type),
    INDEX idx_material_group (material_group),
    INDEX idx_created_on (created_on)
);

-- ============================================
-- Plant-Specific Material Data
-- ============================================
CREATE TABLE material_plants (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    plant_specific_status VARCHAR(10),
    plant_status_valid_from DATE,
    deletion_flag_plant_level BOOLEAN DEFAULT FALSE,
    profit_center VARCHAR(20),
    abc_indicator VARCHAR(5),
    valuation_class VARCHAR(10),
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number) REFERENCES materials(material_number),
    INDEX idx_plant (plant),
    INDEX idx_profit_center (profit_center)
);

-- ============================================
-- Procurement Data
-- ============================================
CREATE TABLE procurement (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    procurement_type_planning VARCHAR(50),
    special_procurement_type VARCHAR(20),
    special_procurement_type_costing VARCHAR(20),
    purchasing_group VARCHAR(50),
    vendor_language_key VARCHAR(5),
    planned_delivery_time_days INT,
    country_of_origin VARCHAR(5),
    region_of_origin VARCHAR(10),
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant),
    INDEX idx_purchasing_group (purchasing_group)
);

-- ============================================
-- Pricing and Costing
-- ============================================
CREATE TABLE pricing (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    price_unit DECIMAL(15,2),
    standard_price DECIMAL(15,2),
    moving_average_price DECIMAL(15,2),
    previous_planned_price DECIMAL(15,2),
    standard_price_previous_period DECIMAL(15,2),
    future_planned_price DECIMAL(15,2),
    future_planned_price_2 DECIMAL(15,2),
    future_planned_price_2_valid_from DATE,
    future_planned_price_3 DECIMAL(15,2),
    future_planned_price_3_valid_from DATE,
    do_not_cost BOOLEAN DEFAULT FALSE,
    is_costed_with_quantity_structure BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant)
);

-- ============================================
-- Cost Estimates
-- ============================================
CREATE TABLE cost_estimates (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    estimate_type VARCHAR(20) NOT NULL, -- 'CURRENT' or 'PREVIOUS'
    fiscal_year INT,
    period INT,
    lot_size_product_costing DECIMAL(15,2),
    costing_overhead_group VARCHAR(20),
    origin_group VARCHAR(20),
    material_related_origin VARCHAR(50),
    PRIMARY KEY (material_number, plant, estimate_type),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant),
    INDEX idx_fiscal_year (fiscal_year)
);

-- ============================================
-- Inventory and Stock
-- ============================================
CREATE TABLE inventory (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    total_valuated_stock DECIMAL(15,2) DEFAULT 0,
    value_of_total_valuated_stock DECIMAL(15,2) DEFAULT 0,
    stock_quantity_total DECIMAL(15,2) DEFAULT 0,
    financial_value_stocks DECIMAL(15,2) DEFAULT 0,
    safety_stock DECIMAL(15,2) DEFAULT 0,
    lifo_fifo_relevant VARCHAR(5),
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant)
);

-- ============================================
-- MRP (Material Requirements Planning)
-- ============================================
CREATE TABLE mrp_data (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    mrp_type VARCHAR(20),
    mrp_group VARCHAR(20),
    mrp_controller VARCHAR(50),
    lot_size_materials_planning VARCHAR(10),
    minimum_lot_size DECIMAL(15,2) DEFAULT 0,
    maximum_lot_size DECIMAL(15,2) DEFAULT 0,
    fixed_lot_size DECIMAL(15,2) DEFAULT 0,
    backflush_indicator BOOLEAN DEFAULT FALSE,
    production_supervisor VARCHAR(50),
    checking_group_availability VARCHAR(20),
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant),
    INDEX idx_mrp_controller (mrp_controller)
);

-- ============================================
-- Storage and Handling
-- ============================================
CREATE TABLE storage_handling (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    bulk_material_indicator BOOLEAN DEFAULT FALSE,
    batch_management_indicator BOOLEAN DEFAULT FALSE,
    batch_management_requirement BOOLEAN DEFAULT FALSE,
    serial_number_profile VARCHAR(20),
    storage_conditions VARCHAR(50),
    temperature_conditions VARCHAR(50),
    minimum_remaining_shelf_life INT,
    total_shelf_life INT,
    shelf_life_period_indicator VARCHAR(10),
    maximum_storage_period INT,
    unit_max_storage_period VARCHAR(10),
    physical_inventory_cycle_counting VARCHAR(20),
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant)
);

-- ============================================
-- Foreign Trade Data
-- ============================================
CREATE TABLE foreign_trade (
    material_number VARCHAR(50) NOT NULL,
    plant VARCHAR(10) NOT NULL,
    commodity_code VARCHAR(50),
    country_of_origin VARCHAR(5),
    component_scrap_percent DECIMAL(5,2) DEFAULT 0,
    PRIMARY KEY (material_number, plant),
    FOREIGN KEY (material_number, plant) REFERENCES material_plants(material_number, plant)
);

-- ============================================
-- Views for Common Queries
-- ============================================

-- Complete Material View
CREATE VIEW v_material_complete AS
SELECT 
    m.*,
    mp.plant,
    mp.plant_specific_status,
    mp.profit_center,
    mp.abc_indicator,
    p.standard_price,
    p.moving_average_price,
    i.stock_quantity_total,
    i.value_of_total_valuated_stock,
    proc.procurement_type_planning,
    proc.purchasing_group,
    mrp.mrp_type,
    mrp.mrp_controller
FROM materials m
LEFT JOIN material_plants mp ON m.material_number = mp.material_number
LEFT JOIN pricing p ON mp.material_number = p.material_number AND mp.plant = p.plant
LEFT JOIN inventory i ON mp.material_number = i.material_number AND mp.plant = i.plant
LEFT JOIN procurement proc ON mp.material_number = proc.material_number AND mp.plant = proc.plant
LEFT JOIN mrp_data mrp ON mp.material_number = mrp.material_number AND mp.plant = mrp.plant;

-- Inventory Value Summary by Plant
CREATE VIEW v_inventory_by_plant AS
SELECT 
    plant,
    COUNT(DISTINCT material_number) as material_count,
    SUM(stock_quantity_total) as total_stock_quantity,
    SUM(value_of_total_valuated_stock) as total_stock_value
FROM inventory
GROUP BY plant;

-- Materials by Type and Status
CREATE VIEW v_materials_by_type_status AS
SELECT 
    m.material_type,
    mp.plant_specific_status,
    COUNT(*) as material_count,
    AVG(p.standard_price) as avg_standard_price
FROM materials m
JOIN material_plants mp ON m.material_number = mp.material_number
LEFT JOIN pricing p ON mp.material_number = p.material_number AND mp.plant = p.plant
GROUP BY m.material_type, mp.plant_specific_status;
