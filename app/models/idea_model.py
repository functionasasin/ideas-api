from pydantic import BaseModel, Field
from typing import List

class Idea(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class IdeaResponse(Idea):
    id: str
    upvote_count: int = 0
    upvoted_by: List[str] = []