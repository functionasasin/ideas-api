import os
from enum import Enum
from fastapi import APIRouter, HTTPException, Request, Query
from typing import List
from app.models.idea_model import Idea, IdeaResponse
from app.helpers.db_helper import idea_helper
from bson import ObjectId
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

TEST_MODE = os.getenv("TEST_MODE", "False") == "True" # For testing, can remove

class SortOptions(str, Enum):
    upvotes = "upvotes"

# Retrieves a list of ideas from db with sorting, filtering, and pagination options
@router.get("/ideas", response_model=List[IdeaResponse])
async def get_ideas(request: Request, upvotes: int = Query(None, ge=0), sort: SortOptions = None,
    limit: int = Query(10, ge=1),
    skip: int = Query(0, ge=0),
    keyword: str = Query(
        None,
        min_length=1,
        max_length=50,
        regex=r"^[a-zA-Z0-9\s]+$",
        description="Keyword for searching ideas. Allowed characters are letters, numbers, and spaces.",
    ),
):
    ideas_collection = request.app.state.db["ideas"]
    query = {}

    """ 
     upvotes: minimum number of upvotes to filter has to be >= 0
     sorting: will only support upvotes for now
     limit: the amount of ideas that are returned (max to 10)
     keyword: words to search for within the content (max of 50 characters)
    """

    if upvotes is not None:
        query["upvote_count"] = {"$gte": upvotes}

    if keyword:
        query["content"] = {"$regex": keyword, "$options": "i"}

    cursor = ideas_collection.find(query)

    if sort == SortOptions.upvotes:
        cursor = cursor.sort("upvote_count", -1)

    cursor = cursor.skip(skip).limit(limit)

    ideas = [idea_helper(idea) async for idea in cursor]

    return ideas

@router.post("/ideas", response_model=IdeaResponse, status_code=201)
async def submit_idea(idea: Idea, request: Request):
    ideas_collection = request.app.state.db["ideas"]

    if not idea.content.strip():
        raise HTTPException(status_code=400, detail="Idea content cannot be empty.")

    idea_doc = idea.model_dump()
    idea_doc["upvote_count"] = 0
    idea_doc["upvoted_by"] = []

    result = await ideas_collection.insert_one(idea_doc)
    new_idea = await ideas_collection.find_one({"_id": result.inserted_id})

    return idea_helper(new_idea)

# IP-based upvoting so I don't have to implement a user auth
@router.post("/ideas/{id}/upvotes")
async def upvote_idea(id: str, request: Request):
    ip_address = request.client.host
    ideas_collection = request.app.state.db["ideas"]

    idea = await ideas_collection.find_one({"_id": ObjectId(id)})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # This is purely for testing, because it limits to 1 upvote per IP
    if not TEST_MODE:
        if ip_address in idea["upvoted_by"]:
            raise HTTPException(status_code=400, detail="You have already upvoted this idea")

    await ideas_collection.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"upvote_count": 1}, "$push": {"upvoted_by": ip_address}}
    )

    updated_idea = await ideas_collection.find_one({"_id": ObjectId(id)})
    return {"message": "Upvote successful", "upvote_count": updated_idea["upvote_count"]}
