USE ROLE SYSADMIN;
USE DATABASE OLIST_DB;
USE SCHEMA STAR_SCHEMA;

---------------------------------------------------------
-- 1. Create Transient Staging Tables
---------------------------------------------------------
CREATE OR REPLACE TRANSIENT TABLE stg_dim_customer CLONE dim_customer;
CREATE OR REPLACE TRANSIENT TABLE stg_dim_product CLONE dim_product;
CREATE OR REPLACE TRANSIENT TABLE stg_fact_order_items CLONE fact_order_items;

---------------------------------------------------------
-- 2. COPY INTO Staging from External Stage
---------------------------------------------------------
COPY INTO stg_dim_customer
FROM @olist_s3_stage/dim_customer/
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

COPY INTO stg_dim_product
FROM @olist_s3_stage/dim_product/
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

COPY INTO stg_fact_order_items
FROM @olist_s3_stage/fact_order_items/
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

---------------------------------------------------------
-- 3. MERGE into Target Tables
---------------------------------------------------------
-- Merge Customer
MERGE INTO dim_customer target
USING stg_dim_customer source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN 
  UPDATE SET 
    target.customer_city = source.customer_city,
    target.customer_state = source.customer_state
WHEN NOT MATCHED THEN 
  INSERT (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
  VALUES (source.customer_id, source.customer_unique_id, source.customer_zip_code_prefix, source.customer_city, source.customer_state);

-- Merge Product
MERGE INTO dim_product target
USING stg_dim_product source
ON target.product_id = source.product_id
WHEN MATCHED THEN 
  UPDATE SET 
    target.product_category_name = source.product_category_name
WHEN NOT MATCHED THEN 
  INSERT (product_id, product_category_name, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
  VALUES (source.product_id, source.product_category_name, source.product_weight_g, source.product_length_cm, source.product_height_cm, source.product_width_cm);

-- Merge Fact Order Items (simple insert if not exists)
MERGE INTO fact_order_items target
USING stg_fact_order_items source
ON target.order_item_id = source.order_item_id
WHEN NOT MATCHED THEN 
  INSERT (order_item_id, order_id, customer_id, product_id, seller_id, order_purchase_timestamp, order_date_id, price, freight_value, order_status)
  VALUES (source.order_item_id, source.order_id, source.customer_id, source.product_id, source.seller_id, source.order_purchase_timestamp, source.order_date_id, source.price, source.freight_value, source.order_status);
