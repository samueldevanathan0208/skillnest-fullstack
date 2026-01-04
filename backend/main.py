from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
# CORS (SERVERLESS SAFE)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# GLOBAL ERROR HANDLER
# --------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )

# --------------------------------------------------
# HEALTH CHECK (CRITICAL FOR VERCEL)
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "SkillNest API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "SkillNest API"}

# --------------------------------------------------
# SERVERLESS-SAFE DB INIT
# --------------------------------------------------
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected")
    except Exception as e:
        print("❌ Database init failed:", e)

# --------------------------------------------------
# USER APIs
# --------------------------------------------------
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/create_user")
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    new_user = User(
        user_name=user.user_name,
        user_email=user.user_email,
        user_password=user.user_password,
        user_dateofbirth=user.user_dateofbirth,
        user_phone=user.user_phone,
        user_gender=user.user_gender,
        user_created_at=datetime.datetime.now().strftime("%B %Y")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "User created"}

@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.user_email == user.user_email,
        User.user_password == user.user_password
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"status": "success", "user": db_user}

@app.put("/user/{user_id}")
def update_user(user_id: int, data: UpdateUser, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(user, k, v)

    db.commit()
    return {"status": "success"}

@app.post("/delete_user/{user_id}")
def delete_user(user_id: int, req: DeleteUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.user_password != req.password:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(user)
    db.commit()
    return {"status": "deleted"}

# --------------------------------------------------
# COURSE APIs
# --------------------------------------------------
@app.post("/create_course")
def create_course(course: Create_course, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    return {"status": "course created"}

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
    return {"status": "quiz saved"}

# --------------------------------------------------
# PROGRESS APIs
# --------------------------------------------------
@app.post("/progress/course/video")
def mark_video(data: VideoProgressCreate, db: Session = Depends(get_db)):
    db.add(CourseVideoProgress(**data.dict()))
    db.commit()
    return {"status": "saved"}

@app.post("/progress/quiz/partial")
def save_partial(data: QuizPartialProgressCreate, db: Session = Depends(get_db)):
    db.add(QuizPartialProgress(**data.dict()))
    db.commit()
    return {"status": "saved"}

# --------------------------------------------------
# DEBUG
# --------------------------------------------------
@app.get("/debug/schema")
def debug_schema():
    from sqlalchemy import inspect
    return inspect(engine).get_table_names()
