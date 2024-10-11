from pydantic import BaseModel
from typing import Any, Optional

class SuccessResponse(BaseModel):
    status: str = "Success"
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    status: str = "Error"
    error: str
    message: str
    details: Optional[Any] = None