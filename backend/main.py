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

app = FastAPI(title="SkillNest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# HTTP EXCEPTION HANDLER (ENSURES CORS ON ERRORS)
# --------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure HTTPException responses include CORS headers"""
    print(f"🔴 HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
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
    db.refresh(user)
    return {"status": "success", "user": user}

@app.post("/delete_user/{user_id}")
def delete_user(user_id: int, req: DeleteUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.user_password != req.password:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(user)
    db.commit()
    return {"status": "success"}

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
    # Check if exists, update or create
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
    return {"status": "saved"}

@app.get("/progress/course/{user_id}")
def get_course_progress(user_id: int, db: Session = Depends(get_db)):
    # Fetch all video progress for user
    records = db.query(CourseVideoProgress).filter(CourseVideoProgress.user_id == user_id).all()
    
    # Aggregate by course_id -> [video_index, ...]
    result = {}
    for r in records:
        if r.course_id not in result:
            result[r.course_id] = []
        if r.video_index not in result[r.course_id]:
            result[r.course_id].append(r.video_index)
            
    return result

@app.get("/progress/quiz/{user_id}")
def get_quiz_progress(user_id: int, db: Session = Depends(get_db)):
    # Fetch all quiz attempts
    records = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    
    # Aggregate: { "python": { "attempts": 2, "bestScore": 90 } }
    temp = {}
    for r in records:
        if r.quiz_id not in temp:
            temp[r.quiz_id] = []
        temp[r.quiz_id].append(r.score)
        
    result = {}
    for q_id, scores in temp.items():
        result[q_id] = {
            "attempts": len(scores),
            "bestScore": max(scores) if scores else 0
        }
    return result

@app.get("/progress/quiz/partial/{user_id}")
def get_partial_quiz_progress(user_id: int, db: Session = Depends(get_db)):
    records = db.query(QuizPartialProgress).filter(QuizPartialProgress.user_id == user_id).all()
    
    # Format: { "python": { "currentIndex": 5, "score": 4 } }
    result = {}
    for r in records:
        result[r.quiz_id] = {
            "currentIndex": r.current_index,
            "score": r.score
        }
    return result

@app.delete("/progress/quiz/partial/{user_id}/{quiz_id}")
def delete_partial_quiz_progress(user_id: int, quiz_id: str, db: Session = Depends(get_db)):
    db.query(QuizPartialProgress).filter(
        QuizPartialProgress.user_id == user_id,
        QuizPartialProgress.quiz_id == quiz_id
    ).delete()
    db.commit()
    return {"status": "deleted"}

# --------------------------------------------------
# DEBUG
# --------------------------------------------------
@app.get("/debug/schema")
def debug_schema():
    from sqlalchemy import inspect
    return inspect(engine).get_table_names()
