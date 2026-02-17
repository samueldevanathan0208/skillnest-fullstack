from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ProblemProgress(Base):
    __tablename__ = "problem_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    language = Column(String) # python, java, javascript
    problem_id = Column(String) 
    status = Column(String) # Solved
    solved_at = Column(DateTime, default=datetime.now)

    user = relationship("User")
