from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.core.response import error_response

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    Transforms validation errors into standardized format.
    
    Example response:
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
    """
    errors = []
    for error in exc.errors():
        # Extract field name from loc (remove 'body' prefix if present)
        field = error["loc"][-1] if error["loc"][-1] != "body" else error["loc"][-2]
        
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    response = error_response(
        message="Validation error",
        errors={
            "fields": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    ) 