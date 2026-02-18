import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to sys.path to import local modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from database import engine, Base
    # Import all models to ensure they are registered with Base.metadata
    import py_models.signin_models
    import py_models.course_models
    import py_models.quiz_models
    import py_models.problem_models
    import py_models.note_models
    
    print("Connecting to database...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Success! All database tables have been created/verified.")
    
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)
