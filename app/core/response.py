from typing import TypeVar, Generic, Optional, Any, Dict, List
from pydantic import BaseModel

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    status: str = "error"
    error: Dict[str, Any]

def success_response(data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
    return {
        "status": "success",
        "data": data,
        "message": message
    } 