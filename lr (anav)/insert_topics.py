from supabase import create_client, Client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

df = pd.read_csv("topics.csv")  
assert "name" in df.columns and "difficulty" in df.columns, "CSV must contain 'name' and 'difficulty' columns"

rows = [
    {"id": i, "name": row["name"], "difficulty": int(row["difficulty"])}
    for i, row in df.iterrows()
]

response = supabase.table("topic_info").insert(rows).execute()
print(response)
