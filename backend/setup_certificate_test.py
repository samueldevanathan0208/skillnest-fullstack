from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.py_models.signin_models import User
from backend.py_models.progress_models import CourseVideoProgress
from backend.py_models.quiz_models import Quiz
from datetime import datetime

# Adjust path if necessary or run from project root
# Using SQLite relative path assuming running from 'c:\Users\SamuelDevanathan\Desktop\project - Copy'
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/lms.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def setup_data():
    email = "cert_test_0@test.com"
    user = db.query(User).filter(User.user_email == email).first()
    
    if not user:
        print(f"User {email} not found!")
        return

    print(f"Found user ID: {user.user_id}")

    # 1. Clear existing progress for HTML to ensure clean slate (optional, but good practice)
    db.query(CourseVideoProgress).filter(CourseVideoProgress.user_id == user.user_id, CourseVideoProgress.course_id == 'html').delete()
    db.query(Quiz).filter(Quiz.user_id == user.user_id, Quiz.quiz_id == 'html').delete()
    db.commit()

    # 2. Add Video Progress (10 videos)
    for i in range(10):
        prog = CourseVideoProgress(
            user_id=user.user_id,
            course_id='html',
            video_index=i
        )
        db.add(prog)
    
    # 3. Add Quiz Result
    quiz = Quiz(
        user_id=user.user_id,
        quiz_id='html',
        score=95,
        attempt_date=datetime.now()
    )
    db.add(quiz)

    db.commit()
    print("Data seeded successfully!")

if __name__ == "__main__":
    setup_data()
