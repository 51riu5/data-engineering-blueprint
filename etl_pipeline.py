import pandas as pd
from sqlalchemy import create_engine
import os

def extract_data(file_path):
    print("=== [1/3] EXTRACTION PHASE STARTING ===")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find the file at {file_path}. Make sure it is renamed correctly.")
        
    df = pd.read_csv(file_path)
    print(f"-> Successfully read raw data.")
    print(f"-> Found {df.shape[0]} rows and {df.shape[1]} columns.\n")
    return df


def transform_data(df):
    print("=== [2/3] TRANSFORMATION PHASE STARTING ===")
    
    cleaned_df = df.copy()
    
    # OPERATION A: Clean Column Names
    # Even though your columns look clean, it's best practice to run this anyway
    # to catch trailing spaces or unexpected capital letters.
    print("-> Enforcing snake_case on column names...")
    cleaned_df.columns = (
        cleaned_df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )
    
    # OPERATION B: Financial Logic Check
    # Let's add a data engineering rule: Total Price should equal (unit_price * quantity) + tax.
    # We will round it to 2 decimal places to ensure clean data.
    print("-> Validating and rounding financial columns...")
    cleaned_df['total_price'] = cleaned_df['total_price'].round(2)
    cleaned_df['tax'] = cleaned_df['tax'].round(2)
    
    # OPERATION C: Quality Control (Using 'sale_id' instead of 'invoice_id')
    # We drop any rows that don't have a valid sale ID.
    initial_rows = len(cleaned_df)
    cleaned_df = cleaned_df.dropna(subset=['sale_id'])
    cleaned_df = cleaned_df.drop_duplicates(subset=['sale_id'])
    
    dropped_rows = initial_rows - len(cleaned_df)
    print(f"-> Quality control complete. Dropped {dropped_rows} bad/duplicate rows.\n")
    
    return cleaned_df


def load_data(df, db_user, db_password, db_host, db_port, db_name, table_name):
    print("=== [3/3] LOADING PHASE STARTING ===")
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"-> Connecting to database '{db_name}'...")
    engine = create_engine(connection_string)
    
    print(f"-> Streaming data into table '{table_name}'...")
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    
    print("=== PIPELINE COMPLETION SUCCESSFUL ===\n")


if __name__ == "__main__":
    # Ensure your CSV is named exactly this or change the variable
    FILE_NAME = "sales.csv"
    
    # DATABASE CREDENTIALS (UPDATE THESE)
    USER = "postgres"
    PASSWORD = "admin" # Change to your actual password
    HOST = "localhost"
    PORT = "5432"
    DATABASE = "de_sandbox"
    TARGET_TABLE = "stg_sales_data"
    
    try:
        raw_data = extract_data(FILE_NAME)
        transformed_data = transform_data(raw_data)
        load_data(transformed_data, USER, PASSWORD, HOST, PORT, DATABASE, TARGET_TABLE)
        
        print("Congratulations! Your adapted ETL pipeline is complete.")
        
    except Exception as e:
        print("\n!!! PIPELINE FAILED !!!")
        print(f"Error details: {e}")