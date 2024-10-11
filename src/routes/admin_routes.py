from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from datetime import timedelta

from src.models import AdminCreate, AdminResponse, Token, SuccessResponse
from src.helpers import create_success_response, admin_helper
from src.core import InvalidCredentialsException, UserAlreadyExistsException, UnauthorizedAccessException, InvalidIDException, ResourceNotFoundException, HTTPStatusCodes
from src.utils import verify_password, create_access_token, verify_token, get_password_hash
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/login")

@router.post("/admins", response_model=SuccessResponse, status_code=HTTPStatusCodes.CREATED.value)
async def register_admin(admin: AdminCreate, request: Request):
    admins_collection = request.app.state.db["admins"]

    existing_admin = await admins_collection.find_one({"username": admin.username})
    if existing_admin:
        raise UserAlreadyExistsException()

    hashed_password = get_password_hash(admin.password)
    admin_data = admin.model_dump()
    admin_data["hashed_password"] = hashed_password
    admin_data.pop("password", None)
    result = await admins_collection.insert_one(admin_data)
    new_admin = await admins_collection.find_one({"_id": result.inserted_id})

    return create_success_response(
        data=admin_helper(new_admin),
        message="Admin registered successfully",
        status_code=HTTPStatusCodes.CREATED.value
    )

@router.post("/admins/login", response_model=SuccessResponse)
async def login_admin(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    admins_collection = request.app.state.db["admins"]

    admin = await admins_collection.find_one({"username": form_data.username})
    if not admin or not verify_password(form_data.password, admin["hashed_password"]):
        raise InvalidCredentialsException()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin["username"]}, expires_delta=access_token_expires
    )
    return create_success_response(
        data={"access_token": access_token, "token_type": "bearer"},
        message="Login successful"
    )

async def get_current_admin(
    token: str = Depends(oauth2_scheme), request: Request = None
):
    admins_collection = request.app.state.db["admins"]
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedAccessException()
    username: str = payload.get("sub")
    if username is None:
        raise UnauthorizedAccessException()
    admin = await admins_collection.find_one({"username": username})
    if admin is None:
        raise InvalidCredentialsException()
    return admin_helper(admin)

@router.delete("/ideas/{id}", response_model=SuccessResponse, status_code=HTTPStatusCodes.OK.value) # Fix no content response
async def delete_idea(
    id: str, request: Request, current_admin: dict = Depends(get_current_admin)
):
    ideas_collection = request.app.state.db["ideas"]

    # Validate ObjectId
    try:
        idea_id = ObjectId(id)
    except Exception:
        raise InvalidIDException()

    idea = await ideas_collection.find_one({"_id": idea_id})
    if not idea:
        raise ResourceNotFoundException(resource_name="Idea")
    
    result = await ideas_collection.delete_one({"_id": idea_id})
    if result.deleted_count == 0:
        raise ResourceNotFoundException(resource_name="Idea")
    
    deleted_data = {
        "id": str(idea_id),
        "content": idea.get("content")
    }

    return create_success_response(
        data=deleted_data,
        message="Idea deleted successfully",
        status_code=HTTPStatusCodes.OK.value
    )