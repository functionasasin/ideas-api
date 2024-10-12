from fastapi.responses import JSONResponse
from typing import TypeVar, Optional
from src.models import SuccessResponse, ErrorResponse
from src.core import HTTPStatusCodes

T = TypeVar('T')

def create_success_response(
    data: Optional[T] = None,
    message: str = "Operation successful",
    status_code: int = HTTPStatusCodes.OK.value,
) -> JSONResponse:
    response = SuccessResponse[T](message=message, data=data)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )

def create_error_response(
    error_code,
    message="An error occurred",
    details: Optional[T] = None,
    status_code: int = HTTPStatusCodes.BAD_REQUEST.value,
) -> JSONResponse:
    response = ErrorResponse[T](error=error_code, message=message, details=details)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )