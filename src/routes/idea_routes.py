import os
from enum import Enum
from fastapi import APIRouter, Request, Query
from typing import List
from bson import ObjectId

from src.models import Idea, IdeaResponse, SuccessResponse
from src.helpers import idea_helper, create_success_response
from src.core import EmptyContentException, DuplicateUpvoteException, InvalidIDException, ResourceNotFoundException, HTTPStatusCodes

router = APIRouter()

TEST_MODE = False

class SortOptions(str, Enum):
    upvotes = "upvotes"

# Retrieves a list of ideas from db with sorting, filtering, and pagination options
@router.get("/ideas", response_model=SuccessResponse)
async def get_ideas(
    request: Request,
    upvotes: int = Query(None, ge=0),
    sort: SortOptions = None,
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

    if upvotes is not None:
        query["upvote_count"] = {"$gte": upvotes}

    if keyword:
        query["content"] = {"$regex": keyword, "$options": "i"}

    cursor = ideas_collection.find(query)

    if sort == SortOptions.upvotes:
        cursor = cursor.sort("upvote_count", -1)

    cursor = cursor.skip(skip).limit(limit)

    ideas = [idea_helper(idea) async for idea in cursor]

    return create_success_response(
        data=ideas,
        message="Ideas retrieved successfully"
    )

@router.post("/ideas", response_model=SuccessResponse, status_code=HTTPStatusCodes.CREATED.value)
async def submit_idea(idea: Idea, request: Request):
    ideas_collection = request.app.state.db["ideas"]

    if not idea.content.strip():
        raise EmptyContentException()

    idea_doc = idea.model_dump()
    idea_doc["upvote_count"] = 0
    idea_doc["upvoted_by"] = []

    result = await ideas_collection.insert_one(idea_doc)
    new_idea = await ideas_collection.find_one({"_id": result.inserted_id})

    return create_success_response(
        data=idea_helper(new_idea),
        message="Idea submitted successfully",
        status_code=HTTPStatusCodes.CREATED.value
    )

# IP-based upvoting so I don't have to implement a user auth
@router.post("/ideas/{id}/upvotes", response_model=SuccessResponse)
async def upvote_idea(id: str, request: Request):
    ip_address = request.client.host
    ideas_collection = request.app.state.db["ideas"]

    # Validate ObjectId
    try:
        idea_id = ObjectId(id)
    except Exception:
        raise InvalidIDException()

    idea = await ideas_collection.find_one({"_id": idea_id})
    if not idea:
        raise ResourceNotFoundException(resource_name="Idea")

    # This is purely for testing, because it limits to 1 upvote per IP
    if not TEST_MODE:
        if ip_address in idea["upvoted_by"]:
            raise DuplicateUpvoteException()

    await ideas_collection.update_one(
        {"_id": idea_id},
        {"$inc": {"upvote_count": 1}, "$push": {"upvoted_by": ip_address}}
    )

    updated_idea = await ideas_collection.find_one({"_id": idea_id})
    return create_success_response(
        data={"upvote_count": updated_idea["upvote_count"]},
        message="Upvote successful"
    )