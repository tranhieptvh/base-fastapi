# Logging Architecture

## Overview

The application implements a comprehensive logging system similar to Laravel's logging functionality. The system provides structured logging with daily rotation, file size limits, and detailed context information.

## Configuration

### 1. Log Directory Structure
```
logs/
├── YYYY-MM-DD.log        # Current day's log file
├── YYYY-MM-DD.log.1      # Previous day's log file
├── YYYY-MM-DD.log.2      # Two days ago log file
└── ...
```

### 2. Log File Settings
- **Location**: `logs/` directory in project root
- **Naming**: `YYYY-MM-DD.log` format
- **Rotation**: 
  - Size limit: 10MB per file
  - Maximum files: 10 backup files
  - Automatic rotation when size limit is reached

### 3. Log Format
```
[timestamp] LEVEL: message [in file:line_number]
```
Example:
```
[2024-03-21 10:30:45,123] INFO: Request: GET /api/users [in /app/src/core/middleware.py:16]
```

## Implementation

### 1. Core Logging Module (`src/core/logging.py`)
```python
def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Formatter configuration
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # File handler with rotation
    log_file = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
```

### 2. Request Logging Middleware (`src/core/middleware.py`)
```python
async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response with timing
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

## Usage

### 1. Basic Logging
```python
from src.core.logging import logger

# Different log levels
logger.info("Information message")
logger.error("Error message")
logger.warning("Warning message")
logger.debug("Debug message")
```

### 2. Logging with Context
```python
# Log with additional context
logger.info(f"Processing user {user_id} with data: {data}")

# Log exceptions
try:
    # Some code
except Exception as e:
    logger.error(f"Failed to process request: {str(e)}")
```

## Log Levels

1. **INFO** (Default)
   - General operational messages
   - Request/Response logging
   - Successful operations

2. **ERROR**
   - Application errors
   - Failed operations
   - Exception details

3. **WARNING**
   - Potential issues
   - Deprecated features
   - Non-critical errors

4. **DEBUG**
   - Detailed debugging information
   - Variable values
   - Execution flow

## Best Practices

1. **Log Levels**
   - Use appropriate log levels
   - Don't log sensitive information
   - Include relevant context

2. **Performance**
   - Keep log messages concise
   - Use string formatting carefully
   - Avoid logging large objects

3. **Maintenance**
   - Regular log rotation
   - Monitor log file sizes
   - Archive old logs

4. **Security**
   - Don't log sensitive data
   - Sanitize log messages
   - Control log file permissions

## Monitoring and Maintenance

1. **Log Rotation**
   - Automatic rotation at 10MB
   - Keeps last 10 files
   - Daily new log file

2. **Log Analysis**
   - Monitor error rates
   - Track response times
   - Identify patterns

3. **Cleanup**
   - Automatic cleanup of old logs
   - Manual cleanup if needed
   - Archive important logs

## Integration with Other Systems

1. **Error Tracking**
   - Log exceptions for error tracking
   - Include stack traces
   - Add correlation IDs

2. **Performance Monitoring**
   - Log request timing
   - Track slow requests
   - Monitor resource usage

3. **Security Monitoring**
   - Log security events
   - Track failed attempts
   - Monitor suspicious activities 