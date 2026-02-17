from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from py_models.problem_models import ProblemProgress
from py_models.signin_models import User
from auth import get_current_user
import datetime

router = APIRouter(prefix="/problem-solving", tags=["Problem Solving"])

# 21 Problems Data
PROBLEMS_DATA = [
    {"id": "1", "title": "Add Two Numbers", "desc": "Write a function to return the sum of two numbers.", "diff": "Easy"},
    {"id": "2", "title": "Check Even or Odd", "desc": "Check if a number is even or odd.", "diff": "Easy"},
    {"id": "3", "title": "Find Maximum", "desc": "Find the maximum of two numbers.", "diff": "Easy"},
    {"id": "4", "title": "Reverse String", "desc": "Reverse the given string.", "diff": "Easy"},
    {"id": "5", "title": "Count Vowels", "desc": "Count the number of vowels in a string.", "diff": "Easy"},
    {"id": "6", "title": "Factorial", "desc": "Find the factorial of a number.", "diff": "Medium"},
    {"id": "7", "title": "Palindrome", "desc": "Check if a string is a palindrome.", "diff": "Easy"},
    {"id": "8", "title": "Sum of List", "desc": "Calculate the sum of all elements in a list/array.", "diff": "Easy"},
    {"id": "9", "title": "Largest Element", "desc": "Find the largest element in a list/array.", "diff": "Easy"},
    {"id": "10", "title": "Count Words", "desc": "Count the number of words in a sentence.", "diff": "Easy"},
    {"id": "11", "title": "String Length", "desc": "Find length of string without using built-in length function.", "diff": "Medium"},
    {"id": "12", "title": "Prime Number", "desc": "Check if a number is prime.", "diff": "Medium"},
    {"id": "13", "title": "Fibonacci", "desc": "Find the Nth Fibonacci number.", "diff": "Medium"},
    {"id": "14", "title": "Count Evens", "desc": "Count even numbers in a list.", "diff": "Easy"},
    {"id": "15", "title": "To Uppercase", "desc": "Convert string to uppercase without parameters.", "diff": "Medium"},
    {"id": "16", "title": "Find Minimum", "desc": "Find the minimum number in a list.", "diff": "Easy"},
    {"id": "17", "title": "Remove Duplicates", "desc": "Remove duplicates from a list.", "diff": "Medium"},
    {"id": "18", "title": "Second Largest", "desc": "Find the second largest number in a list.", "diff": "Medium"},
    {"id": "19", "title": "Reverse List", "desc": "Reverse a list/array.", "diff": "Easy"},
    {"id": "20", "title": "Anagram Check", "desc": "Check if two strings are anagrams.", "diff": "Medium"},
    {"id": "21", "title": "Leap Year", "desc": "Check if a year is a leap year.", "diff": "Easy"},
]

def generate_problems(lang):
    problems = []
    for p in PROBLEMS_DATA:
        pid = f"{lang}{p['id']}"
        starter = ""
        if lang == "python":
            starter = f"def solve():\n    # {p['title']}\n    pass"
        elif lang == "java":
            starter = f"class Solution {{\n    public void solve() {{\n        // {p['title']}\n    }}\n}}"
        elif lang == "javascript":
            starter = f"function solve() {{\n    // {p['title']}\n}}"
            
        problems.append({
            "id": pid,
            "title": p["title"],
            "difficulty": p["diff"],
            "description": p["desc"],
            "starter_code": "{\"" + lang + "\": " + "\"" + starter.replace("\n", "\\n").replace('"', '\\"') + "\"}"
        })
    return problems

PROBLEMS_DB = {
    "python": generate_problems("python"),
    "java": generate_problems("java"),
    "javascript": generate_problems("javascript")
}

class SubmitRequest(BaseModel):
    user_id: int
    problem_id: str
    language: str
    code: str

@router.get("/languages")
def get_languages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    
    # Calculate progress for each language
    def get_solved_count(lang):
        return db.query(ProblemProgress).filter(
            ProblemProgress.user_id == user_id,
            ProblemProgress.language == lang,
            ProblemProgress.status == "Solved"
        ).count()

    return [
        {"id": "python", "name": "Python", "total": 21, "solved": get_solved_count("python")},
        {"id": "java", "name": "Java", "total": 21, "solved": get_solved_count("java")},
        {"id": "javascript", "name": "JavaScript", "total": 21, "solved": get_solved_count("javascript")}
    ]

@router.get("/{lang_id}/problems")
def get_problems(lang_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    problems = PROBLEMS_DB.get(lang_id, [])
    
    # Get user's solved problems
    solved_ids = db.query(ProblemProgress.problem_id).filter(
        ProblemProgress.user_id == current_user.user_id,
        ProblemProgress.language == lang_id,
        ProblemProgress.status == "Solved"
    ).all()
    solved_set = {s[0] for s in solved_ids}

    # Add 'status' to response
    response = []
    for p in problems:
        p_copy = p.copy()
        p_copy["status"] = "Solved" if p["id"] in solved_set else "Unsolved"
        response.append(p_copy)
        
    return response

@router.post("/submit")
def submit_solution(request: SubmitRequest, db: Session = Depends(get_db)):
    # Mock Judgement
    code = request.code.strip()
    if len(code) < 10:
        return {"status": "Failed", "error": "Code too short"}
    
    # Mock Success logic
    status = "Passed" # Assume pass for now to allow user to complete flow
    
    if status == "Passed":
        # Save progress
        existing = db.query(ProblemProgress).filter(
            ProblemProgress.user_id == request.user_id,
            ProblemProgress.problem_id == request.problem_id
        ).first()
        
        if not existing:
            new_progress = ProblemProgress(
                user_id=request.user_id,
                language=request.language,
                problem_id=request.problem_id,
                status="Solved"
            )
            db.add(new_progress)
            db.commit()
            
    return {"status": status}
