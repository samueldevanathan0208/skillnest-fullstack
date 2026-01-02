from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:AcademyRootPassword@localhost:5432/skillnest"
engine = create_engine(DB_URL)

with engine.connect() as conn:
    print("Adding user_created_at column...")
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS user_created_at VARCHAR DEFAULT 'January 2024'"))
    conn.commit()
    print("Success!")
