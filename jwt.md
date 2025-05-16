# JWT Authentication in dueDash

## Overview
The dueDash API uses JSON Web Tokens (JWT) for secure user authentication. JWTs are used to verify the identity of users accessing protected endpoints, such as todo management routes. The implementation is built with the python-jose library for JWT encoding/decoding and passlib for password hashing, ensuring secure authentication.

## Dependencies
The JWT authentication system relies on the following Python packages (listed in requirements.txt):

- **python-jose>=3.3.0**: For JWT encoding and decoding.
- **passlib>=1.7.4**: For secure password hashing using bcrypt.
- **python-dotenv>=1.0.0**: For loading environment variables.

## Configuration
JWT-related settings are stored in the `.env` file and loaded in `auth.py` using python-dotenv. The key configuration variables are:

- **SECRET_KEY**: A secure key used for signing and verifying JWTs. Must be unique and kept confidential.
- **ALGORITHM**: The algorithm used for JWT signing, set to HS256 (HMAC with SHA-256).
- **ACCESS_TOKEN_EXPIRE_MINUTES**: The duration (in minutes) for which the access token is valid, defaulting to 30 minutes.

Example `.env` configuration:
```
SECRET_KEY=7oHRlT0I8rD3n8v9O4YBfMN2z2Rm12g5fW9LRz0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Security Note**: Never commit the `.env` file to version control. Generate a strong SECRET_KEY using a command like `openssl rand -hex 32` in PowerShell.

## Implementation Details

### Authentication Flow

1. **User Signup** (`POST /signup`):
   - A new user is created with a username and hashed password (using bcrypt).
   - The password is hashed using passlib's CryptContext in `auth.py` (`get_password_hash` function).
   - The user is stored in the PostgreSQL database via SQLModel.

2. **User Login** (`POST /login`):
   - The user submits a username and password via an OAuth2-compatible form (OAuth2PasswordRequestForm).
   - The password is verified against the stored hash using `verify_password`.
   - If valid, a JWT access token is generated using `create_access_token` and returned to the client.

3. **Accessing Protected Endpoints**:
   - Protected endpoints (e.g., `/todos`) require a valid JWT in the Authorization header (`Bearer <token>`).
   - The `get_current_user` function validates the token and retrieves the associated user from the database.

### Key Functions (in `auth.py`)

- **`verify_password(plain_password, hashed_password)`**:
  - Verifies a plain-text password against a hashed password using bcrypt.
  - Returns `True` if the password matches, `False` otherwise.

- **`get_password_hash(password)`**:
  - Hashes a plain-text password using bcrypt.
  - Returns the hashed password for storage in the database.

- **`create_access_token(data, expires_delta=None)`**:
  - Creates a JWT with the provided data (e.g., `{"sub": username}`).
  - Includes standard claims: `exp` (expiration time), `iat` (issued at), and `type` (set to "access").
  - Optionally accepts a custom expiration time; defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
  - Signs the token with SECRET_KEY using the HS256 algorithm.

- **`get_user(db, username)`**:
  - Retrieves a user from the database by username using SQLModel.
  - Returns the User object or None if not found.

- **`get_current_user(token, db)`**:
  - Validates a JWT and retrieves the associated user.
  - Decodes the token using SECRET_KEY and ALGORITHM.
  - Checks for token type (access), expiration, and valid claims.
  - Raises HTTP exceptions for invalid or expired tokens.
  - Returns the User object for the authenticated user.

## OAuth2 Integration
The API uses FastAPI's OAuth2PasswordBearer to handle token-based authentication. The token URL is set to `/login`, where clients send credentials to obtain a JWT. This is defined in `auth.py`:
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

## Error Handling
The JWT system includes robust error handling for various scenarios:

- **Invalid Credentials**: HTTP 401 Unauthorized with "Could not validate credentials".
- **Expired Token**: HTTP 401 Unauthorized with "Token has expired".
- **Invalid Token Type**: HTTP 401 Unauthorized with "Invalid token type".
- **Invalid Claims**: HTTP 401 Unauthorized with "Invalid token claims".
- **General JWT Errors**: HTTP 401 Unauthorized with appropriate headers.

## Usage Example
The `login_test.py` script demonstrates the JWT authentication flow using the requests library. It:

1. Signs up a unique user (e.g., `testuser_<random-id>`).
2. Logs in to obtain a JWT.
3. Creates a todo item.
4. Deletes the todo and verifies cleanup.

Run the test:
```
python login_test.py
```

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

For interactive testing, use tools like Postman or Insomnia instead of manual HTTP requests.

## Security Considerations

- **Token Expiration**: Tokens expire after 30 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES). Clients must re-authenticate to obtain a new token.
- **Secure Storage**: Clients should store JWTs securely (e.g., in memory or secure storage, not local storage).
- **HTTPS**: Use HTTPS in production to prevent token interception.
- **Secret Key**: Ensure SECRET_KEY is strong, unique, and never exposed.
- **Password Hashing**: Passwords are hashed with bcrypt, a secure and slow hashing algorithm to resist brute-force attacks.

## Testing
The `login_test.py` script tests the JWT authentication flow. Ensure the API is running:
```
uvicorn main:app --reload
```

Then run:
```
python login_test.py
```

For more testing details, see [testing.md](testing.md).

## Troubleshooting

- **Token Expired**: Re-authenticate if the token expires after 30 minutes.
- **Invalid Signature**: Verify SECRET_KEY matches in `.env`.
- **Database Errors**: Check database connectivity and user existence 
- **File Not Found**: Ensure you're in the project directory (`cd C:\path\to\dueDash`) and `login_test.py` exists (`dir login_test.py`).

## References

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [python-jose Documentation](https://python-jose.readthedocs.io/en/latest/)
- [passlib Documentation](https://passlib.readthedocs.io/en/stable/)
