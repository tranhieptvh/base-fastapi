from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.core.response import ErrorResponse

class AppException(HTTPException):
    """
    Base exception class for application errors.
    Uses consistent format with ErrorResponse.
    """
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_response = ErrorResponse(
            error={
                "code": error_code,
                "message": message,
                "details": details or {}
            }
        )
        super().__init__(status_code=status_code, detail=error_response.dict())

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class NotFoundException(AppException):
    """
    Exception for resource not found errors.
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message
        )

class DuplicateEntryException(AppException):
    """
    Exception for duplicate entry errors.
    """
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="DUPLICATE_ENTRY",
            message=f"{field} already exists",
            details={"field": field, "value": value}
        )