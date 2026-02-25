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

import multiprocessing
import queue

# --------------------------------------------------
# 21 Problems Data
# --------------------------------------------------
PROBLEMS_DATA = [
    {"id": "1", "title": "Add Two Numbers", "desc": "Write a function `solve(a, b)` to return the sum of two numbers.", "diff": "Easy", "args": "a, b", "j_args": "int a, int b", "j_ret": "int", "fname": "solve", "input": "a=5, b=3", "output": "8"},
    {"id": "2", "title": "Check Even or Odd", "desc": "Check if a number `solve(n)` is even or odd.", "diff": "Easy", "args": "n", "j_args": "int n", "j_ret": "boolean", "fname": "solve", "input": "n=4", "output": "True (\"Even\")"},
    {"id": "3", "title": "Find Maximum", "desc": "Find the maximum of two numbers `solve(a, b)`.", "diff": "Easy", "args": "a, b", "j_args": "int a, int b", "j_ret": "int", "fname": "solve", "input": "a=10, b=20", "output": "20"},
    {"id": "4", "title": "Reverse String", "desc": "Reverse the given string.", "diff": "Easy", "args": "s", "j_args": "String s", "j_ret": "String", "input": "\"hello\"", "output": "\"olleh\""},
    {"id": "5", "title": "Count Vowels", "desc": "Count the number of vowels in a string.", "diff": "Easy", "args": "s", "j_args": "String s", "j_ret": "int", "input": "\"coding\"", "output": "2"},
    {"id": "6", "title": "Factorial", "desc": "Find the factorial of a number.", "diff": "Medium", "args": "n", "j_args": "int n", "j_ret": "int", "input": "n=5", "output": "120"},
    {"id": "7", "title": "Palindrome", "desc": "Check if a string is a palindrome.", "diff": "Easy", "args": "s", "j_args": "String s", "j_ret": "boolean", "input": "\"racecar\"", "output": "True"},
    {"id": "8", "title": "Sum of List", "desc": "Calculate the sum of all elements in a list/array.", "diff": "Easy", "args": "nums", "j_args": "int[] nums", "j_ret": "int", "input": "[1, 2, 3, 4]", "output": "10"},
    {"id": "9", "title": "Largest Element", "desc": "Find the largest element in a list/array.", "diff": "Easy", "args": "nums", "j_args": "int[] nums", "j_ret": "int", "input": "[5, 8, 2, 10]", "output": "10"},
    {"id": "10", "title": "Count Words", "desc": "Count the number of words in a sentence.", "diff": "Easy", "args": "s", "j_args": "String s", "j_ret": "int", "input": "\"Sky is blue\"", "output": "3"},
    {"id": "11", "title": "String Length", "desc": "Find length of string without using built-in length function.", "diff": "Medium", "args": "s", "j_args": "String s", "j_ret": "int", "input": "\"nest\"", "output": "4"},
    {"id": "12", "title": "Prime Number", "desc": "Check if a number is prime.", "diff": "Medium", "args": "n", "j_args": "int n", "j_ret": "boolean", "input": "n=7", "output": "True"},
    {"id": "13", "title": "Fibonacci", "desc": "Find the Nth Fibonacci number.", "diff": "Medium", "args": "n", "j_args": "int n", "j_ret": "int", "input": "n=6", "output": "8"},
    {"id": "14", "title": "Count Evens", "desc": "Count even numbers in a list.", "diff": "Easy", "args": "nums", "j_args": "int[] nums", "j_ret": "int", "input": "[1, 2, 3, 4, 5, 6]", "output": "3"},
    {"id": "15", "title": "To Uppercase", "desc": "Convert string to uppercase.", "diff": "Medium", "args": "s", "j_args": "String s", "j_ret": "String", "input": "\"react\"", "output": "\"REACT\""},
    {"id": "16", "title": "Find Minimum", "desc": "Find the minimum number in a list.", "diff": "Easy", "args": "nums", "j_args": "int[] nums", "j_ret": "int", "input": "[10, 20, 5, 40]", "output": "5"},
    {"id": "17", "title": "Remove Duplicates", "desc": "Remove duplicates from a list.", "diff": "Medium", "args": "nums", "j_args": "int[] nums", "j_ret": "int[]", "input": "[1, 2, 2, 3, 4, 4]", "output": "[1, 2, 3, 4]"},
    {"id": "18", "title": "Second Largest", "desc": "Find the second largest number in a list.", "diff": "Medium", "args": "nums", "j_args": "int[] nums", "j_ret": "int", "input": "[10, 20, 5, 40]", "output": "20"},
    {"id": "19", "title": "Reverse List", "desc": "Reverse a list/array.", "diff": "Easy", "args": "nums", "j_args": "int[] nums", "j_ret": "int[]", "input": "[1, 2, 3]", "output": "[3, 2, 1]"},
    {"id": "20", "title": "Anagram Check", "desc": "Check if two strings are anagrams.", "diff": "Medium", "args": "s1, s2", "j_args": "String s1, String s2", "j_ret": "boolean", "input": "\"listen\", \"silent\"", "output": "True"},
    {"id": "21", "title": "Leap Year", "desc": "Check if a year is a leap year.", "diff": "Easy", "args": "year", "j_args": "int year", "j_ret": "boolean", "input": "year=2024", "output": "True"},
]

# --------------------------------------------------
# TEST CASES
# --------------------------------------------------
# --------------------------------------------------
# COMPREHENSIVE TEST CASES (All 21 Problems)
# --------------------------------------------------
TEST_CASES = {
    # 1. Add Two Numbers
    "1": {"cases": [{"input": (5, 3), "expected": 8}, {"input": (10, 2), "expected": 12}, {"input": (0, 0), "expected": 0}]},
    # 2. Check Even or Odd
    "2": {"cases": [{"input": (4,), "expected": True}, {"input": (7,), "expected": False}, {"input": (0,), "expected": True}]},
    # 3. Find Maximum
    "3": {"cases": [{"input": (10, 20), "expected": 20}, {"input": (5, 2), "expected": 5}, {"input": (-1, -5), "expected": -1}]},
    # 4. Reverse String
    "4": {"cases": [{"input": ("hello",), "expected": "olleh"}, {"input": ("world",), "expected": "dlrow"}, {"input": ("a",), "expected": "a"}]},
    # 5. Count Vowels
    "5": {"cases": [{"input": ("coding",), "expected": 2}, {"input": ("sky",), "expected": 0}, {"input": ("aeiou",), "expected": 5}]},
    # 6. Factorial
    "6": {"cases": [{"input": (5,), "expected": 120}, {"input": (0,), "expected": 1}, {"input": (3,), "expected": 6}]},
    # 7. Palindrome
    "7": {"cases": [{"input": ("racecar",), "expected": True}, {"input": ("hello",), "expected": False}, {"input": ("madam",), "expected": True}]},
    # 8. Sum of List
    "8": {"cases": [{"input": ([1, 2, 3, 4],), "expected": 10}, {"input": ([],), "expected": 0}, {"input": ([5],), "expected": 5}]},
    # 9. Largest Element
    "9": {"cases": [{"input": ([5, 8, 2, 10],), "expected": 10}, {"input": ([1],), "expected": 1}, {"input": ([-1, -5, -2],), "expected": -1}]},
    # 10. Count Words
    "10": {"cases": [{"input": ("Sky is blue",), "expected": 3}, {"input": ("Hello",), "expected": 1}, {"input": ("",), "expected": 0}]},
    # 11. String Length
    "11": {"cases": [{"input": ("nest",), "expected": 4}, {"input": ("",), "expected": 0}, {"input": ("a b",), "expected": 3}]},
    # 12. Prime Number
    "12": {"cases": [{"input": (7,), "expected": True}, {"input": (4,), "expected": False}, {"input": (1,), "expected": False}]},
    # 13. Fibonacci
    "13": {"cases": [{"input": (6,), "expected": 8}, {"input": (1,), "expected": 1}, {"input": (0,), "expected": 0}]},
    # 14. Count Evens
    "14": {"cases": [{"input": ([1, 2, 3, 4, 5, 6],), "expected": 3}, {"input": ([1, 3, 5],), "expected": 0}, {"input": ([2, 4, 6],), "expected": 3}]},
    # 15. To Uppercase
    "15": {"cases": [{"input": ("react",), "expected": "REACT"}, {"input": ("Hello",), "expected": "HELLO"}, {"input": ("",), "expected": ""}]},
    # 16. Find Minimum
    "16": {"cases": [{"input": ([10, 20, 5, 40],), "expected": 5}, {"input": ([1],), "expected": 1}, {"input": ([-1, -5],), "expected": -5}]},
    # 17. Remove Duplicates
    "17": {"cases": [{"input": ([1, 2, 2, 3, 4, 4],), "expected": [1, 2, 3, 4]}, {"input": ([1, 1, 1],), "expected": [1]}, {"input": ([],), "expected": []}]},
    # 18. Second Largest
    "18": {"cases": [{"input": ([10, 20, 5, 40],), "expected": 20}, {"input": ([1, 2],), "expected": 1}, {"input": ([5, 5, 5],), "expected": None}]},
    # 19. Reverse List
    "19": {"cases": [{"input": ([1, 2, 3],), "expected": [3, 2, 1]}, {"input": ([5],), "expected": [5]}, {"input": ([],), "expected": []}]},
    # 20. Anagram Check
    "20": {"cases": [{"input": ("listen", "silent"), "expected": True}, {"input": ("hello", "world"), "expected": False}, {"input": ("abc", "cba"), "expected": True}]},
    # 21. Leap Year
    "21": {"cases": [{"input": (2024,), "expected": True}, {"input": (2023,), "expected": False}, {"input": (2000,), "expected": True}]},
}

# --------------------------------------------------
# SAFETY & TIMEOUT (using multiprocessing)
# --------------------------------------------------
import concurrent.futures

def run_python_test(code: str, problem_id: str):
    # problem_id comes as 'python1', 'python2' etc. Extract numeric part.
    numeric_id = "".join(filter(str.isdigit, problem_id)) 
    spec = TEST_CASES.get(numeric_id)
    
    if not spec:
        return {"passed": False, "error": f"Test cases not defined for {problem_id}"}

    function_name = "solve"
    
    # 1. Fast check for basic function definition
    if f"def {function_name}" not in code:
        return {"passed": False, "error": f"Function '{function_name}' not found in your code."}

    # Restricted execution environment
    safe_globals = {
        "__builtins__": {
            "len": len,
            "range": range,
            "print": print,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "abs": abs,
            "max": max,
            "min": min,
            "sum": sum,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
        }
    }

    def _execute():
        try:
            # Execute code
            exec(code, safe_globals)
            func = safe_globals.get(function_name)
            
            if not func or not callable(func):
                return {"passed": False, "error": f"Function '{function_name}' is not defined correctly."}

            # Run test cases
            for i, case in enumerate(spec['cases']):
                actual = func(*case['input'])
                if actual != case['expected']:
                    return {
                        "passed": False,
                        "error": f"Test case {i+1} failed",
                        "details": f"Input: {case['input']}, Expected: {case['expected']}, Got: {actual}"
                    }
            return {"passed": True}
        except Exception as e:
            return {"passed": False, "error": f"Runtime Error: {str(e)}"}

    # 2. Use ThreadPoolExecutor for timeout (Vercel-friendly)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_execute)
        try:
            return future.result(timeout=2) # 2 second limit
        except concurrent.futures.TimeoutError:
            return {"passed": False, "error": "Code took too long to execute (Timeout)"}
        except Exception as e:
            return {"passed": False, "error": f"Internal Error: {str(e)}"}

import os
import tempfile
import json

def run_java_test(code: str, problem_id: str):
    numeric_id = "".join(filter(str.isdigit, problem_id))
    spec = TEST_CASES.get(numeric_id)
    if not spec:
        return {"passed": False, "error": f"Test cases not defined for {problem_id}"}

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write Solution.java
        java_file = os.path.join(tmpdir, "Solution.java")
        with open(java_file, "w") as f:
            f.write(code)

        # Compile
        compile_res = subprocess.run(["javac", java_file], capture_output=True, text=True)
        if compile_res.returncode != 0:
            return {"passed": False, "error": f"Compilation Error: {compile_res.stderr}"}

        # For each test case, we run a small Java wrapper
        for i, case in enumerate(spec['cases']):
            # Convert input to Java-friendly string
            args_str = ", ".join(map(lambda x: json.dumps(x), case['input']))
            
            # This is a bit complex for Java because we need to call the method.
            # We'll create a TestRunner.java
            runner_code = f"""
import java.util.*;

public class TestRunner {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
        try {{
            Object result = sol.solve({args_str});
            System.out.println(JSONSerializer.serialize(result));
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
    }}
}}

class JSONSerializer {{
    public static String serialize(Object obj) {{
        if (obj == null) return "null";
        if (obj instanceof String) return "\\"" + obj + "\\"";
        if (obj instanceof List) {{
           return Arrays.toString(((List)obj).toArray());
        }}
        if (obj.getClass().isArray()) {{
            if (obj instanceof int[]) return Arrays.toString((int[])obj);
            if (obj instanceof boolean[]) return Arrays.toString((boolean[])obj);
            return Arrays.deepToString((Object[])obj);
        }}
        return obj.toString();
    }}
}}
"""
            runner_file = os.path.join(tmpdir, "TestRunner.java")
            with open(runner_file, "w") as f:
                f.write(runner_code)
            
            subprocess.run(["javac", "-cp", tmpdir, runner_file], capture_output=True, text=True)
            
            run_res = subprocess.run(["java", "-cp", tmpdir, "TestRunner"], capture_output=True, text=True, timeout=2)
            if run_res.returncode != 0:
                return {"passed": False, "error": f"Runtime Error on case {i+1}: {run_res.stderr}"}
            
            actual_str = run_res.stdout.strip()
            expected_str = str(case['expected']).replace("True", "true").replace("False", "false")
            
            # Simple string comparison for now, can be improved
            if actual_str != expected_str and actual_str.lower() != expected_str.lower():
                return {
                    "passed": False,
                    "error": f"Test case {i+1} failed",
                    "details": f"Input: {case['input']}, Expected: {expected_str}, Got: {actual_str}"
                }
        
        return {"passed": True}

def run_javascript_test(code: str, problem_id: str):
    numeric_id = "".join(filter(str.isdigit, problem_id))
    spec = TEST_CASES.get(numeric_id)
    if not spec:
        return {"passed": False, "error": f"Test cases not defined for {problem_id}"}

    with tempfile.TemporaryDirectory() as tmpdir:
        js_file = os.path.join(tmpdir, "solution.js")
        
        # Prepare valid JS code that exports solve
        full_code = code + "\n\n"
        
        for i, case in enumerate(spec['cases']):
            args_str = ", ".join(map(lambda x: json.dumps(x), case['input']))
            test_runner_js = f"""
{code}
try {{
    const result = solve({args_str});
    console.log(JSON.stringify(result));
}} catch (e) {{
    console.error(e.message);
    process.exit(1);
}}
"""
            runner_file = os.path.join(tmpdir, f"test_{i}.js")
            with open(runner_file, "w") as f:
                f.write(test_runner_js)
            
            run_res = subprocess.run(["node", runner_file], capture_output=True, text=True, timeout=2)
            if run_res.returncode != 0:
                return {"passed": False, "error": f"Runtime Error on case {i+1}: {run_res.stderr}"}
            
            actual_str = run_res.stdout.strip()
            expected_json = json.dumps(case['expected'])
            
            if actual_str != expected_json:
                return {
                    "passed": False,
                    "error": f"Test case {i+1} failed",
                    "details": f"Input: {case['input']}, Expected: {expected_json}, Got: {actual_str}"
                }
                
        return {"passed": True}
import subprocess

# --------------------------------------------------
# GENERATE PROBLEMS
# --------------------------------------------------
def generate_problems(lang):
    problems = []
    for p in PROBLEMS_DATA:
        pid = f"{lang}{p['id']}"
        starter = ""
        
        if lang == "python":
            starter = f"def solve({p['args']}):\n    # {p['title']}\n    pass"
        elif lang == "java":
            starter = f"class Solution {{\n    public {p['j_ret']} solve({p['j_args']}) {{\n        // {p['title']}\n        return " 
            if p['j_ret'] == 'boolean': starter += "false;"
            elif p['j_ret'] == 'int': starter += "0;"
            elif "[]" in p['j_ret']: starter += "new int[0];"
            else: starter += "null;"
            starter += "\n    }}\n}}"
        elif lang == "javascript":
            starter = f"function solve({p['args']}) {{\n    // {p['title']}\n}}"
            
        problems.append({
            "id": pid,
            "title": p["title"],
            "difficulty": p["diff"],
            "description": p["desc"],
            "input": p.get("input", "N/A"),
            "output": p.get("output", "N/A"),
            "test_cases": TEST_CASES.get(p["id"], {}).get("cases", []),
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

# --------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------
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
    code = request.code.strip()
    
    if len(code) < 15:
        return {"status": "Failed", "error": "Code is too short."}
    
    # 1. EVALUATE BASED ON LANGUAGE
    if request.language == "python":
        result = run_python_test(code, request.problem_id)
    elif request.language == "java":
        result = run_java_test(code, request.problem_id)
    elif request.language == "javascript":
        result = run_javascript_test(code, request.problem_id)
    else:
        return {"status": "Failed", "error": f"Language {request.language} not supported."}

    if not result["passed"]:
        return {
            "status": "Failed", 
            "error": result["error"],
            "details": result.get("details", "")
        }
    status = "Passed"

    # 2. SAVE PROGRESS IF PASSED
    if status in ["Passed", "Mocked (Pass)"]:
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
