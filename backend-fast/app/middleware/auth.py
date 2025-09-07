from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from app.core.security import verify_token
import logging

logger = logging.getLogger(__name__)


async def auth_middleware(request: Request, call_next):
    """Middleware to log authentication attempts and add user context"""
    
    # Skip auth middleware for public endpoints
    public_paths = ["/", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/login"]
    if request.url.path in public_paths:
        response = await call_next(request)
        return response
    
    # Extract token from Authorization header
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() == "bearer" and token:
            try:
                username = verify_token(token)
                # Add username to request state for logging
                request.state.username = username
                logger.info(f"Authenticated request from user: {username}")
            except HTTPException:
                logger.warning(f"Invalid token in request to {request.url.path}")
    
    response = await call_next(request)
    return response
