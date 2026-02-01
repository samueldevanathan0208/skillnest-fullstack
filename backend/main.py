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


app = FastAPI(title="SkillNest API")


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


@app.get("/health")
def health():
    return {"status": "ok", "service": "SkillNest API"}


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


@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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

    db_user = db.query(User).filter(User.user_email == user.user_email.strip()).first()

    password = str(user.user_password).strip()

    if not db_user or not verify_password(password, db_user.user_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(db_user.user_id)})

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.user_id
    }


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

    if not user or not verify_password(req.password.strip(), user.user_password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.delete(user)
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
def create_quiz(data: QuizResultCreate, db: Session = Depends(get_db)):
    quiz = Quiz(**data.dict())
    db.add(quiz)
    db.commit()
    return {"status": "quiz saved"}


# ==================================================
# PROGRESS APIs
# ==================================================

@app.post("/progress/course/video")
def mark_video(data: VideoProgressCreate, db: Session = Depends(get_db)):
    db.add(CourseVideoProgress(**data.dict()))
    db.commit()
    return {"status": "saved"}


@app.post("/progress/quiz/partial")
def save_partial(data: QuizPartialProgressCreate, db: Session = Depends(get_db)):
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
    records = db.query(CourseVideoProgress).filter(CourseVideoProgress.user_id == user_id).all()

    result = {}
    for r in records:
        result.setdefault(r.course_id, []).append(r.video_index)

    return result


@app.get("/progress/quiz/{user_id}")
def get_quiz_progress(user_id: int, db: Session = Depends(get_db)):
    records = db.query(Quiz).filter(Quiz.user_id == user_id).all()

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


@app.get("/progress/quiz/partial/{user_id}")
def get_partial_quiz_progress(user_id: int, db: Session = Depends(get_db)):
    records = db.query(QuizPartialProgress).filter(QuizPartialProgress.user_id == user_id).all()

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
