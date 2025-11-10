import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if database_url:
    # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
    database_url = database_url.replace('postgres://', 'postgresql://')
engine = create_engine(database_url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("SUCCESS: Connected to Tiger Data!")
        print(result.fetchone()[0])
        
        # Create tables
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS code_submissions (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                code_content TEXT,
                uploaded_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS security_findings (
                id SERIAL PRIMARY KEY,
                submission_id INTEGER,
                issue_type TEXT,
                line_number INTEGER,
                severity TEXT,
                description TEXT,
                suggested_fix TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        conn.commit()
        print("SUCCESS: Created tables!")
        
except Exception as e:
    print(f"ERROR: {e}")
