from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class BaseResponse(BaseModel):
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class SuccessResponse(BaseResponse, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: str = "Operation completed successfully"

class ErrorResponse(BaseResponse):
    status: str = "error"
    error: Dict[str, Any]

# For backward compatibility
def success_response(data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
    return SuccessResponse(data=data, message=message).dict() 