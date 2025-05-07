from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any

class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None
    ):
        self.error_code = error_code
        self.details = details or []
        super().__init__(status_code=status_code, detail={
            "status": "error",
            "error": {
                "code": error_code,
                "message": message,
                "details": self.details
            }
        })

class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class DuplicateEntryException(AppException):
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="DUPLICATE_ENTRY",
            message=f"{field} already exists",
            details=[{"field": field, "message": f"{field} already exists"}]
        )