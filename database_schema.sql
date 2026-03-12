-- SAP Material Management Database Schema
-- Generated from main SAP Data.csv
-- Single table design with all columns from CSV

CREATE TABLE sap_material_data (
    -- Primary identifiers
    material_number VARCHAR(50),
    plant VARCHAR(10),
    
    -- Material basic info
    material_type VARCHAR(10),
    modeldata_timestamp TIMESTAMP,
    material_description TEXT,
    material_base_unit_of_measure VARCHAR(10),
    material_group VARCHAR(50),
    material_external_material_group VARCHAR(50),
    material_product_hierarchy VARCHAR(50),
    material_old_material_number VARCHAR(50),
    material_document_version VARCHAR(50),
    material_general_item_category_group VARCHAR(50),
    
    -- Procurement
    procurement_type_planning VARCHAR(50),
    special_procurement_type VARCHAR(20),
    special_procurement_type_for_costing VARCHAR(20),
    vendor_language_key VARCHAR(5),
    purchasing_group VARCHAR(50),
    planned_delivery_time_in_days INT,
    country_of_origin_of_the_material VARCHAR(5),
    region_of_origin_of_material VARCHAR(10),
    
    -- Pricing
    future_planned_price_2 DECIMAL(15,2),
    date_from_which_future_planned_price_2_is_valid DATE,
    future_planned_price_3 DECIMAL(15,2),
    date_from_which_future_planned_price_3_is_valid DATE,
    price_unit DECIMAL(15,2),
    do_not_cost VARCHAR(10),
    moving_average_price_periodic_unit_price DECIMAL(15,2),
    standard_price DECIMAL(15,2),
    standard_price_in_the_previous_period DECIMAL(15,2),
    previous_planned_price DECIMAL(15,2),
    future_planned_price DECIMAL(15,2),
    
    -- Status fields
    material_cross_plant_material_status VARCHAR(10),
    plant_specific_material_status VARCHAR(10),
    material_cross_distribution_chain_material_status VARCHAR(10),
    material_date_from_which_the_x_distr_chain_material_status_is_valid DATE,
    material_date_from_which_the_cross_plant_material_status_is_valid DATE,
    date_from_which_the_plant_specific_material_status_is_valid DATE,
    
    -- Indicators and flags
    indicator_bulk_material BOOLEAN,
    flag_material_for_deletion_at_plant_level BOOLEAN,
    material_flag_material_for_deletion_at_client_level BOOLEAN,
    batch_management_indicator_internal BOOLEAN,
    material_batch_management_requirement_indicator BOOLEAN,
    indicator_backflush BOOLEAN,
    material_is_costed_with_quantity_structure BOOLEAN,
    lifo_fifo_relevant VARCHAR(5),
    
    -- Cost estimates
    lot_size_for_product_costing DECIMAL(15,2),
    period_of_current_standard_cost_estimate INT,
    fiscal_year_of_current_standard_cost_estimate INT,
    period_of_previous_standard_cost_estimate INT,
    fiscal_year_of_previous_standard_cost_estimate INT,
    costing_overhead_group VARCHAR(20),
    origin_group_as_subdivision_of_cost_element VARCHAR(20),
    material_related_origin VARCHAR(50),
    
    -- Inventory
    total_valuated_stock DECIMAL(15,2),
    value_of_total_valuated_stock DECIMAL(15,2),
    stock_quantity_total DECIMAL(15,2),
    financial_value_stocks DECIMAL(15,2),
    safety_stock DECIMAL(15,2),
    
    -- Organization
    profit_center VARCHAR(20),
    abc_indicator VARCHAR(5),
    valuation_class VARCHAR(10),
    
    -- MRP (Material Requirements Planning)
    mrp_type VARCHAR(20),
    mrp_group VARCHAR(20),
    mrp_controller VARCHAR(50),
    lot_size_materials_planning VARCHAR(10),
    minimum_lot_size DECIMAL(15,2),
    maximum_lot_size DECIMAL(15,2),
    fixed_lot_size DECIMAL(15,2),
    production_supervisor VARCHAR(50),
    checking_group_for_availability_check VARCHAR(20),
    
    -- Storage and handling
    material_storage_conditions VARCHAR(50),
    material_temperature_conditions_indicator VARCHAR(50),
    material_minimum_remaining_shelf_life INT,
    material_total_shelf_life INT,
    material_period_indicator_for_shelf_life_expiration_date VARCHAR(10),
    maximum_storage_period INT,
    unit_for_maximum_storage_period VARCHAR(10),
    physical_inventory_indicator_for_cycle_counting VARCHAR(20),
    serial_number_profile VARCHAR(20),
    
    -- Foreign trade
    commodity_code_import_code_number_for_foreign_trade VARCHAR(50),
    component_scrap_in_percent DECIMAL(5,2),
    material_country_of_origin_of_the_material VARCHAR(5),
    
    -- Audit fields
    material_name_of_person_responsible_for_creating_the_object VARCHAR(100),
    material_created_on DATE,
    
    -- Composite primary key
    PRIMARY KEY (material_number, plant),
    
    -- Indexes for common queries
    INDEX idx_material_type (material_type),
    INDEX idx_material_group (material_group),
    INDEX idx_plant (plant),
    INDEX idx_profit_center (profit_center),
    INDEX idx_mrp_controller (mrp_controller),
    INDEX idx_purchasing_group (purchasing_group),
    INDEX idx_created_on (material_created_on)
);
