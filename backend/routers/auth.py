from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import logging

from models.users import (
    User, UserCreate, UserInDB, LoginRequest, Token, 
    PasswordResetRequest, PasswordReset, UserRole
)
from models.responses import APIResponse
from services.auth_service import (
    authenticate_user, create_access_token, create_refresh_token,
    get_current_user, create_user, get_password_hash
)
from config.database import get_database
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=APIResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Create user in database
        new_user = await create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )

        logger.info(f"New user registered: {user_data.username}")

        return APIResponse(
            success=True,
            message="User registered successfully",
            data={
                "user_id": new_user.id,
                "username": new_user.username,
                "role": new_user.role
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Authenticate user and return tokens"""
    try:
        # Authenticate user
        user = await authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            },
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            }
        )

        # Update last login
        db = await get_database()
        await db.users.update_one(
            {"username": user.username},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        logger.info(f"User logged in: {user.username}")

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token"""
    try:
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": current_user.username,
                "user_id": current_user.id,
                "role": current_user.role
            },
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(
            data={
                "sub": current_user.username,
                "user_id": current_user.id,
                "role": current_user.role
            }
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.post("/demo/create-demo-users")
async def create_demo_users():
    """Create demo users for testing (development only)"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user creation only available in development"
        )

    try:
        db = await get_database()

        # Demo users
        demo_users = [
            {
                "id": "user_demo",
                "username": "demo",
                "email": "demo@smartswapml.com",
                "hashed_password": get_password_hash("demo123"),
                "role": UserRole.USER,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "full_name": "Demo User",
                "last_login": None
            },
            {
                "id": "user_admin",
                "username": "admin",
                "email": "admin@smartswapml.com",
                "hashed_password": get_password_hash("admin123"),
                "role": UserRole.ADMIN,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "full_name": "Admin User",
                "last_login": None
            },
            {
                "id": "user_operator",
                "username": "operator",
                "email": "operator@smartswapml.com",
                "hashed_password": get_password_hash("operator123"),
                "role": UserRole.OPERATOR,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "full_name": "Operator User",
                "last_login": None
            }
        ]

        created_users = []
        for user_data in demo_users:
            # Check if user already exists
            existing = await db.users.find_one({"username": user_data["username"]})
            if not existing:
                await db.users.insert_one(user_data)
                created_users.append(user_data["username"])

        return APIResponse(
            success=True,
            message="Demo users created successfully",
            data={
                "created_users": created_users,
                "credentials": [
                    {"username": "demo", "password": "demo123", "role": "user"},
                    {"username": "admin", "password": "admin123", "role": "admin"},
                    {"username": "operator", "password": "operator123", "role": "operator"}
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error creating demo users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating demo users: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )

@router.post("/password-reset-request")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset (placeholder)"""
    # In production, this would send an email with reset token
    return APIResponse(
        success=True,
        message="Password reset email sent (if email exists)",
        data={"note": "This is a placeholder endpoint"}
    )

@router.post("/password-reset")
async def reset_password(reset_data: PasswordReset):
    """Reset password with token (placeholder)"""
    # In production, this would validate token and reset password
    return APIResponse(
        success=True,
        message="Password reset successfully",
        data={"note": "This is a placeholder endpoint"}
    )
