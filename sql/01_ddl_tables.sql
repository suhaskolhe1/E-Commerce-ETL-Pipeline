-- Create Schema
CREATE SCHEMA IF NOT EXISTS star_schema;
SET search_path TO star_schema;

-- Dimensions
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(20),
    customer_city VARCHAR(100),
    customer_state VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT
);

-- Fact Table (Grain: One row per order line item)
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_id VARCHAR(100) PRIMARY KEY,
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_date_id DATE,
    price FLOAT,
    freight_value FLOAT,
    order_status VARCHAR(20)
);
