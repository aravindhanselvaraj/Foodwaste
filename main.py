import pandas as pd
from sqlalchemy import create_engine

# DB config (your setup)
db_config = {
    "user": "postgres",
    "password": "postgresql",
    "host": "localhost",
    "port": "5432",
    "database": "foodwaste"
}

# Connection string
conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(conn_str)

# Load CSVs (adjust path as per your local path if needed)
providers = pd.read_csv("providers_data.csv")
receivers = pd.read_csv("receivers_data.csv")
food = pd.read_csv("food_listings_data.csv")
claims = pd.read_csv("claims_data.csv")

# Optional: Clean date columns
food['Expiry_Date'] = pd.to_datetime(food['Expiry_Date'], errors='coerce')
claims['Timestamp'] = pd.to_datetime(claims['Timestamp'], errors='coerce')

# Load to DB
providers.to_sql("providers", con=engine, if_exists='replace', index=False)
receivers.to_sql("receivers", con=engine, if_exists='replace', index=False)
food.to_sql("food_listings", con=engine, if_exists='replace', index=False)
claims.to_sql("claims", con=engine, if_exists='replace', index=False)

print("✅ Data loaded into PostgreSQL successfully!")
