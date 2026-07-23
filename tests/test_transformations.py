import pytest
import os
import tempfile
import json
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType
from transformations.spark_etl import process_customers, process_products

def test_process_customers_deduplication(spark):
    # Setup test data with a duplicate
    test_data = [
        {"customer_id": "c1", "customer_city": "City A"},
        {"customer_id": "c1", "customer_city": "City B"}, # Duplicate ID
        {"customer_id": "c2", "customer_city": "City C"}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "raw")
        os.makedirs(input_path)
        output_path = os.path.join(temp_dir, "processed")
        
        # Write mock json
        with open(os.path.join(input_path, "customers.json"), "w") as f:
            for d in test_data:
                f.write(json.dumps(d) + "\n")
                
        # Run transformation
        process_customers(spark, input_path, output_path)
        
        # Verify output
        df_out = spark.read.parquet(os.path.join(output_path, "dim_customer"))
        
        # Should only have 2 unique customers
        assert df_out.count() == 2
        
        # Verify both c1 and c2 exist
        customer_ids = [row.customer_id for row in df_out.select("customer_id").collect()]
        assert "c1" in customer_ids
        assert "c2" in customer_ids

def test_process_products_deduplication(spark):
    test_data = [
        {"product_id": "p1", "product_category_name": "Cat A"},
        {"product_id": "p1", "product_category_name": "Cat B"}
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "raw")
        os.makedirs(input_path)
        output_path = os.path.join(temp_dir, "processed")
        
        with open(os.path.join(input_path, "products.json"), "w") as f:
            for d in test_data:
                f.write(json.dumps(d) + "\n")
                
        process_products(spark, input_path, output_path)
        
        df_out = spark.read.parquet(os.path.join(output_path, "dim_product"))
        assert df_out.count() == 1
