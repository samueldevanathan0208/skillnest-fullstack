import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"
USER_ID = 15 # CertTest

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def verify_edit():
    print(f"--- Verifying Edit for User {USER_ID} (Urllib) ---")
    
    # 1. Get current data
    print("1. Fetching current user data...")
    current_user = make_request('GET', f"/user/{USER_ID}")
    if not current_user:
        return
        
    print(f"   Current Name: {current_user.get('user_name')}")
    
    # 2. Prepare Update Data
    new_name = "CertTest Verified"
    update_data = {
        "user_name": new_name,
        "user_email": current_user.get('user_email'),
        "user_phone": "9876543210",
        "user_dateofbirth": current_user.get('user_dateofbirth'),
        "user_gender": "Male"
    }
    
    print(f"2. Sending Update: Name -> '{new_name}'")
    
    # 3. Send PUT
    put_response = make_request('PUT', f"/user/{USER_ID}", update_data)
    
    if put_response and put_response.get("status") == "success":
        print("   PUT Request Successful.")
    else:
        print(f"   PUT Request Failed: {put_response}")
        return

    # 4. Verify Persistence
    print("3. Verifying persistence (Fetching data again)...")
    updated_user = make_request('GET', f"/user/{USER_ID}")
    
    print(f"   Updated Name from DB: {updated_user.get('user_name')}")
    
    if updated_user.get('user_name') == new_name:
        print("   ✅ SUCCESS: Name was updated in the database.")
    else:
        print("   ❌ FAILURE: Name did not change in the database.")

if __name__ == "__main__":
    verify_edit()
