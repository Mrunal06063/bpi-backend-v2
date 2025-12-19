from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import SignupRequest, LoginRequest, AuthResponse
from app.utils import hash_password, verify_password
from app.jwt import create_access_token

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Determine role based on email domain
    role = "employee" if data.email.endswith("@blauplug.com") else "customer"

    # Create new user
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return AuthResponse(email=user.email, role=user.role, access_token=access_token)


@router.post("/login", response_model=AuthResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Debug logging
    print(f"[LOGIN] Email received: '{credentials.email}'")
    print(f"[LOGIN] Password length: {len(credentials.password)}")

    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        print(f"[LOGIN] User NOT FOUND for email: '{credentials.email}'")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    print(f"[LOGIN] User found: {user.email}")
    password_valid = verify_password(credentials.password, user.password)
    print(f"[LOGIN] Password valid: {password_valid}")

    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    # Generate token
    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return AuthResponse(email=user.email, role=user.role, access_token=access_token)
