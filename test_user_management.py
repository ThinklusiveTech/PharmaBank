import subprocess
import time
import sys
import os
import json
import urllib.request
import urllib.error

PORT = "8002"
BASE_URL = f"http://localhost:{PORT}/v1"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req_headers = headers.copy()
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            body = response.read().decode("utf-8")
            try:
                res_data = json.loads(body)
            except json.JSONDecodeError:
                res_data = body
            return status_code, res_data
    except urllib.error.HTTPError as e:
        status_code = e.code
        body = e.read().decode("utf-8")
        try:
            res_data = json.loads(body)
        except json.JSONDecodeError:
            res_data = body
        return status_code, res_data
    except urllib.error.URLError as e:
        print(f"URL Error connecting to {url}: {e.reason}")
        return 0, str(e.reason)

def run_tests():
    # 1. Start Server
    print(f"Starting uvicorn server on port {PORT}...")
    env = os.environ.copy()
    env["MONGO_URL"] = "mongodb://localhost:27017"
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", PORT],
        cwd=".",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(3.0)
    
    try:
        # 1. Login as Admin
        print("\n--- Logging in as Admin ---")
        status, res_body = make_request(f"{BASE_URL}/login", "POST", {
            "email": "admin@chembank.com",
            "password": "admin123"
        })
        assert status == 200, f"Admin login failed: {res_body}"
        admin_token = res_body["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 2. Login as Subscriber (to test unauthorized role update)
        print("\n--- Logging in as Subscriber ---")
        status, res_body = make_request(f"{BASE_URL}/login", "POST", {
            "email": "subscriber@chembank.com",
            "password": "subscriber123"
        })
        assert status == 200, f"Subscriber login failed: {res_body}"
        sub_token = res_body["access_token"]
        sub_headers = {"Authorization": f"Bearer {sub_token}"}

        # 3. Get all users as Admin
        print("\n--- Fetching all users ---")
        status, res_body = make_request(f"{BASE_URL}/allusers", "GET", headers=admin_headers)
        assert status == 200, f"Failed to get users: {res_body}"
        users_list = res_body["data"]
        
        # Find the subscriber user
        sub_user = next((u for u in users_list if u["email"] == "subscriber@chembank.com"), None)
        assert sub_user is not None, "Subscriber user not found in the seeded DB"
        sub_user_id = sub_user["_id"]
        print(f"Found Subscriber user with ID: {sub_user_id}")

        # 4. Try updating Subscriber's role using Subscriber's token (should fail)
        print("\n--- Updating role as Subscriber (should fail with 403) ---")
        status, res_body = make_request(f"{BASE_URL}/user/{sub_user_id}", "PUT", {"roles": ["editor"]}, headers=sub_headers)
        print(f"PUT /user/{sub_user_id} status code: {status} (Expected: 403)")
        assert status == 403, f"Non-admin user was able to update role: {res_body}"

        # 5. Update Subscriber's role to editor using Admin's token (should succeed)
        print("\n--- Updating role as Admin (should succeed) ---")
        status, res_body = make_request(f"{BASE_URL}/user/{sub_user_id}", "PUT", {"roles": ["editor"]}, headers=admin_headers)
        print(f"PUT /user/{sub_user_id} status code: {status} (Expected: 200)")
        assert status == 200, f"Admin role update failed: {res_body}"
        assert "editor" in res_body["data"]["roles"], f"Updated roles list did not contain 'editor': {res_body}"
        
        # 6. Verify role change in allusers list
        print("\n--- Verifying role change in user list ---")
        status, res_body = make_request(f"{BASE_URL}/allusers", "GET", headers=admin_headers)
        assert status == 200
        updated_sub_user = next((u for u in res_body["data"] if u["_id"] == sub_user_id), None)
        assert updated_sub_user is not None
        assert "editor" in updated_sub_user["roles"], f"Role was not saved in DB: {updated_sub_user}"
        print("Role successfully updated and verified in DB!")

        # 7. Revert back to subscriber role
        print("\n--- Reverting role back to subscriber ---")
        status, res_body = make_request(f"{BASE_URL}/user/{sub_user_id}", "PUT", {"roles": ["subscriber"]}, headers=admin_headers)
        assert status == 200, f"Role reversion failed: {res_body}"

        print("\nAll User Management Integration tests passed successfully!")
        
    finally:
        print(f"Shutting down uvicorn server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_tests()
