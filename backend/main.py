from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import logging
import secrets
import string
from typing import List, Optional

from database import get_db, engine
from models import Base, User
from schemas import UserResponse, UserLogin, Token, UserCreateAdmin, PasswordChange, UserCreateResponse

# Create tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vegan Buddies API", version="1.0.0")

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

# Add general exception handler to prevent 500 errors from breaking CORS
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Add simple request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# CORS middleware - temporarily permissive for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=False,  # Set to False when using "*" origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Validate environment variables
def validate_environment():
    """Validate that required environment variables are properly configured."""
    errors = []
    
    # Check SECRET_KEY
    if SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY is not configured. Please run 'python setup_env.py' to generate secure credentials.")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url or "postgres:postgres" in database_url:
        errors.append("DATABASE_URL is not properly configured. Please run 'python setup_env.py' to generate secure credentials.")
    
    if errors:
        logger.error("Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Environment not configured",
                "message": "Please run 'python setup_env.py' to configure the application",
                "details": errors
            }
        )

# Validate environment on startup
try:
    validate_environment()
    logger.info("Environment validation passed")
except HTTPException:
    logger.error("Environment validation failed - application may not work correctly")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_secure_password(length=12):
    """Generate a secure random password with mixed case, numbers, and symbols."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {user_credentials.username}")
    try:
        user = db.query(User).filter(User.username == user_credentials.username).first()
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            logger.warning(f"Login failed for username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Login successful for username: {user_credentials.username}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login service temporarily unavailable"
        )

@app.get("/users", response_model=List[UserResponse])
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/users", response_model=UserCreateResponse)
def create_user(user: UserCreateAdmin, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create an admin user with auto-generated password"""
    logger.info(f"Creating admin user: {user.username}, {user.email}")
    logger.info(f"Current user: {current_user.username}")
    
    try:
        # Check if user already exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Generate secure password
        generated_password = generate_secure_password()
        hashed_password = get_password_hash(generated_password)
        
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=True,
            password_change_required=True  # Force password change on first login
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Admin user created successfully: {db_user.username}")
        return UserCreateResponse(user=db_user, generated_password=generated_password)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating admin user: {str(e)}")

@app.post("/change-password", response_model=UserResponse)
def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change user password"""
    logger.info(f"Password change attempt for user: {current_user.username}")
    
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            logger.warning(f"Invalid current password for user: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # Update user password and mark password change as not required
        current_user.hashed_password = new_hashed_password
        current_user.password_change_required = False
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Password changed successfully for user: {current_user.username}")
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error changing password")

@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    try:
        # Ensure password_change_required field exists (for backward compatibility)
        if not hasattr(current_user, 'password_change_required'):
            current_user.password_change_required = False
        return current_user
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )

@app.get("/health")
def health_check():
    """Health check endpoint that also validates environment and admin users."""
    try:
        # Check environment
        validate_environment()
        
        # Check if admin users exist
        db = next(get_db())
        admin_count = db.query(User).filter(User.is_admin == True).count()
        
        return {
            "status": "healthy",
            "environment": "configured",
            "admin_users": admin_count,
            "message": "Vegan Buddies API is running!"
        }
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "environment": "not_configured",
            "admin_users": 0,
            "error": e.detail
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "environment": "unknown",
            "admin_users": 0,
            "error": "Internal server error"
        }

@app.get("/")
def read_root():
    return {"message": "Vegan Buddies API is running!"}
