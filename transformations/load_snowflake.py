import os
import snowflake.connector

def load_to_snowflake():
    # Fetch credentials from environment
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'OLIST_WH')
    database = os.getenv('SNOWFLAKE_DATABASE', 'OLIST_DB')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'STAR_SCHEMA')
    
    if not all([user, password, account]):
        print("Snowflake credentials not found in environment. Skipping load.")
        return

    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    
    cursor = conn.cursor()
    
    # Read the SQL script
    sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'sql', '03_copy_and_merge.sql')
    
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            
        # Split by semicolon to execute one statement at a time
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                print(f"Executing: {statement.strip()[:50]}...")
                cursor.execute(statement)
                
        print("Snowflake load and merge completed successfully.")
    except Exception as e:
        print(f"Error executing Snowflake script: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_to_snowflake()
