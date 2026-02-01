from pydantic import BaseModel
from typing import List

class VideoProgressCreate(BaseModel):
    course_id: str
    video_index: int

class QuizPartialProgressCreate(BaseModel):
    quiz_id: str
    current_index: int
    score: int

class QuizResultCreate(BaseModel):
    quiz_id: str
    score: int
    attempt_date: str
