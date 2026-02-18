import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# Load .env for LOCAL development only (Ve# Load .env for LOCAL development only (Vercel ignores this)
# Try multiple paths to find .env

# 1. Check parent directory (Standard structure)
env_path = Path(__file__).parent.parent / '.env' 

# 2. Check direct path if running from root
if not env_path.exists():
    env_path = Path(os.getcwd()) / '.env'

# 3. Check hardcoded path as fallback
if not env_path.exists():
    env_path = Path("C:/Users/SamuelDevanathan/Desktop/LMS(fullstack)/.env")

if env_path.exists():
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path)
else:
    print("WARNING: .env file not found!")
    load_dotenv() # Final fallback

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=1,        # CRITICAL for serverless
    max_overflow=0,     # CRITICAL for serverless
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
