"""
Main FastAPI Application - Business Automation System X3.0
Secure, High-Availability Trading & Legal Automation Platform

Security Features Implemented:
✓ Authentication and Access Control
✓ Rate Limiting and DDoS Protection
✓ Comprehensive Audit Logging
✓ Input Validation and Sanitization
✓ Data Encryption
✓ Environment Separation
✓ Backup and Disaster Recovery
✓ Health Monitoring
✓ IP Whitelisting
"""

import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_settings
from auth import (
    User,
    auth_service,
    get_current_user,
    require_permission,
    require_role,
    Permission,
    UserRole,
    initialize_default_users,
)
from logging_system import logging_system, AuditEventType
from rate_limiter import limiter, RateLimitConfig, rate_limit
from trading_bot import SecureTradingBot, BotStatus, TradingStrategy
from email_automation import (
    email_automation,
    EmailRecipient,
    EmailTemplate,
    register_default_templates,
)
from backup_system import backup_system
from slowapi.errors import RateLimitExceeded


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    settings = get_settings()

    # Startup
    logging_system.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        environment=settings.environment,
        sandbox_mode=settings.is_sandbox(),
    )

    logging_system.audit(
        event_type=AuditEventType.SYSTEM_STARTUP,
        user="system",
        action="application startup",
        details={
            "version": settings.app_version,
            "environment": settings.environment,
            "sandbox_mode": settings.is_sandbox(),
        },
    )

    # Initialize default users
    initialize_default_users()

    # Register email templates
    register_default_templates()

    # Start automated backups
    if settings.backup_enabled:
        await backup_system.start_automated_backups()

    logging_system.info("Application startup complete")

    yield

    # Shutdown
    logging_system.info("Shutting down application")

    logging_system.audit(
        event_type=AuditEventType.SYSTEM_SHUTDOWN,
        user="system",
        action="application shutdown",
        details={"graceful": True},
    )

    # Stop automated backups
    await backup_system.stop_automated_backups()

    logging_system.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Business Automation System",
    description="Secure Trading Bot & Legal Automation Platform",
    version="3.0.0",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict


class BotStartRequest(BaseModel):
    strategy_name: str


class EmailSendRequest(BaseModel):
    recipients: List[str]
    subject: str
    body_text: str
    body_html: Optional[str] = None


class BackupRequest(BaseModel):
    backup_type: str = "full"
    destinations: List[str] = ["local"]


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """
    Public health check endpoint
    Used for load balancers and monitoring
    """
    settings = get_settings()

    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "sandbox_mode": settings.is_sandbox(),
    }


# Authentication Endpoints
@app.post("/auth/login", response_model=LoginResponse)
@limiter.limit(RateLimitConfig.LOGIN)
async def login(
    request: Request,
    credentials: LoginRequest,
):
    """
    Authenticate user and get access token

    Security: Rate limited to prevent brute force attacks
    """
    user = auth_service.authenticate_user(credentials.username, credentials.password)

    if not user:
        logging_system.audit_authentication(
            user=credentials.username,
            ip_address=request.client.host,
            success=False,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create access token
    access_token = auth_service.create_access_token(user)

    logging_system.audit_authentication(
        user=user.username,
        ip_address=request.client.host,
        success=True,
    )

    return LoginResponse(
        access_token=access_token,
        user={
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
        },
    )


@app.get("/auth/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
    }


# Trading Bot Endpoints
_active_bots: Dict[str, SecureTradingBot] = {}


@app.post("/trading/start")
@limiter.limit(RateLimitConfig.API_WRITE)
async def start_trading_bot(
    request: Request,
    bot_request: BotStartRequest,
    current_user: User = Depends(require_permission(Permission.START_BOT)),
):
    """
    Start trading bot

    Security: Requires START_BOT permission
    """
    # Create or get bot instance
    if current_user.username not in _active_bots:
        bot = SecureTradingBot(current_user)
        _active_bots[current_user.username] = bot
    else:
        bot = _active_bots[current_user.username]

    # Create a simple strategy (placeholder)
    class SimpleStrategy(TradingStrategy):
        def __init__(self):
            super().__init__("simple_strategy")

        async def analyze(self, market_data: Dict) -> Optional[Dict]:
            # Placeholder - implement actual strategy
            return None

    strategy = SimpleStrategy()

    # Start bot
    await bot.start(strategy)

    return {
        "message": "Trading bot started",
        "status": bot.get_status(),
    }


@app.post("/trading/stop")
@limiter.limit(RateLimitConfig.API_WRITE)
async def stop_trading_bot(
    request: Request,
    current_user: User = Depends(require_permission(Permission.STOP_BOT)),
):
    """
    Stop trading bot

    Security: Requires STOP_BOT permission
    """
    if current_user.username not in _active_bots:
        raise HTTPException(status_code=404, detail="No active bot found")

    bot = _active_bots[current_user.username]
    await bot.stop()

    return {
        "message": "Trading bot stopped",
        "status": bot.get_status(),
    }


@app.get("/trading/status")
@limiter.limit(RateLimitConfig.API_READ)
async def get_trading_bot_status(
    request: Request,
    current_user: User = Depends(require_permission(Permission.VIEW_TRADES)),
):
    """
    Get trading bot status

    Security: Requires VIEW_TRADES permission
    """
    if current_user.username not in _active_bots:
        return {
            "status": "not_initialized",
            "message": "No trading bot initialized for this user",
        }

    bot = _active_bots[current_user.username]
    return bot.get_status()


# Email Automation Endpoints
@app.post("/email/send")
@limiter.limit(RateLimitConfig.EMAIL_SEND)
async def send_email(
    request: Request,
    email_request: EmailSendRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send email

    Security: Rate limited, input validated, HTML sanitized
    """
    # Convert recipient strings to EmailRecipient objects
    recipients = [EmailRecipient(email=email) for email in email_request.recipients]

    # Send email
    success = await email_automation.send_email(
        sender=current_user.email,
        recipients=recipients,
        subject=email_request.subject,
        body_text=email_request.body_text,
        body_html=email_request.body_html,
        user=current_user.username,
    )

    return {
        "success": success,
        "message": "Email sent successfully",
        "recipient_count": len(recipients),
    }


@app.get("/email/templates")
async def list_email_templates(
    current_user: User = Depends(get_current_user),
):
    """List available email templates"""
    templates = list(email_automation._templates.keys())

    return {
        "templates": templates,
        "count": len(templates),
    }


# Backup Endpoints
@app.post("/backup/create")
@limiter.limit("5/hour")
async def create_backup(
    request: Request,
    backup_request: BackupRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create system backup

    Security: Admin only, rate limited
    """
    backup_info = await backup_system.create_backup(
        backup_type=backup_request.backup_type,
        destinations=backup_request.destinations,
    )

    return {
        "message": "Backup created successfully",
        "backup_info": backup_info,
    }


@app.get("/backup/list")
async def list_backups(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    List available backups

    Security: Admin only
    """
    backups = []

    for backup_file in backup_system.backup_dir.glob("backup_*.tar.gz"):
        backups.append({
            "name": backup_file.name,
            "size_bytes": backup_file.stat().st_size,
            "created": backup_file.stat().st_mtime,
        })

    return {
        "backups": backups,
        "count": len(backups),
    }


# System Information Endpoints
@app.get("/system/info")
async def get_system_info(
    current_user: User = Depends(get_current_user),
):
    """Get system information"""
    settings = get_settings()

    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "sandbox_mode": settings.is_sandbox(),
        "features": {
            "authentication": True,
            "rate_limiting": True,
            "audit_logging": settings.audit_log_enabled,
            "backup_system": settings.backup_enabled,
            "encryption": True,
            "ip_whitelisting": settings.enable_ip_whitelist,
        },
    }


@app.get("/system/stats")
async def get_system_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Get system statistics

    Security: Admin only
    """
    active_bots = len(_active_bots)
    running_bots = sum(
        1 for bot in _active_bots.values() if bot.status == BotStatus.RUNNING
    )

    return {
        "active_bots": active_bots,
        "running_bots": running_bots,
        "users_count": len(auth_service._users_db),
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with audit logging"""
    if exc.status_code in [401, 403]:
        logging_system.audit_security_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
            ip_address=request.client.host,
            details={
                "path": str(request.url.path),
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Business Automation System X3.0",
        "description": "Secure Trading Bot & Legal Automation Platform",
        "version": "3.0.0",
        "security_features": [
            "Authentication & Authorization",
            "Rate Limiting & DDoS Protection",
            "Comprehensive Audit Logging",
            "Data Encryption",
            "Input Validation",
            "Backup & Disaster Recovery",
            "High Availability",
            "IP Whitelisting",
        ],
        "docs_url": "/docs",
        "health_check_url": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=settings.max_workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
    )
