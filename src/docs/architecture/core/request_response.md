# Request & Response Handling

## Overview

The project implements a standardized approach to request validation and response formatting. This ensures consistent behavior across all API endpoints and provides clear error messages for clients.

## Request Validation

### 1. Pydantic Models
- Automatic type conversion
- Custom validators for complex rules
- Detailed error messages for invalid inputs
- Nested model validation

### 2. Validation Features
- Type checking
- Required field validation
- Custom validation rules
- Nested object validation
- List validation
- Enum validation

### 3. Example Validation
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)
    role_id: int

    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
```

## Response Models

### 1. Base Response
```python
class BaseResponse(BaseModel):
    status: str
    message: str
```

### 2. Success Response
```python
class SuccessResponse(BaseResponse, Generic[T]):
    status: str = "success"
    message: str = "Success"
    data: Optional[T] = None
```

### 3. Error Response
```python
class ErrorResponse(BaseResponse):
    status: str = "error"
    message: str = "Error"
    errors: Dict[str, Any] = {}
```

## Response Format

### 1. Success Response Format
```json
{
    "status": "success",
    "message": "Success",
    "data": {
        // Response data here
    }
}
```

### 2. Error Response Format
```json
{
    "status": "error",
    "message": "Error message",
    "errors": {
        // Additional error details
    }
}
```

## Helper Functions

### 1. Success Response Helper
```python
def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """
    Creates a standardized success response
    
    Args:
        data: Optional response data
        message: Optional success message
        
    Returns:
        Dictionary containing success response
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }
```

### 2. Error Response Helper
```python
def error_response(message: str = "Error", errors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Creates a standardized error response
    
    Args:
        message: Error message
        errors: Optional error details
        
    Returns:
        Dictionary containing error response
    """
    return {
        "status": "error",
        "message": message,
        "errors": errors or {}
    }
```

## Usage Examples

### 1. Success Response
```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(data=user)
```

### 2. Error Response
```python
@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = create_user_in_db(db, user)
        return success_response(data=db_user)
    except ValueError as e:
        return error_response(message=str(e))
```

## Best Practices

### 1. Request Validation
- Use Pydantic models for all requests
- Implement custom validators when needed
- Provide clear error messages
- Validate nested objects properly

### 2. Response Formatting
- Use consistent response structure
- Include appropriate status codes
- Provide meaningful messages
- Handle all error cases

### 3. Error Handling
- Use appropriate HTTP status codes
- Provide detailed error messages
- Include error context when helpful
- Log all errors appropriately

### 4. Performance
- Validate requests early
- Use efficient data structures
- Minimize response size
- Cache when appropriate

## Troubleshooting

### 1. Common Issues
- Validation errors
- Type conversion problems
- Missing required fields
- Invalid data formats

### 2. Debugging Tips
- Check request data
- Verify response format
- Review error messages
- Test edge cases

### 3. Performance Optimization
- Use appropriate data types
- Minimize validation complexity
- Optimize response size
- Cache common responses 