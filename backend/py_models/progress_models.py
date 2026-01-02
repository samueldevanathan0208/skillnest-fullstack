from sqlalchemy import Column, Integer, String, ForeignKey
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
