from sqlalchemy import Column, Integer, String
from database import Base

class UserNotes(Base):
    __tablename__ = "user_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    course_id = Column(String, nullable=False)
    notes = Column(String, nullable=True)
