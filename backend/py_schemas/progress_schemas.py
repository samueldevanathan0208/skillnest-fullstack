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

class ProgressUpdate(BaseModel):
    course_id: str
    video_id: int
    last_watched_time: float
    duration: float
    percentage: float

class ProgressResponse(BaseModel):
    last_watched_time: float
    duration: float
    percentage: float
    is_completed: bool
