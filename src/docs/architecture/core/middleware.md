# Middleware Architecture

## Overview

The project includes several middleware components to enhance security, logging, and error handling. These middleware components are designed to handle cross-cutting concerns and provide consistent behavior across the application.

## Available Middleware

### 1. Request Logging Middleware
- **Purpose**: Logs all incoming requests and their processing time
- **Location**: `src/core/middleware.py`
- **Features**:
  - Logs request method and path
  - Logs response status code
  - Measures and logs processing time
  - Error logging for failed requests
- **Usage**: Applied globally via `setup_middleware`

### 2. CORS Middleware
- **Purpose**: Handles Cross-Origin Resource Sharing
- **Location**: `src/core/middleware.py`
- **Features**:
  - Configurable allowed origins from settings
  - Allows all methods and headers
  - Exposes all response headers
  - Preflight request caching (1 hour)
  - Credentials support
- **Usage**: Applied via `setup_cors_middleware`

### 3. Exception Handlers
- **Purpose**: Global exception handling and standardized error responses
- **Location**: `src/core/middleware.py`
- **Features**:
  - Custom validation error handler
  - Custom application exception handler
  - Standardized error response format
  - Detailed error messages
  - HTTP status code mapping

#### Validation Error Response Format
```json
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
```

## Implementation Details

### 1. Middleware Setup
```python
def setup_middleware(app):
    # Add request logging middleware
    app.middleware("http")(log_request_middleware)
    
    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    
    # Setup CORS
    setup_cors_middleware(app)
```

### 2. CORS Configuration
```python
def setup_cors_middleware(app):
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
```

### 3. Request Logging
```python
async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.2f}s"
        )
        return response
    except Exception as e:
        logger.error(
            f"Error: {request.method} {request.url.path} "
            f"Error: {str(e)}"
        )
        raise
```

## Best Practices

### 1. Middleware Order
- Request logging middleware should be first to capture all requests
- CORS middleware should be early to handle preflight requests
- Exception handlers should be last to catch all errors

### 2. Performance Considerations
- Request logging is lightweight and async
- CORS preflight caching reduces unnecessary requests
- Exception handlers provide detailed error information

### 3. Security Considerations
- CORS is configured based on environment settings
- All exceptions are properly logged
- Validation errors provide clear feedback

### 4. Error Handling
- Consistent error response format
- Detailed validation error messages
- Proper HTTP status codes
- Comprehensive error logging

## Usage in Main Application

The middleware is set up in `main.py` with a single call:

```python
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# Setup all middleware
setup_middleware(app)
```

## Troubleshooting

### 1. Common Issues
- CORS errors: Check BACKEND_CORS_ORIGINS setting
- Validation errors: Review request payload format
- Performance issues: Check request logs for slow endpoints

### 2. Debugging Tips
- Review application logs for request/response details
- Check CORS configuration in settings
- Verify exception handler responses

### 3. Performance Optimization
- Monitor request processing times in logs
- Adjust CORS preflight cache duration if needed
- Review and optimize slow endpoints 