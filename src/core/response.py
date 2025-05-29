from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class BaseResponse(BaseModel):
    status: str
    message: str
    
    model_config = ConfigDict(from_attributes=True)

class SuccessResponse(BaseResponse, Generic[T]):
    status: str = "success"
    message: str = "Success"
    data: Optional[T] = None

class ErrorResponse(BaseResponse):
    status: str = "error"
    message: str = "Error"
    errors: Dict[str, Any] = {}

def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    return SuccessResponse(data=data, message=message).model_dump()

def error_response(message: str = "Error", errors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ErrorResponse(message=message, errors=errors or {}).model_dump() 