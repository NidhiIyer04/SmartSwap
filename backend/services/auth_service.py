import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.users import User, UserInDB, TokenData, UserRole
from config.settings import settings
from config.database import get_database

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception

        token_data = TokenData(username=username, user_id=user_id, role=role)
        return token_data

    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        raise credentials_exception

async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get user by username from database"""
    try:
        db = await get_database()
        user_doc = await db.users.find_one({"username": username})
        if user_doc:
            return UserInDB(**user_doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None

async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user credentials"""
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token_data = await verify_token(credentials.credentials)
    user = await get_user_by_username(token_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    return User(**user.dict())

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_roles(allowed_roles: list):
    """Decorator factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# Role-based dependencies
require_admin = require_roles([UserRole.ADMIN])
require_operator = require_roles([UserRole.ADMIN, UserRole.OPERATOR])
require_user = require_roles([UserRole.ADMIN, UserRole.OPERATOR, UserRole.USER])

async def create_user(username: str, email: str, password: str, role: UserRole = UserRole.USER) -> UserInDB:
    """Create new user"""
    db = await get_database()

    # Check if user exists
    existing_user = await db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    hashed_password = get_password_hash(password)
    user_data = {
        "id": f"user_{int(datetime.utcnow().timestamp())}",
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "full_name": None,
        "last_login": None
    }

    await db.users.insert_one(user_data)
    return UserInDB(**user_data)
