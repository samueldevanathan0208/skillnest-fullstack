from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from py_models.note_models import UserNotes
from py_schemas.note_schemas import NotesSchema

router = APIRouter()

@router.post("/notes/save")
def save_notes(data: NotesSchema, db: Session = Depends(get_db)):
    # Check if notes exist for user + course
    existing_note = db.query(UserNotes).filter(
        UserNotes.user_id == data.user_id,
        UserNotes.course_id == data.course_id
    ).first()

    if existing_note:
        existing_note.notes = data.notes
        db.commit()
        return {"status": "updated", "message": "Notes updated successfully"}
    else:
        new_note = UserNotes(
            user_id=data.user_id,
            course_id=data.course_id,
            notes=data.notes
        )
        db.add(new_note)
        db.commit()
        return {"status": "saved", "message": "Notes saved successfully"}

@router.get("/notes/{user_id}/{course_id}")
def get_notes(user_id: int, course_id: str, db: Session = Depends(get_db)):
    note = db.query(UserNotes).filter(
        UserNotes.user_id == user_id,
        UserNotes.course_id == course_id
    ).first()

    if note:
        return {"notes": note.notes}
    else:
        return {"notes": ""}
