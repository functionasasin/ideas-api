from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    status: str = "Success"
    message: str
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    status: str = "Error"
    error: str
    message: str
    details: Optional[Any] = None