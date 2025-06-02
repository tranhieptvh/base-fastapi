from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.core.response import error_response
from src.core.exceptions import AppException
from src.core.logging import logger
import time

async def log_request_middleware(request: Request, call_next):
    """
    Middleware to log all incoming requests
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.2f}s"
        )
        
        return response
    except Exception as e:
        # Log error
        logger.error(
            f"Error: {request.method} {request.url.path} "
            f"Error: {str(e)}"
        )
        raise

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    Transforms validation errors into standardized format.
    
    Example response:
    {
        "status": "error",
        "message": "Validation error",
        "errors": {
            "fields": [
                {
                    "field": "email",
                    "message": "invalid email format",
                    "type": "value_error.email"
                }
            ]
        }
    }
    """
    errors = []
    for error in exc.errors():
        # Extract field name from loc (remove 'body' prefix if present)
        field = error["loc"][-1] if error["loc"][-1] != "body" else error["loc"][-2]
        
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    response = error_response(
        message="Validation error",
        errors={
            "fields": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )

async def app_exception_handler(request: Request, exc: AppException):
    """
    Custom handler for AppException.
    Returns error response in standardized format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

def setup_cors_middleware(app):
    """
    Setup CORS middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    from fastapi.middleware.cors import CORSMiddleware
    from src.core.config import settings
    
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=3600,  # Cache preflight requests for 1 hour
        )

def setup_middleware(app):
    """
    Setup all middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Add request logging middleware
    app.middleware("http")(log_request_middleware)
    
    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    
    # Setup CORS
    setup_cors_middleware(app) 