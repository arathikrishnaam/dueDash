# Setup Guide for dueDash

## Overview
This guide provides step-by-step instructions for setting up the dueDash API development environment, initializing the database, and running the application locally on Windows using PowerShell.

## Prerequisites
Before starting, ensure you have the following installed:

- **Python**: Version 3.9 or higher (ensure `python --version` shows 3.9+).
- **PostgreSQL**: A running PostgreSQL server (version 12 or higher recommended).
- **pip**: Python package manager (included with Python).
- **Git**: For cloning the repository.
- **Windows PowerShell**: For running commands.

## Step-by-Step Setup

### 1. Clone the Repository
Clone the dueDash repository to your local machine:
```
git clone <repository-url>
cd C:\Users\<YourUsername>\OneDrive\Desktop\todo
```

### 2. Create a Virtual Environment
Set up a virtual environment to isolate project dependencies:
```
python -m venv venv
.\venv\Scripts\activate
```

Verify the virtual environment is active (you'll see `(venv)` in the prompt). To deactivate later:
```
deactivate
```

### 3. Install Dependencies
Install the required Python packages listed in requirements.txt:
```
pip install -r requirements.txt
```

Key dependencies include:

- **fastapi>=0.95.0**: Web framework.
- **sqlmodel>=0.0.8**: ORM for database interactions.
- **uvicorn>=0.21.1**: ASGI server for running the API.
- **python-jose>=3.3.0** and **passlib>=1.7.4**: For JWT authentication.
- **python-dotenv>=1.0.0**: For environment variable management.
- **requests>=2.28.2**: For testing with login_test.py.

### 4. Configure PostgreSQL
Ensure a PostgreSQL server is running. Create a database for the project:
```
psql -U postgres -c "CREATE DATABASE todoapp;"
```

Verify connectivity using psql:
```
psql -h localhost -U postgres -d todoapp
```

If `psql` is not recognized, add PostgreSQL's bin directory to your PATH (e.g., `C:\Program Files\PostgreSQL\<version>\bin`).

### 5. Set Up Environment Variables
Create a `.env` file in the project root (e.g., `C:\Users\<YourUsername>\OneDrive\Desktop\todo`) with the following content:
```
DATABASE_URL=postgresql://postgres:<your-password>@localhost:5432/todoapp
SECRET_KEY=<your-secure-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace:

- `<your-password>` with your PostgreSQL password.
- `<your-secure-secret-key>` with a strong key (generate with `openssl rand -hex 32` in PowerShell).

**Security Note**: Add `.env` to `.gitignore` to prevent committing sensitive data.

### 6. Initialize the Database
Run the init_db.py script to create the necessary database tables:
```
python init_db.py
```

This script uses SQLModel to create `User` and `Todo` tables defined in `models.py`.

### 7. Run the Application
Start the FastAPI server using Uvicorn:
```
uvicorn main:app --reload
```

- `--reload`: Enables auto-reload for development.
- The API will be available at http://127.0.0.1:8000.

### 8. Verify the Setup
Check if the API is running:
```
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "<current-timestamp>"}
```

Check database connectivity:
```
Invoke-RestMethod -Uri http://127.0.0.1:8000/health/db
```

Expected response:
```json
{"status": "healthy", "timestamp": "<current-timestamp>"}
```

Explore the interactive API documentation at:

- http://127.0.0.1:8000/docs (Swagger UI)
- http://127.0.0.1:8000/redoc (ReDoc)

## Troubleshooting

### Database Connection Error:
- Verify DATABASE_URL in `.env` matches your PostgreSQL setup.
- Ensure PostgreSQL is running (`pg_ctl -D "C:\Program Files\PostgreSQL\<version>\data" start`).

### Module Not Found:
- Confirm the virtual environment is active (`.\venv\Scripts\activate`).
- Reinstall dependencies: `pip install -r requirements.txt`.

### File Not Found (e.g., `login_test.py`):
- Ensure you're in the project directory: `cd C:\Users\<YourUsername>\OneDrive\Desktop\todo`.
- Verify the file exists: `dir login_test.py`.
- Run with full path if needed: `python C:\Users\<YourUsername>\OneDrive\Desktop\todo\login_test.py`.

### Port Conflict:
- If port 8000 is in use, specify a different port: `uvicorn main:app --port 8001 --reload`.

### Environment Variables Not Loaded:
- Ensure `.env` is in the project root and correctly formatted.

