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
        # ---------------- SUBSCRIBER TEST ----------------
        print("\n--- Testing SUBSCRIBER ---")
        status, res_body = make_request(f"{BASE_URL}/login", "POST", {
            "email": "subscriber@chembank.com",
            "password": "subscriber123"
        })
        assert status == 200, f"Subscriber login failed: {res_body}"
        sub_token = res_body["access_token"]
        sub_headers = {"Authorization": f"Bearer {sub_token}"}
        
        # Can Search / View Drugs (GET /drugs/)
        status, res_body = make_request(f"{BASE_URL}/drugs/", "GET", headers=sub_headers)
        print(f"GET /drugs/ status code: {status} (Expected: 200)")
        assert status == 200, f"Subscriber could not search drugs: {res_body}"
        
        # Cannot Add Drug (POST /drugs/)
        status, res_body = make_request(f"{BASE_URL}/drugs/", "POST", {"data": "{}"}, headers=sub_headers)
        print(f"POST /drugs/ status code: {status} (Expected: 403)")
        assert status == 403, f"Subscriber allowed to add drug: {res_body}"

        # Cannot View All Users (GET /allusers)
        status, res_body = make_request(f"{BASE_URL}/allusers", "GET", headers=sub_headers)
        print(f"GET /allusers status code: {status} (Expected: 403)")
        assert status == 403, f"Subscriber allowed to view users: {res_body}"
        
        
        # ---------------- EDITOR TEST ----------------
        print("\n--- Testing EDITOR ---")
        status, res_body = make_request(f"{BASE_URL}/login", "POST", {
            "email": "editor@chembank.com",
            "password": "editor123"
        })
        assert status == 200, f"Editor login failed: {res_body}"
        ed_token = res_body["access_token"]
        ed_headers = {"Authorization": f"Bearer {ed_token}"}
        
        # Can Search / View Drugs (GET /drugs/)
        status, res_body = make_request(f"{BASE_URL}/drugs/", "GET", headers=ed_headers)
        print(f"GET /drugs/ status code: {status} (Expected: 200)")
        assert status == 200
        
        # Can Add Drug (POST /drugs/) -> Should get 200 (since payload with all optional fields is valid)
        status, res_body = make_request(f"{BASE_URL}/drugs/", "POST", {"data": "{}"}, headers=ed_headers)
        print(f"POST /drugs/ status code: {status} (Expected: 200)")
        assert status == 200, f"Editor add drug returned unexpected status: {status}"
        
        # Cannot Delete Drug (DELETE /drugs/{id}) -> Should get 403
        status, res_body = make_request(f"{BASE_URL}/drugs/60c72b2f9b1d8e1f5c8b4567", "DELETE", headers=ed_headers)
        print(f"DELETE /drugs/ status code: {status} (Expected: 403)")
        assert status == 403, f"Editor allowed to delete drug: {res_body}"

        # Cannot View All Users (GET /allusers)
        status, res_body = make_request(f"{BASE_URL}/allusers", "GET", headers=ed_headers)
        print(f"GET /allusers status code: {status} (Expected: 403)")
        assert status == 403, f"Editor allowed to view users: {res_body}"
        
        
        # ---------------- ADMIN TEST ----------------
        print("\n--- Testing ADMIN ---")
        status, res_body = make_request(f"{BASE_URL}/login", "POST", {
            "email": "admin@chembank.com",
            "password": "admin123"
        })
        assert status == 200, f"Admin login failed: {res_body}"
        admin_token = res_body["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Can View All Users (GET /allusers)
        status, res_body = make_request(f"{BASE_URL}/allusers", "GET", headers=admin_headers)
        print(f"GET /allusers status code: {status} (Expected: 200)")
        assert status == 200, f"Admin cannot view users: {res_body}"
        
        # Can Delete Drug (DELETE /drugs/{id}) -> Should get 404 (not found) not 403
        status, res_body = make_request(f"{BASE_URL}/drugs/60c72b2f9b1d8e1f5c8b4567", "DELETE", headers=admin_headers)
        print(f"DELETE /drugs/ status code: {status} (Expected: 404 not found)")
        assert status == 404, f"Admin delete drug returned unexpected status: {status}"

        print("\nRBAC verification tests completed successfully!")
        
    finally:
        print(f"Shutting down uvicorn server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_tests()
