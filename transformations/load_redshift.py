import os
import redshift_connector
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def load_to_redshift():
    # Fetch credentials from environment
    host = os.getenv('REDSHIFT_HOST')
    port = int(os.getenv('REDSHIFT_PORT', '5439'))
    database = os.getenv('REDSHIFT_DATABASE')
    user = os.getenv('REDSHIFT_USER')
    password = os.getenv('REDSHIFT_PASSWORD')
    iam_role = os.getenv('REDSHIFT_IAM_ROLE')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    if not all([host, database, user, password, iam_role, s3_bucket]):
        print("Redshift credentials or configuration missing. Skipping load.")
        return

    print(f"Connecting to Redshift cluster at {host}...")
    try:
        conn = redshift_connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        
        cursor = conn.cursor()
        
        # Execute scripts in order
        scripts = ['01_ddl_tables.sql', '02_copy_and_merge.sql']
        
        for script_name in scripts:
            sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'sql', script_name)
            
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()
                
            # Replace placeholders
            sql_script = sql_script.replace('{{REDSHIFT_IAM_ROLE}}', iam_role)
            sql_script = sql_script.replace('{{S3_BUCKET_NAME}}', s3_bucket)
            
            # Split by semicolon to execute one statement at a time
            statements = sql_script.split(';')
            
            for statement in statements:
                if statement.strip():
                    print(f"Executing: {statement.strip()[:50]}...")
                    cursor.execute(statement)
                    
        conn.commit()
        print("Redshift load and merge completed successfully.")
    except Exception as e:
        print(f"Error executing Redshift script: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    load_to_redshift()
