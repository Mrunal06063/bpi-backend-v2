# BPI Backend - Authentication API

Clean, minimal authentication backend with JWT tokens and role-based access.

## Features

- User signup and login
- Password hashing with bcrypt
- JWT token authentication
- Role-based access (employee/customer)
- Email validation
- Active user status tracking

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file (already created):
```env
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bpi_auth

SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

3. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /auth/signup
Create a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@blauplug.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "email": "john@blauplug.com",
  "role": "employee",
  "access_token": "eyJhbGc..."
}
```

**Roles:**
- `@blauplug.com` emails → `employee`
- Other emails → `customer`

### POST /auth/login
Login with existing credentials.

**Request:**
```json
{
  "email": "john@blauplug.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "email": "john@blauplug.com",
  "role": "employee",
  "access_token": "eyJhbGc..."
}
```

## Database Schema

**users** table:
- `id` - Primary key
- `name` - User's full name
- `email` - Unique email (indexed)
- `password` - Bcrypt hashed password
- `role` - employee or customer
- `is_active` - Account status (default: true)
- `created_at` - Timestamp
- `updated_at` - Auto-updated timestamp

## Project Structure

```
app/
├── main.py       # FastAPI app, CORS, routes
├── auth.py       # Signup/login endpoints
├── models.py     # SQLAlchemy User model
├── schemas.py    # Pydantic request/response models
├── database.py   # DB connection & session
├── jwt.py        # JWT token generation
└── utils.py      # Password hashing utilities
```

## Security

- Passwords hashed with bcrypt
- JWT tokens with configurable expiry
- Email validation
- Inactive account blocking
- Same error message for invalid email/password (prevents enumeration)
