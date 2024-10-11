from pydantic import BaseModel, Field
from typing import List

class Idea(BaseModel):
    content: str = Field(max_length=500)