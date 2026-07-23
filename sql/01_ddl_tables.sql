-- Use system admin role
USE ROLE SYSADMIN;

-- Create a dedicated compute warehouse
CREATE WAREHOUSE IF NOT EXISTS OLIST_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Create Database and Schema
CREATE DATABASE IF NOT EXISTS OLIST_DB;
CREATE SCHEMA IF NOT EXISTS OLIST_DB.STAR_SCHEMA;

USE DATABASE OLIST_DB;
USE SCHEMA STAR_SCHEMA;

-- Dimensions
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
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
