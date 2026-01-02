from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------------
# CORS (Production Safe)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# HEALTH CHECK (FIXES 404)
# -----------------------------
@app.get("/")
def root():
    return {"status": "SkillNest API is running"}

# -----------------------------
# SERVERLESS SAFE DB INIT
# -----------------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# -----------------------------
# USER APIs
# -----------------------------
@app.get("/users")
def get_all_user(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/user/{id}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == id).first()
    if db_user:
        return {
            "user_id": db_user.user_id,
            "user_name": db_user.user_name,
            "user_email": db_user.user_email,
            "user_phone": db_user.user_phone,
            "user_gender": db_user.user_gender,
            "user_dateofbirth": db_user.user_dateofbirth,
            "user_created_at": getattr(db_user, 'user_created_at', "January 2024")
        }
    return None

@app.post("/create_user")
def add_user(user: CreateUser, db: Session = Depends(get_db)):
    import datetime
    now = datetime.datetime.now()
    created_at = now.strftime("%B %Y")

    new_user = User(
        user_name=user.user_name,
        user_email=user.user_email,
        user_password=user.user_password,
        user_dateofbirth=user.user_dateofbirth,
        user_phone=user.user_phone,
        user_gender=user.user_gender,
        user_created_at=created_at
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User added successfully"}

@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.user_email == user.user_email,
        User.user_password == user.user_password
    ).first()

    if db_user:
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
                "user_created_at": getattr(db_user, 'user_created_at', "January 2024")
            }
        }
    return {"status": "error", "message": "Invalid email or password"}

@app.put("/user/{user_id}")
def update_user(user_id: int, user_data: UpdateUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return {"status": "error", "message": "User not found"}

    if user_data.user_name is not None:
        db_user.user_name = user_data.user_name
    if user_data.user_email is not None:
        db_user.user_email = user_data.user_email
    if user_data.user_dateofbirth is not None:
        db_user.user_dateofbirth = user_data.user_dateofbirth
    if user_data.user_phone is not None:
        db_user.user_phone = user_data.user_phone
    if user_data.user_gender is not None:
        db_user.user_gender = user_data.user_gender

    db.commit()
    db.refresh(db_user)

    return {
        "status": "success",
        "message": "User updated successfully",
        "user": {
            "user_id": db_user.user_id,
            "user_name": db_user.user_name,
            "user_email": db_user.user_email
        }
    }

@app.post("/delete_user/{user_id}")
def delete_user(user_id: int, request: DeleteUserRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return {"status": "error", "message": "User not found"}

    if db_user.user_password != request.password:
        return {"status": "error", "message": "Incorrect password"}

    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}

# -----------------------------
# COURSE APIs
# -----------------------------
@app.post("/create_course")
def create_course(course: Create_course, db: Session = Depends(get_db)):
    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return "course added successfully"

@app.get("/course")
def get_all_course(db: Session = Depends(get_db)):
    return db.query(Course).all()

# -----------------------------
# QUIZ APIs
# -----------------------------
@app.post("/create_quiz")
def create_quiz(data: QuizResultCreate, db: Session = Depends(get_db)):
    new_quiz = Quiz(**data.dict())
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return {"status": "success", "message": "Quiz result saved successfully"}

# -----------------------------
# COURSE PROGRESS APIs
# -----------------------------
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
    existing = db.query(CourseVideoProgress).filter(
        CourseVideoProgress.user_id == data.user_id,
        CourseVideoProgress.course_id == data.course_id,
        CourseVideoProgress.video_index == data.video_index
    ).first()

    if existing:
        return {"status": "success", "message": "Video already marked complete"}

    db.add(CourseVideoProgress(**data.dict()))
    db.commit()
    return {"status": "success", "message": "Video marked complete"}

# -----------------------------
# QUIZ PROGRESS APIs
# -----------------------------
@app.get("/progress/quiz/{user_id}")
def get_quiz_results(user_id: int, db: Session = Depends(get_db)):
    results = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    result_map = {}

    for r in results:
        result_map.setdefault(
            r.quiz_id, {"attempts": 0, "bestScore": 0, "lastScore": 0}
        )
        result_map[r.quiz_id]["attempts"] += 1
        result_map[r.quiz_id]["lastScore"] = r.score
        result_map[r.quiz_id]["bestScore"] = max(
            result_map[r.quiz_id]["bestScore"], r.score
        )

    return result_map

@app.get("/progress/quiz/partial/{user_id}")
def get_all_partial_progress(user_id: int, db: Session = Depends(get_db)):
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
        QuizPartialProgress.quiz_id == data.quiz_id
    ).first()

    if existing:
        existing.current_index = data.current_index
        existing.score = data.score
    else:
        db.add(QuizPartialProgress(**data.dict()))

    db.commit()
    return {"status": "success", "message": "Partial progress saved"}

@app.delete("/progress/quiz/partial/{user_id}/{quiz_id}")
def delete_partial_progress(user_id: int, quiz_id: str, db: Session = Depends(get_db)):
    partial = db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == user_id,
        QuizPartialProgress.quiz_id == quiz_id
    ).first()
    if partial:
        db.delete(partial)
        db.commit()
    return {"status": "success", "message": "Partial progress cleared"}

# -----------------------------
# DEBUG (KEEP AS IS)
# -----------------------------
@app.get("/debug/schema")
def debug_schema():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = inspector.get_columns('quizz')
    return [{"name": c["name"], "type": str(c["type"])} for c in columns]

@app.get("/debug/reset_quiz")
def reset_quiz_table():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS quizz"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    return {"status": "reset complete"}
