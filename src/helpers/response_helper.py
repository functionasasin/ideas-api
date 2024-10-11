from fastapi.responses import JSONResponse
from src.models import SuccessResponse, ErrorResponse
from src.core import HTTPStatusCodes

def create_success_response(
    data=None,
    message="Operation successful",
    status_code=HTTPStatusCodes.OK.value,
):
    response = SuccessResponse(message=message, data=data)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )

def create_error_response(
    error_code,
    message="An error occurred",
    details=None,
    status_code=HTTPStatusCodes.BAD_REQUEST.value,
):
    response = ErrorResponse(error=error_code, message=message, details=details)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )