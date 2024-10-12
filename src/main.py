from fastapi import FastAPI, Request
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler as default_http_exception_handler
from contextlib import asynccontextmanager
from src.routes import idea_routes, admin_routes
from src.config import MONGO_URI
from src.helpers import create_error_response
from src.core import InvalidCredentialsException, ResourceNotFoundException, UserAlreadyExistsException, UnauthorizedAccessException, DuplicateUpvoteException, EmptyContentException, InvalidIDException, ErrorCodes, HTTPStatusCodes
from src.exception_handlers import invalid_credentials_exception_handler, resource_not_found_exception_handler, user_already_exists_exception_handler, unauthorized_access_exception_handler, duplicate_upvote_exception_handler, empty_content_exception_handler,invalid_id_exception_handler
from fastapi.exceptions import RequestValidationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["idea_db"]  # Replace with your own db name
    app.state.db_client = client
    app.state.db = db

    yield

    print("Shutting down MongoDB connection...")
    client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def main_page():
    return {"message": "Test 1"}

# Routes
app.include_router(idea_routes.router)
app.include_router(admin_routes.router)

app.add_exception_handler(InvalidCredentialsException, invalid_credentials_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(UserAlreadyExistsException, user_already_exists_exception_handler)
app.add_exception_handler(UnauthorizedAccessException, unauthorized_access_exception_handler)
app.add_exception_handler(DuplicateUpvoteException, duplicate_upvote_exception_handler)
app.add_exception_handler(EmptyContentException, empty_content_exception_handler)
app.add_exception_handler(InvalidIDException, invalid_id_exception_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response[List[Dict[str, Any]]](
        error_code=ErrorCodes.VALIDATION_ERROR.value,
        message="Validation error",
        details=exc.errors(),
        status_code=HTTPStatusCodes.UNPROCESSABLE_ENTITY.value
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == HTTPStatusCodes.UNAUTHORIZED.value:
        return create_error_response[None](
            error_code=ErrorCodes.UNAUTHORIZED_ACCESS.value,
            message=exc.detail or "Unauthorized access",
            details=None,
            status_code=exc.status_code
        )
    elif exc.status_code == HTTPStatusCodes.NOT_FOUND.value:
        return create_error_response[None](
            error_code=ErrorCodes.RESOURCE_NOT_FOUND.value,
            message=exc.detail or "Resource not found",
            details=None,
            status_code=exc.status_code
        )
    else:
        return create_error_response[None](
            error_code="HTTPException",
            message=exc.detail or "An error occurred",
            details=None,
            status_code=exc.status_code
        )

# uvicorn src.main:app --reload



