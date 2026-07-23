SET search_path TO star_schema;

---------------------------------------------------------
-- 1. Create Staging (Temp) Tables
---------------------------------------------------------
CREATE TEMP TABLE stg_dim_customer (LIKE dim_customer);
CREATE TEMP TABLE stg_dim_product (LIKE dim_product);
CREATE TEMP TABLE stg_fact_order_items (LIKE fact_order_items);

---------------------------------------------------------
-- 2. COPY INTO Staging from S3
---------------------------------------------------------
COPY stg_dim_customer
FROM 's3://{{S3_BUCKET_NAME}}/processed/dim_customer/'
IAM_ROLE '{{REDSHIFT_IAM_ROLE}}'
FORMAT AS PARQUET;

COPY stg_dim_product
FROM 's3://{{S3_BUCKET_NAME}}/processed/dim_product/'
IAM_ROLE '{{REDSHIFT_IAM_ROLE}}'
FORMAT AS PARQUET;

COPY stg_fact_order_items
FROM 's3://{{S3_BUCKET_NAME}}/processed/fact_order_items/'
IAM_ROLE '{{REDSHIFT_IAM_ROLE}}'
FORMAT AS PARQUET;

---------------------------------------------------------
-- 3. MERGE into Target Tables
---------------------------------------------------------
-- Merge Customer
MERGE INTO dim_customer USING stg_dim_customer 
ON dim_customer.customer_id = stg_dim_customer.customer_id
WHEN MATCHED THEN
  UPDATE SET 
    customer_city = stg_dim_customer.customer_city,
    customer_state = stg_dim_customer.customer_state
WHEN NOT MATCHED THEN
  INSERT (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
  VALUES (stg_dim_customer.customer_id, stg_dim_customer.customer_unique_id, stg_dim_customer.customer_zip_code_prefix, stg_dim_customer.customer_city, stg_dim_customer.customer_state);

-- Merge Product
MERGE INTO dim_product USING stg_dim_product 
ON dim_product.product_id = stg_dim_product.product_id
WHEN MATCHED THEN
  UPDATE SET 
    product_category_name = stg_dim_product.product_category_name
WHEN NOT MATCHED THEN
  INSERT (product_id, product_category_name, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
  VALUES (stg_dim_product.product_id, stg_dim_product.product_category_name, stg_dim_product.product_weight_g, stg_dim_product.product_length_cm, stg_dim_product.product_height_cm, stg_dim_product.product_width_cm);

-- Merge Fact Order Items
MERGE INTO fact_order_items USING stg_fact_order_items 
ON fact_order_items.order_item_id = stg_fact_order_items.order_item_id
WHEN NOT MATCHED THEN
  INSERT (order_item_id, order_id, customer_id, product_id, seller_id, order_purchase_timestamp, order_date_id, price, freight_value, order_status)
  VALUES (stg_fact_order_items.order_item_id, stg_fact_order_items.order_id, stg_fact_order_items.customer_id, stg_fact_order_items.product_id, stg_fact_order_items.seller_id, stg_fact_order_items.order_purchase_timestamp, stg_fact_order_items.order_date_id, stg_fact_order_items.price, stg_fact_order_items.freight_value, stg_fact_order_items.order_status);
