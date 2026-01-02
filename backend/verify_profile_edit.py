import requests
import json

BASE_URL = "http://127.0.0.1:8000"
USER_ID = 15 # CertTest

def verify_edit():
    print(f"--- Verifying Edit for User {USER_ID} ---")
    
    # 1. Get current data
    try:
        r = requests.get(f"{BASE_URL}/user/{USER_ID}")
        if r.status_code != 200:
            print(f"Failed to get user: {r.text}")
            return
        
        current_user = r.json()
        print(f"Current Name: {current_user.get('user_name')}")
        print(f"Current Phone: {current_user.get('user_phone')}")
        
        # 2. Prepare Update Data (Change name and phone)
        new_name = "Cert Test Updated"
        new_phone = "1234567890"
        
        update_data = {
            "user_name": new_name,
            "user_phone": new_phone,
            "user_email": current_user.get('user_email'), # Keep email same
            # Sending others as is or empty to see behavior
            "user_gender": "Other"
        }
        
        print(f"Sending Update: {update_data}")
        
        # 3. Send PUT
        r_put = requests.put(f"{BASE_URL}/user/{USER_ID}", json=update_data)
        
        if r_put.status_code == 200:
            print("PUT Success:", r_put.json())
        else:
            print(f"PUT Failed: {r_put.status_code} - {r_put.text}")
            return

        # 4. Verify Persistence
        r_check = requests.get(f"{BASE_URL}/user/{USER_ID}")
        updated_user = r_check.json()
        
        print(f"Updated Name: {updated_user.get('user_name')}")
        print(f"Updated Phone: {updated_user.get('user_phone')}")
        print(f"Updated Gender: {updated_user.get('user_gender')}")
        
        if updated_user.get('user_name') == new_name and updated_user.get('user_phone') == new_phone:
            print("VERIFICATION PASSED: Changes were saved.")
        else:
            print("VERIFICATION FAILED: Changes were NOT saved correctly.")
            
        # 5. Revert Changes
        print("Reverting changes...")
        revert_data = {
            "user_name": "Cert Test", # Original
            "user_phone": current_user.get('user_phone'),
            "user_gender": "Prefer not to say"
        }
        requests.put(f"{BASE_URL}/user/{USER_ID}", json=revert_data)
        print("Reverted.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_edit()
