from pydantic import BaseModel, Field
from typing import Optional

class AdminBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)

class AdminCreate(AdminBase):
    password: str = Field(min_length=8, max_length=24)

class AdminResponse(AdminBase):
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None