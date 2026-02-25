import subprocess

def check_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        print(f"Command: {cmd}")
        print(f"Return Code: {result.returncode}")
        print(f"Stdout: {result.stdout.strip()}")
        print(f"Stderr: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

print("Checking dependencies...")
check_command("java -version")
check_command("javac -version")
check_command("node -v")
