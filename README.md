# dueDash

**dueDash** is a simple, secure, and scalable Todo application API built with FastAPI, SQLModel, and PostgreSQL.
It supports user authentication (JWT-based), todo creation, and task management with features like completion tracking and overdue status.

## Features
- User registration and login with JWT authentication
- CRUD operations for todos (create, read, update, delete)
- Todo categorization (completed, to-be-done, overdue)
- Health check endpoints for monitoring
- CORS support for frontend integration
- PostgreSQL database with SQLModel ORM
- Modular and testable codebase

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLModel
- **Authentication**: JWT with OAuth2
- **Environment Management**: python-dotenv
- **Testing**: Pytest (basic test included)

## Prerequisites
- Python 3.10+
- PostgreSQL 12+
