from pydantic import BaseModel
from typing import List

class VideoProgressCreate(BaseModel):
    user_id: int
    course_id: str
    video_index: int

class QuizPartialProgressCreate(BaseModel):
    user_id: int
    quiz_id: str
    current_index: int
    score: int

class QuizResultCreate(BaseModel):
    user_id: int
    quiz_id: str
    score: int
    attempt_date: str
