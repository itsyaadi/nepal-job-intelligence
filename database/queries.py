import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    try:
        import streamlit as st
        creds = st.secrets
        db_url = (
            f"postgresql://{creds['DB_USER']}:{creds['DB_PASSWORD']}"
            f"@{creds['DB_HOST']}:{creds['DB_PORT']}/{creds['DB_NAME']}"
        )
    except Exception:
        db_url = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
    return create_engine(db_url)

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✅ Connected to DB:", result.fetchone()[0])
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    test_connection()