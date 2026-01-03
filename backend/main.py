from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import datetime

from database import engine, get_db, Base

from py_models.signin_models import User
from py_models.course_models import Course
from py_models.quiz_models import Quiz
from py_models.progress_models import CourseVideoProgress, QuizPartialProgress

from py_schemas.signin_schemas import (
    CreateUser,
    LoginRequest,
    UpdateUser,
    DeleteUserRequest
)
from py_schemas.course_schemas import Create_course
from py_schemas.quizz_schemas import CreateQuiz
from py_schemas.progress_schemas import (
    VideoProgressCreate,
    QuizPartialProgressCreate,
    QuizResultCreate
)

# --------------------------------------------------
# APP INIT
# --------------------------------------------------
app = FastAPI(title="SkillNest API")

# --------------------------------------------------
# CORS CONFIGURATION (ROOT PERMISSIVE - NO CREDENTIALS)
# --------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# --------------------------------------------------
# HEALTH CHECK (CRITICAL FOR VERCEL)
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "SkillNest API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
    return {"status": "ok", "service": "SkillNest API"}

# --------------------------------------------------
# SERVERLESS-SAFE DB INIT
# --------------------------------------------------
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected and tables verified")
    except Exception as e:
        print("❌ Database startup failed:", str(e))

# --------------------------------------------------
# USER APIs
# --------------------------------------------------
@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/user/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.user_id,
        "user_name": user.user_name,
        "user_email": user.user_email,
        "user_phone": user.user_phone,
        "user_gender": user.user_gender,
        "user_dateofbirth": user.user_dateofbirth,
        "user_created_at": getattr(user, "user_created_at", "January 2024"),
    }

@app.post("/create_user")
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    created_at = datetime.datetime.now().strftime("%B %Y")

    new_user = User(
        user_name=user.user_name,
        user_email=user.user_email,
        user_password=user.user_password,
        user_dateofbirth=user.user_dateofbirth,
        user_phone=user.user_phone,
        user_gender=user.user_gender,
        user_created_at=created_at,
    )
    return {"status": "success", "message": "User added successfully"}

@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.user_email == user.user_email,
        User.user_password == user.user_password
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "user_id": db_user.user_id,
            "user_name": db_user.user_name,
            "user_email": db_user.user_email,
            "user_phone": db_user.user_phone,
            "user_gender": db_user.user_gender,
            "user_dateofbirth": db_user.user_dateofbirth,
            "user_created_at": getattr(db_user, "user_created_at", "January 2024"),
        },
    }

@app.put("/user/{user_id}")
def update_user(user_id: int, data: UpdateUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"status": "success", "message": "User updated successfully"}

@app.post("/delete_user/{user_id}")
def delete_user(user_id: int, req: DeleteUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_password != req.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    db.delete(user)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}

# --------------------------------------------------
# COURSE APIs
# --------------------------------------------------
@app.post("/create_course")
def create_course(course: Create_course, db: Session = Depends(get_db)):
    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"status": "success", "message": "Course created"}

@app.get("/course")
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# --------------------------------------------------
# QUIZ APIs
# --------------------------------------------------
@app.post("/create_quiz")
def create_quiz(data: QuizResultCreate, db: Session = Depends(get_db)):
    quiz = Quiz(**data.dict())
    db.add(quiz)
    db.commit()
    return {"status": "success", "message": "Quiz saved"}

# --------------------------------------------------
# COURSE PROGRESS
# --------------------------------------------------
@app.get("/progress/course/{user_id}")
def get_course_progress(user_id: int, db: Session = Depends(get_db)):
    progress = db.query(CourseVideoProgress).filter(
        CourseVideoProgress.user_id == user_id
    ).all()

    result = {}
    for p in progress:
        result.setdefault(p.course_id, []).append(p.video_index)
    return result

@app.post("/progress/course/video")
def mark_video_complete(data: VideoProgressCreate, db: Session = Depends(get_db)):
    exists = db.query(CourseVideoProgress).filter(
        CourseVideoProgress.user_id == data.user_id,
        CourseVideoProgress.course_id == data.course_id,
        CourseVideoProgress.video_index == data.video_index,
    ).first()

    if exists:
        return {"status": "success", "message": "Already completed"}

    db.add(CourseVideoProgress(**data.dict()))
    db.commit()
    return {"status": "success", "message": "Video marked complete"}

# --------------------------------------------------
# QUIZ PROGRESS
# --------------------------------------------------
@app.get("/progress/quiz/{user_id}")
def get_quiz_results(user_id: int, db: Session = Depends(get_db)):
    results = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    summary = {}

    for r in results:
        summary.setdefault(r.quiz_id, {"attempts": 0, "bestScore": 0, "lastScore": 0})
        summary[r.quiz_id]["attempts"] += 1
        summary[r.quiz_id]["lastScore"] = r.score
        summary[r.quiz_id]["bestScore"] = max(summary[r.quiz_id]["bestScore"], r.score)

    return summary

@app.get("/progress/quiz/partial/{user_id}")
def get_partial_progress(user_id: int, db: Session = Depends(get_db)):
    partials = db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == user_id
    ).all()
    return {
        p.quiz_id: {"currentIndex": p.current_index, "score": p.score}
        for p in partials
    }

@app.post("/progress/quiz/partial")
def save_partial_progress(data: QuizPartialProgressCreate, db: Session = Depends(get_db)):
    existing = db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == data.user_id,
        QuizPartialProgress.quiz_id == data.quiz_id,
    ).first()

    if existing:
        existing.current_index = data.current_index
        existing.score = data.score
    else:
        db.add(QuizPartialProgress(**data.dict()))

    db.commit()
    return {"status": "success", "message": "Partial progress saved"}

@app.delete("/progress/quiz/partial/{user_id}/{quiz_id}")
def delete_partial(user_id: int, quiz_id: str, db: Session = Depends(get_db)):
    partial = db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == user_id,
        QuizPartialProgress.quiz_id == quiz_id,
    ).first()

    if partial:
        db.delete(partial)
        db.commit()

    return {"status": "success", "message": "Partial progress cleared"}

# --------------------------------------------------
# DEBUG (KEEP)
# --------------------------------------------------
@app.get("/debug/schema")
def debug_schema():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    return inspector.get_table_names()

@app.get("/debug/reset_quiz")
def reset_quiz():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS quizz"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    return {"status": "reset complete"}
