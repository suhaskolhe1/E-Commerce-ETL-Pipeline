-- Run this as ACCOUNTADMIN or a role with integration creation privileges
USE ROLE ACCOUNTADMIN;

-- Create Storage Integration (Make sure to replace the ARN with your actual AWS Role ARN)
CREATE STORAGE INTEGRATION IF NOT EXISTS s3_olist_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/snowflake_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://olist-ecommerce-data-lake-123/processed/');

-- Grant usage to SYSADMIN so they can use it to create stages
GRANT USAGE ON INTEGRATION s3_olist_int TO ROLE SYSADMIN;

USE ROLE SYSADMIN;
USE DATABASE OLIST_DB;
USE SCHEMA STAR_SCHEMA;

-- Define Parquet file format
CREATE OR REPLACE FILE FORMAT parquet_format
  TYPE = PARQUET
  COMPRESSION = SNAPPY;

-- Create External Stage pointing to the processed S3 folder
CREATE OR REPLACE STAGE olist_s3_stage
  URL = 's3://olist-ecommerce-data-lake-123/processed/'
  STORAGE_INTEGRATION = s3_olist_int
  FILE_FORMAT = parquet_format;
