"""
Authentication and Access Control System
FIX: No Authentication or Access Control in Trading Bot
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config import get_settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class UserRole(str, Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class Permission(str, Enum):
    """Granular permissions"""
    # Trading permissions
    EXECUTE_TRADES = "execute_trades"
    VIEW_TRADES = "view_trades"
    MODIFY_STRATEGY = "modify_strategy"

    # System permissions
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    MANAGE_CONFIG = "manage_config"

    # Data permissions
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    EXPORT_DATA = "export_data"

    # Bot control
    START_BOT = "start_bot"
    STOP_BOT = "stop_bot"
    CONFIGURE_BOT = "configure_bot"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [p for p in Permission],  # All permissions
    UserRole.TRADER: [
        Permission.EXECUTE_TRADES,
        Permission.VIEW_TRADES,
        Permission.MODIFY_STRATEGY,
        Permission.VIEW_LOGS,
        Permission.START_BOT,
        Permission.STOP_BOT,
        Permission.CONFIGURE_BOT,
    ],
    UserRole.VIEWER: [
        Permission.VIEW_TRADES,
        Permission.VIEW_LOGS,
    ],
    UserRole.AUDITOR: [
        Permission.VIEW_TRADES,
        Permission.VIEW_LOGS,
        Permission.ACCESS_SENSITIVE_DATA,
        Permission.EXPORT_DATA,
    ],
}


class User(BaseModel):
    """User model"""
    username: str
    email: str
    role: UserRole
    disabled: bool = False
    api_key: Optional[str] = None


class TokenData(BaseModel):
    """JWT token data"""
    username: str
    role: UserRole
    permissions: List[str]
    exp: datetime


class AuthService:
    """Authentication service"""

    def __init__(self):
        self.settings = get_settings()
        self._users_db: Dict[str, Dict] = {}  # In production, use a real database
        self._api_keys: Dict[str, str] = {}  # API key -> username mapping

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        """Create a new user"""
        if username in self._users_db:
            raise ValueError(f"User {username} already exists")

        hashed_password = self.hash_password(password)
        api_key = self.generate_api_key()

        self._users_db[username] = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "role": role,
            "disabled": False,
            "api_key": api_key,
            "created_at": datetime.utcnow(),
            "last_login": None,
        }

        self._api_keys[api_key] = username

        return User(username=username, email=email, role=role, api_key=api_key)

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"sk_{secrets.token_urlsafe(32)}"

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user_data = self._users_db.get(username)
        if not user_data:
            return None

        if not self.verify_password(password, user_data["hashed_password"]):
            return None

        if user_data["disabled"]:
            return None

        # Update last login
        user_data["last_login"] = datetime.utcnow()

        return User(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            disabled=user_data["disabled"],
            api_key=user_data["api_key"],
        )

    def authenticate_by_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate a user by API key"""
        username = self._api_keys.get(api_key)
        if not username:
            return None

        user_data = self._users_db.get(username)
        if not user_data or user_data["disabled"]:
            return None

        return User(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            disabled=user_data["disabled"],
            api_key=user_data["api_key"],
        )

    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        permissions = [p.value for p in ROLE_PERMISSIONS[user.role]]

        expire = datetime.utcnow() + timedelta(hours=self.settings.jwt_expiration_hours)

        token_data = {
            "sub": user.username,
            "role": user.role.value,
            "permissions": permissions,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(token_data, self.settings.jwt_secret_key, algorithm="HS256")
        return token

    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.settings.jwt_secret_key, algorithms=["HS256"])

            username = payload.get("sub")
            role = payload.get("role")
            permissions = payload.get("permissions", [])
            exp = datetime.fromtimestamp(payload.get("exp"))

            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            return TokenData(
                username=username,
                role=UserRole(role),
                permissions=permissions,
                exp=exp,
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        return permission in ROLE_PERMISSIONS[user.role]

    def check_ip_whitelist(self, request: Request) -> bool:
        """
        Check if request IP is whitelisted
        FIX: Additional security layer
        """
        if not self.settings.enable_ip_whitelist:
            return True

        client_ip = request.client.host
        allowed_ips = self.settings.get_allowed_ips()

        # Check exact match
        if client_ip in allowed_ips:
            return True

        # Check CIDR ranges (simplified - use ipaddress module for production)
        for allowed_ip in allowed_ips:
            if "/" in allowed_ip:  # CIDR notation
                # In production, use ipaddress.ip_network for proper CIDR matching
                network = allowed_ip.split("/")[0]
                if client_ip.startswith(network.rsplit(".", 1)[0]):
                    return True

        return False


# Global auth service instance
auth_service = AuthService()


# Dependency for route protection
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    request: Request = None,
) -> User:
    """
    Get current authenticated user
    Used as FastAPI dependency for protected routes
    """

    # Check IP whitelist first
    if request and not auth_service.check_ip_whitelist(request):
        raise HTTPException(
            status_code=403,
            detail="Access denied: IP address not whitelisted",
        )

    token = credentials.credentials

    # Try JWT token first
    try:
        token_data = auth_service.verify_token(token)
        user_data = auth_service._users_db.get(token_data.username)

        if not user_data or user_data["disabled"]:
            raise HTTPException(status_code=401, detail="User not found or disabled")

        return User(
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            disabled=user_data["disabled"],
            api_key=user_data["api_key"],
        )

    except HTTPException:
        # Try API key authentication
        user = auth_service.authenticate_by_api_key(token)
        if user:
            return user

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )


def require_permission(permission: Permission):
    """
    Decorator factory for permission-based access control
    Usage: @require_permission(Permission.EXECUTE_TRADES)
    """

    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not auth_service.has_permission(user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission.value} required",
            )
        return user

    return permission_checker


def require_role(role: UserRole):
    """
    Decorator factory for role-based access control
    Usage: @require_role(UserRole.ADMIN)
    """

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != role and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: {role.value} role required",
            )
        return user

    return role_checker


# Initialize default admin user (for development)
def initialize_default_users():
    """Create default users for initial setup"""
    try:
        # Create admin user
        admin = auth_service.create_user(
            username="admin",
            email="admin@example.com",
            password="Admin123!Change",  # MUST be changed in production
            role=UserRole.ADMIN,
        )
        print(f"Created admin user. API Key: {admin.api_key}")

        # Create trader user
        trader = auth_service.create_user(
            username="trader",
            email="trader@example.com",
            password="Trader123!Change",
            role=UserRole.TRADER,
        )
        print(f"Created trader user. API Key: {trader.api_key}")

    except ValueError as e:
        print(f"Users already exist: {e}")
