import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

print("Testing database connections...")
print("="*60)

# Test main DB
try:
    main_url = os.getenv('DATABASE_URL')
    if main_url:
        # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
        main_url = main_url.replace('postgres://', 'postgresql://')
        main_engine = create_engine(main_url)
        with main_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("SUCCESS: Main DB: Connected")
    else:
        print("ERROR: Main DB: No URL in .env")
except Exception as e:
    print(f"ERROR: Main DB: Failed - {e}")

# Test security fork
try:
    security_url = os.getenv('SECURITY_FORK_URL')
    if security_url:
        # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
        security_url = security_url.replace('postgres://', 'postgresql://')
        security_engine = create_engine(security_url)
        with security_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("SUCCESS: Security Fork: Connected")
    else:
        print("ERROR: Security Fork: No URL in .env")
except Exception as e:
    print(f"ERROR: Security Fork: Failed - {e}")

# Test quality fork
try:
    quality_url = os.getenv('QUALITY_FORK_URL')
    if quality_url:
        # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
        quality_url = quality_url.replace('postgres://', 'postgresql://')
        quality_engine = create_engine(quality_url)
        with quality_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("SUCCESS: Quality Fork: Connected")
    else:
        print("ERROR: Quality Fork: No URL in .env")
except Exception as e:
    print(f"ERROR: Quality Fork: Failed - {e}")

# Test performance fork
try:
    performance_url = os.getenv('PERFORMANCE_FORK_URL')
    if performance_url:
        # Convert postgres:// to postgresql:// for newer SQLAlchemy versions
        performance_url = performance_url.replace('postgres://', 'postgresql://')
        performance_engine = create_engine(performance_url)
        with performance_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("SUCCESS: Performance Fork: Connected")
    else:
        print("ERROR: Performance Fork: No URL in .env")
except Exception as e:
    print(f"ERROR: Performance Fork: Failed - {e}")

print("="*60)
