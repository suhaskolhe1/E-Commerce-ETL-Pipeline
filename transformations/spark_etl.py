import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, to_date, row_number, lit
from pyspark.sql.window import Window

# Configuration
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'olist-ecommerce-data-lake-123')
RUN_LOCAL = os.getenv('RUN_LOCAL', 'true').lower() == 'true'
from datetime import datetime

DT_PARTITION = os.getenv('DT_PARTITION', datetime.now().strftime('%Y-%m-%d'))

def create_spark_session():
    builder = SparkSession.builder.appName("OlistETL")
    if not RUN_LOCAL:
        # Config for S3 access (requires AWS credentials in env or instance profile)
        builder = builder \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1")
    return builder.getOrCreate()

def process_customers(spark, input_path, output_path):
    df = spark.read.json(f"{input_path}/customers.json")
    
    # Deduplicate: Keep the latest if there are duplicates (using simple dropDuplicates here as there's no update timestamp)
    df_clean = df.dropDuplicates(["customer_id"])
    
    df_clean.write.mode("overwrite").parquet(f"{output_path}/dim_customer")
    print("Processed customers.")

def process_products(spark, input_path, output_path):
    df = spark.read.json(f"{input_path}/products.json")
    df_clean = df.dropDuplicates(["product_id"])
    df_clean.write.mode("overwrite").parquet(f"{output_path}/dim_product")
    print("Processed products.")

def process_orders(spark, input_path, output_path):
    df_orders = spark.read.json(f"{input_path}/orders.json")
    df_items = spark.read.json(f"{input_path}/order_items.json")
    
    # Clean orders
    df_orders_clean = df_orders.withColumn("order_purchase_timestamp", to_timestamp("order_purchase_timestamp")) \
                               .withColumn("order_date_id", to_date("order_purchase_timestamp")) \
                               .dropDuplicates(["order_id"])
                               
    # Clean items
    df_items_clean = df_items.dropDuplicates(["order_item_id"])
    
    # Join to create fact table grain
    fact_df = df_items_clean.join(df_orders_clean, on="order_id", how="inner")
    
    # Add a pseudo date partition column for writing (just copying order_date_id as string)
    fact_df = fact_df.withColumn("dt", col("order_date_id").cast("string"))
    
    # Write partitioned by date
    fact_df.write.mode("overwrite") \
           .partitionBy("dt") \
           .parquet(f"{output_path}/fact_order_items")
    print("Processed fact_order_items.")

def main():
    spark = create_spark_session()
    
    if RUN_LOCAL:
        input_base = "/tmp"
        output_base = "/tmp/processed"
    else:
        input_base = f"s3a://{S3_BUCKET}/raw/dt={DT_PARTITION}"
        output_base = f"s3a://{S3_BUCKET}/processed"
        
    process_customers(spark, input_base, output_base)
    process_products(spark, input_base, output_base)
    process_orders(spark, input_base, output_base)
    
    spark.stop()

if __name__ == "__main__":
    main()
