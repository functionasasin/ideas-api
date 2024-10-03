from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.helpers.db_helper import admin_helper
from src.models.admin_model import Admin
from src.utils.jwt import verify_password, create_access_token, verify_token, get_password_hash
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from bson import ObjectId
from datetime import timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admins/login")

@router.post("/admins")
async def register_admin(admin: Admin, request: Request):
    admins_collection = request.app.state.db["admins"]

    existing_admin = await admins_collection.find_one({"username": admin.username})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin username already exists")

    hashed_password = get_password_hash(admin.password)
    admin_data = {"username": admin.username, "hashed_password": hashed_password}
    await admins_collection.insert_one(admin_data)

    return {"message": "Admin registered successfully"}

@router.post("/admins/login")
async def login_admin(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    admins_collection = request.app.state.db["admins"]

    admin = await admins_collection.find_one({"username": form_data.username})
    if not admin:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    admin_in_db = admin_helper(admin)

    if not verify_password(form_data.password, admin_in_db["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_in_db["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_admin(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return payload

@router.delete("/ideas/{id}")
async def delete_idea(id: str, request: Request, token: str = Depends(oauth2_scheme)):
    ideas_collection = request.app.state.db["ideas"]

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await ideas_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted successfully"}