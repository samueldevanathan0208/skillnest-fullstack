import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_notes_persistence():
    user_id = 999
    course_id = "test_course"
    note_content = "This is a test note for persistence check."

    print(f"1. Saving notes for User {user_id}, Course {course_id}...")
    save_url = f"{BASE_URL}/notes/save"
    payload = {
        "user_id": user_id,
        "course_id": course_id,
        "notes": note_content
    }
    
    try:
        response = requests.post(save_url, json=payload)
        if response.status_code == 200:
            print("✅ Save Success:", response.json())
        else:
            print("❌ Save Failed:", response.text)
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    print("\n2. Simulating Logout/Login (Fetching notes from DB)...")
    get_url = f"{BASE_URL}/notes/{user_id}/{course_id}"
    
    try:
        response = requests.get(get_url)
        if response.status_code == 200:
            data = response.json()
            retrieved_note = data.get("notes")
            print(f"📥 Retrieved Note: '{retrieved_note}'")
            
            if retrieved_note == note_content:
                print("✅ PERSISTENCE VERIFIED: Notes match exactly!")
            else:
                print("❌ MISMATCH: Notes do not match.")
        else:
            print("❌ Fetch Failed:", response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_notes_persistence()
