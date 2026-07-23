import json
import os
import boto3
from datetime import datetime, timedelta
from faker import Faker
import uuid
import random

fake = Faker()

# Configuration
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'olist-ecommerce-data-lake-123')
UPLOAD_TO_S3 = os.getenv('UPLOAD_TO_S3', 'false').lower() == 'true'
NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDERS = 200

def generate_customers(num):
    customers = []
    for _ in range(num):
        customers.append({
            "customer_id": str(uuid.uuid4()),
            "customer_unique_id": str(uuid.uuid4()),
            "customer_zip_code_prefix": fake.postcode(),
            "customer_city": fake.city(),
            "customer_state": fake.state_abbr()
        })
    return customers

def generate_products(num):
    categories = ['toys', 'electronics', 'furniture', 'sports', 'health_beauty']
    products = []
    for _ in range(num):
        products.append({
            "product_id": str(uuid.uuid4()),
            "product_category_name": random.choice(categories),
            "product_weight_g": round(random.uniform(100.0, 5000.0), 2),
            "product_length_cm": round(random.uniform(10.0, 100.0), 2),
            "product_height_cm": round(random.uniform(10.0, 100.0), 2),
            "product_width_cm": round(random.uniform(10.0, 100.0), 2)
        })
    return products

def generate_orders_and_items(num_orders, customers, products):
    orders = []
    order_items = []
    for _ in range(num_orders):
        order_id = str(uuid.uuid4())
        customer = random.choice(customers)
        order_date = fake.date_time_between(start_date="-30d", end_date="now")
        
        orders.append({
            "order_id": order_id,
            "customer_id": customer['customer_id'],
            "order_status": random.choices(['delivered', 'shipped', 'canceled'], weights=[0.8, 0.1, 0.1])[0],
            "order_purchase_timestamp": order_date.isoformat()
        })
        
        # Generate 1 to 4 items per order
        num_items = random.randint(1, 4)
        for i in range(num_items):
            product = random.choice(products)
            order_items.append({
                "order_id": order_id,
                "order_item_id": f"{order_id}_{i+1}",
                "product_id": product['product_id'],
                "seller_id": str(uuid.uuid4()),
                "price": round(random.uniform(10.0, 200.0), 2),
                "freight_value": round(random.uniform(5.0, 50.0), 2)
            })
            
    return orders, order_items

def save_and_upload(data, filename, s3_client, dt_partition):
    local_path = f"/tmp/{filename}"
    with open(local_path, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
            
    if UPLOAD_TO_S3:
        s3_key = f"raw/dt={dt_partition}/{filename}"
        s3_client.upload_file(local_path, S3_BUCKET, s3_key)
        print(f"Uploaded {filename} to s3://{S3_BUCKET}/{s3_key}")
    else:
        print(f"Saved {filename} locally to {local_path} (S3 upload disabled)")

if __name__ == "__main__":
    print("Generating fake data...")
    customers = generate_customers(NUM_CUSTOMERS)
    products = generate_products(NUM_PRODUCTS)
    orders, order_items = generate_orders_and_items(NUM_ORDERS, customers, products)
    
    dt_partition = datetime.now().strftime('%Y-%m-%d')
    s3_client = boto3.client('s3') if UPLOAD_TO_S3 else None
    
    # Ensure /tmp exists on Windows for local testing, or use a local data dir
    os.makedirs('/tmp', exist_ok=True)
    
    save_and_upload(customers, 'customers.json', s3_client, dt_partition)
    save_and_upload(products, 'products.json', s3_client, dt_partition)
    save_and_upload(orders, 'orders.json', s3_client, dt_partition)
    save_and_upload(order_items, 'order_items.json', s3_client, dt_partition)
    print("Data generation complete.")
