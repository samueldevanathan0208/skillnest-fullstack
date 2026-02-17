from pydantic import BaseModel

class NotesSchema(BaseModel):
    user_id: int
    course_id: str
    notes: str
