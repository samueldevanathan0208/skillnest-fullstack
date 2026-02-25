from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class CourseVideoProgress(Base):
    __tablename__ = "course_video_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    course_id = Column(String)  # 'html', 'css', 'fastapi', etc.
    video_index = Column(Integer)

class QuizPartialProgress(Base):
    __tablename__ = "quiz_partial_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    quiz_id = Column(String)    # 'html', 'css', 'fastapi', etc.
    current_index = Column(Integer)
    score = Column(Integer)

class VideoProgress(Base):
    __tablename__ = "video_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    course_id = Column(String)
    video_id = Column(Integer)  # index in playlist
    last_watched_time = Column(Float, default=0.0)
    duration = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
