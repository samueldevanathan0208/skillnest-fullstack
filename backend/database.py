import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

# Load .env locally (ignored on Vercel, but safe)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --------------------------------------------------
# VALIDATE DATABASE_URL
# --------------------------------------------------

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL environment variable not set")

# Remove accidental whitespace/newline
DATABASE_URL = DATABASE_URL.strip()

# Mask password for safe logging
masked_url = re.sub(r":([^@]+)@", ":****@", DATABASE_URL)

print(f"[DB] Connecting using: {masked_url}")

# --------------------------------------------------
# CREATE ENGINE (SUPABASE + VERCEL SAFE CONFIG)
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,

    # CRITICAL: Disable SQLAlchemy pooling
    poolclass=NullPool,

    # Required for Supabase SSL
    connect_args={
        "sslmode": "require",
        "application_name": "skillnest-vercel"
    },

    # Recommended settings
    echo=False,
    future=True,
)

# --------------------------------------------------
# SESSION FACTORY
# --------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# BASE MODEL CLASS
# --------------------------------------------------

Base = declarative_base()

# --------------------------------------------------
# DEPENDENCY FOR FASTAPI
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# OPTIONAL HEALTH TEST FUNCTION
# --------------------------------------------------

def test_connection():
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
