from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from src.core.response import error_response

class AppException(HTTPException):
    """
    Base exception class for application errors.
    Uses consistent format with ErrorResponse.
    """
    def __init__(
        self,
        status_code: int,
        message: str,
        errors: Optional[Dict[str, Any]] = None
    ):
        error_data = error_response(
            message=message,
            errors=errors or {}
        )
        super().__init__(status_code=status_code, detail=error_data)

class ValidationException(AppException):
    """
    Base class for validation errors.
    """
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            errors=errors or {}
        )

class DuplicateEntryException(ValidationException):
    """
    Exception for duplicate entry errors.
    """
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"{field} already exists",
            errors={
                "fields": [
                    {
                        "type": "duplicate_entry",
                        "field": field,
                        "value": value
                    }
                ]
            }
        )

class NotFoundException(AppException):
    """
    Exception for resource not found errors.
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            errors={"type": "not_found"}
        )

class UnauthorizedException(AppException):
    """
    Exception for unauthorized access errors.
    """
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            errors={"type": "unauthorized"}
        )

class BadRequestException(AppException):
    """
    Exception for bad request errors.
    """
    def __init__(self, message: str = "Bad Request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            errors={"type": "bad_request"}
        )