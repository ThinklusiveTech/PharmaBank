import requests
import time

BASE_URL = "http://localhost:8001/v1" # Adjust based on main.py routing

def test_refresh_token_flow():
    # 1. Register/Login
    login_payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Try login first
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/login", json=login_payload)
    
    if response.status_code != 200:
        print("Login failed, trying registration...")
        reg_payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "roles": ["admin"]
        }
        res = requests.post(f"{BASE_URL}/register", json=reg_payload)
        print(f"Registration response: {res.status_code}, {res.json()}")
        response = requests.post(f"{BASE_URL}/login", json=login_payload)

    login_data = response.json()
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    print(f"Login successful. Access Token: {access_token[:20]}..., Refresh Token: {refresh_token[:20]}...")

    # 2. Verify Access Token on protected endpoint
    print("Verifying access token on /allusers...")
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(f"{BASE_URL}/allusers", headers=headers)
    print(f"Protected endpoint response: {res.status_code}")
    assert res.status_code == 200

    # 3. Refresh Access Token
    print("Refreshing access token...")
    refresh_payload = {"refresh_token": refresh_token}
    res = requests.post(f"{BASE_URL}/refresh", json=refresh_payload)
    print(f"Refresh response: {res.status_code}, {res.json()}")
    assert res.status_code == 200
    
    new_access_token = res.json()["access_token"]
    print(f"New Access Token: {new_access_token[:20]}...")

    # 4. Verify New Access Token
    print("Verifying new access token...")
    headers = {"Authorization": f"Bearer {new_access_token}"}
    res = requests.get(f"{BASE_URL}/allusers", headers=headers)
    print(f"Protected endpoint response with new token: {res.status_code}")
    assert res.status_code == 200

    # 5. Logout
    print("Logging out...")
    res = requests.post(f"{BASE_URL}/logout", json=refresh_payload, headers=headers)
    print(f"Logout response: {res.status_code}, {res.json()}")
    assert res.status_code == 200

    # 6. Verify Refresh Token is invalid after logout
    print("Verifying refresh token is invalid after logout...")
    res = requests.post(f"{BASE_URL}/refresh", json=refresh_payload)
    print(f"Refresh response after logout: {res.status_code}")
    if res.status_code != 401:
        print(f"Error: Expected 401 but got {res.status_code}. Content: {res.text}")
    assert res.status_code == 401

if __name__ == "__main__":
    try:
        test_refresh_token_flow()
        print("\n[OK] Refresh token flow verified successfully!")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
