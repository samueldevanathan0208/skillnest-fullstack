import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variables from .env if it exists
load_dotenv()

# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Production safety: Do not fallback to localhost if running on Vercel
if not DATABASE_URL:
    if os.getenv("VERCEL"):
        raise ValueError("DATABASE_URL environment variable is missing in Vercel settings.")
    # Local development fallback
    DATABASE_URL = "postgresql://postgres:AcademyRootPassword@localhost:5432/skillnest"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
