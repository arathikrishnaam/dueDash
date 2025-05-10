import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

# Step 1: Signup
signup_payload = {
    "username": "testuser",
    "password": "testpass"
}
signup_response = requests.post(f"{BASE_URL}/signup", json=signup_payload)

if signup_response.status_code == 200:
    print("✓ User created successfully")
elif signup_response.status_code == 400:
    print("⚠️  User already exists, continuing to login...")
else:
    print("✗ Signup failed:", signup_response.text)
    exit()

# Step 2: Login
login_payload = {
    "username": "testuser",
    "password": "testpass"
}
login_response = requests.post(f"{BASE_URL}/login", data=login_payload)

if login_response.status_code != 200:
    print("✗ Login failed")
    exit()

token = login_response.json()["access_token"]
print("✓ Logged in successfully")

# Step 3: Create a Todo
todo_payload = {
    "title": "Buy groceries",
    "description": "Milk, Bread, Eggs",
    "due_time": (datetime.now() + timedelta(days=1)).isoformat()
}
headers = {"Authorization": f"Bearer {token}"}
todo_response = requests.post(f"{BASE_URL}/todos", json=todo_payload, headers=headers)

print("Create Todo Status:", todo_response.status_code)
print("Todo Response:", todo_response.json())
