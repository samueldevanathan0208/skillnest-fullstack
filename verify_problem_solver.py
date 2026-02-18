import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock environment variables for database
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"

from api.problem_solving import run_python_test

# Test 1: Incorrect Solution (should fail)
code_fail = """
def solve(a, b):
    return a
"""
result_fail = run_python_test(code_fail, "python1")
print(f"Test 1 (return a): {result_fail}")

# Test 2: Correct Solution (should pass)
code_pass = """
def solve(a, b):
    return a + b
"""
result_pass = run_python_test(code_pass, "python1")
print(f"Test 2 (return a + b): {result_pass}")

# Test 3: Infinite Loop (should timeout)
code_timeout = """
def solve(a, b):
    while True:
        pass
"""
result_timeout = run_python_test(code_timeout, "python1")
print(f"Test 3 (infinite loop): {result_timeout}")
