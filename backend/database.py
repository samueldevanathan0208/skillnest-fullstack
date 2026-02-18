import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# Load .env for local development
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Handle SSL and protocol prefix for SQLAlchemy 2.0 + Supabase
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL and "sslmode" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{separator}sslmode=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Verify connection health before use
    pool_size=1,        # Minimal pooling for serverless (avoids connection exhaustion)
    max_overflow=0,     # No extra connections beyond pool_size
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
