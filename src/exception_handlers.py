from fastapi import Request
from src.helpers import create_error_response

async def invalid_credentials_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def user_already_exists_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def unauthorized_access_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def invalid_id_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def resource_not_found_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def duplicate_upvote_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )

async def empty_content_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        status_code=exc.status_code
    )