from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        # Convert Pydantic error format to our format
        field = ".".join(str(x) for x in error["loc"])
        if field.startswith("body."):
            field = field[5:]  # Remove "body." prefix
        details.append({
            "field": field,
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": details
            }
        }
    ) 