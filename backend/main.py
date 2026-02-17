from dotenv import load_dotenv
import os
import sys

# Load .env from parent directory or current directory
# Adjust path to find .env in LMS(fullstack)/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")
load_dotenv(env_path)

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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

from auth import hash_password, verify_password, create_access_token, get_current_user

# Import new routers
from api import notes, chat

app = FastAPI(title="SkillNest API")

# Include Routers
app.include_router(notes.router)
app.include_router(chat.router)


# --------------------------------------------------
# CORS
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"}
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "SkillNest API is running"}


# @app.get("/health")
# def health():
#     return {"status": "ok", "service": "SkillNest API"}


# --------------------------------------------------
# DB INIT
# --------------------------------------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ==================================================
# USER APIs
# ==================================================

@app.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()


@app.get("/user/me")
def get_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user


# -----------------------------
# CREATE USER (FIXED)
# -----------------------------
@app.post("/create_user")
def create_user(user: CreateUser, db: Session = Depends(get_db)):

    # ✅ FORCE SAFE STRING (prevents bcrypt 72 byte crash)
    password = str(user.user_password).strip()

    if not password:
        raise HTTPException(status_code=400, detail="Password required")

    hashed_password = hash_password(password)

    new_user = User(
        user_name=user.user_name.strip(),
        user_email=user.user_email.strip(),
        user_password=hashed_password,
        user_dateofbirth=user.user_dateofbirth,
        user_phone=user.user_phone.strip(),
        user_gender=user.user_gender,
        user_created_at=datetime.datetime.now().strftime("%B %Y")
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"status": "success", "message": "User created"}


# -----------------------------
# LOGIN (FIXED)
# -----------------------------
@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    try:
        email = user.user_email.strip().lower()
        print(f"Login attempt for: {email}")
        
        # Try finding the user (case-insensitive)
        db_user = db.query(User).filter(User.user_email.ilike(email)).first()
        
        if not db_user:
            print(f"User not found in DB: {email}")
            raise HTTPException(status_code=401, detail=f"User '{email}' not found")

        password = str(user.user_password).strip()

        if not verify_password(password, db_user.user_password):
            print(f"Invalid password for: {email}")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_access_token(data={"sub": str(db_user.user_id)})
        print(f"Login successful for: {email} (ID: {db_user.user_id})")

        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL LOGIN ERROR:\n{error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Server Crash: {type(e).__name__}: {str(e)}"
        )


@app.put("/user/me")
def update_user(data: UpdateUser, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for k, v in data.dict(exclude_unset=True).items():
        setattr(current_user, k, v)

    db.commit()
    db.refresh(current_user)
    return {"status": "success", "user": current_user}


@app.post("/user/delete")
def delete_user(req: DeleteUserRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(req.password.strip(), current_user.user_password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(current_user)
    db.commit()
    return {"status": "success"}


# ==================================================
# COURSE APIs
# ==================================================

@app.post("/create_course")
def create_course(course: Create_course, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    return {"status": "course created"}


@app.get("/course")
def get_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Course).all()


# ==================================================
# QUIZ APIs
# ==================================================

@app.post("/create_quiz")
def create_quiz(data: QuizResultCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quiz = Quiz(user_id=current_user.user_id, **data.dict())
    db.add(quiz)
    db.commit()
    return {"status": "quiz saved"}


# ==================================================
# PROGRESS APIs
# ==================================================

@app.post("/progress/course/video")
def mark_video(data: VideoProgressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if record already exists for this user, course, and video
    existing = db.query(CourseVideoProgress).filter(
        CourseVideoProgress.user_id == current_user.user_id,
        CourseVideoProgress.course_id == data.course_id,
        CourseVideoProgress.video_index == data.video_index
    ).first()

    if not existing:
        db.add(CourseVideoProgress(user_id=current_user.user_id, **data.dict()))
        db.commit()

    return {"status": "saved"}


@app.post("/progress/quiz/partial")
def save_partial(data: QuizPartialProgressCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == current_user.user_id,
        QuizPartialProgress.quiz_id == data.quiz_id
    ).first()

    if existing:
        existing.current_index = data.current_index
        existing.score = data.score
    else:
        db.add(QuizPartialProgress(user_id=current_user.user_id, **data.dict()))

    db.commit()
    return {"status": "saved"}


@app.get("/progress/course")
def get_course_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(CourseVideoProgress).filter(
        CourseVideoProgress.user_id == current_user.user_id
    ).all()

    result = {}
    for r in records:
        if r.course_id not in result:
            result[r.course_id] = set()
        result[r.course_id].add(r.video_index)

    # Convert sets to lists for JSON serialization
    for course_id in result:
        result[course_id] = list(result[course_id])

    return result


@app.get("/progress/quiz")
def get_quiz_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(Quiz).filter(Quiz.user_id == current_user.user_id).all()

    temp = {}
    for r in records:
        temp.setdefault(r.quiz_id, []).append(r.score)

    result = {}
    for q_id, scores in temp.items():
        result[q_id] = {
            "attempts": len(scores),
            "bestScore": max(scores)
        }

    return result


@app.get("/progress/quiz/partial")
def get_partial_quiz_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(QuizPartialProgress).filter(QuizPartialProgress.user_id == current_user.user_id).all()

    result = {}
    for r in records:
        result[r.quiz_id] = {
            "currentIndex": r.current_index,
            "score": r.score
        }

    return result


@app.delete("/progress/quiz/partial/{quiz_id}")
def delete_partial_quiz_progress(quiz_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == current_user.user_id,
        QuizPartialProgress.quiz_id == quiz_id
    ).delete()

    db.commit()
    return {"status": "deleted"}
