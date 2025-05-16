# Testing Guide for dueDash

## Overview
This guide covers the testing setup for the dueDash API, focusing on the provided `login_test.py` script, which uses the requests library to test signup, login, todo creation, and cleanup. It also provides guidance for expanding tests and troubleshooting common issues on Windows PowerShell.

## Testing Dependencies
The testing setup relies on:

- **requests>=2.28.2**: For making HTTP requests in `login_test.py` (included in requirements.txt).

Optional tools for advanced testing:

- **pytest**: For unit and integration testing.
- **httpx**: For async HTTP requests with FastAPI test clients.
- **testcontainers**: For isolated PostgreSQL testing.

Install optional tools if needed:
```
pip install pytest httpx
```

## Running Existing Tests
The `login_test.py` script tests the authentication and todo creation flow, with cleanup to avoid redundant data.

### Prerequisites

- The API must be running:
  ```
  cd C:\Users\<YourUsername>\OneDrive\Desktop\todo
  .\venv\Scripts\activate
  uvicorn main:app --reload
  ```
- PostgreSQL database must be set up and initialized (see [setup.md](setup.md)).
- The `.env` file must be configured with `DATABASE_URL`, `SECRET_KEY`, etc.

### Run the Test
Execute the test script:
```
python login_test.py
```

### Expected Output
The script:

1. Signs up a unique user (e.g., `testuser_<random-id>`).
2. Logs in to obtain a JWT.
3. Creates a todo item.
4. Deletes the todo and verifies it no longer exists.

Example output:
```
✓ User created successfully
✓ Logged in successfully
✓ Todo created successfully
Create Todo Status: 200
Todo Response: {'id': 1, 'title': 'Buy groceries', 'description': 'Milk, Bread, Eggs', 'due_time': '2025-05-11T14:30:00', 'completed': False, 'user_id': 1}
✓ Todo deleted successfully
✓ Verified todo no longer exists
```

## Troubleshooting

### API Not Running:
- Ensure the server is running (`uvicorn main:app --reload`).
- Check http://127.0.0.1:8000/health with `Invoke-RestMethod`.

### File Not Found:
- Verify the project directory: `cd C:\Users\<YourUsername>\OneDrive\Desktop\todo`.
- Check file existence: `dir login_test.py`.
- Run with full path: `python C:\Users\<YourUsername>\OneDrive\Desktop\todo\login_test.py`.

### Database Error:
- Verify `DATABASE_URL` in `.env`.
- Ensure PostgreSQL is running (`pg_ctl -D "C:\Program Files\PostgreSQL\<version>\data" start`).

### Redundant Todos:
- If previous tests left todos, reset the database:
  ```
  psql -U postgres -c "DROP DATABASE todoapp;"
  psql -U postgres -c "CREATE DATABASE todoapp;"
  python init_db.py
  ```

## Writing New Tests
To extend testing, modify `login_test.py` or create a pytest-based suite.

### Example: Adding a Test to login_test.py
Add a test for retrieving all todos (insert before the delete step in `login_test.py`):
```python
# Get All Todos
todos_response = requests.get(f"{BASE_URL}/todos", headers=headers)
if todos_response.status_code == 200:
    print("✓ Retrieved todos successfully")
    print("Todos Response:", todos_response.json())
else:
    print("✗ Failed to retrieve todos:", todos_response.text)
```

Run the updated script:
```
python login_test.py
```

### Using Pytest for Advanced Testing
For a scalable testing setup, use pytest with FastAPI's TestClient.

Install dependencies:
```
pip install pytest httpx
```

Create a tests directory and `
