from pydantic import BaseModel, Field
from typing import List

class Idea(BaseModel):
    content: str = Field(max_length=500)

class IdeaResponse(Idea):
    id: str
    upvote_count: int = 0
    upvoted_by: List[str] = []