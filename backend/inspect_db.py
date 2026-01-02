from sqlalchemy import create_engine, inspect
from database import DATABASE_URL  # Assuming DATABASE_URL is in database.py

# If DATABASE_URL is not directly available, construct it or use the sqlite file
# Usually: sqlite:///./sql_app.db
# Let's try to import or just use the default
try:
    from database import engine
except:
    engine = create_engine("sqlite:///./sql_app.db")

inspector = inspect(engine)
columns = inspector.get_columns('quizz')
print("Columns in 'quizz' table:")
for column in columns:
    print(f"- {column['name']} ({column['type']})")
