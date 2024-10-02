# Helper functions to transform mongodb documents into dictionary format
def idea_helper(idea) -> dict:
    return {
        "id": str(idea["_id"]),
        "content": idea["content"],
        "upvote_count": idea.get("upvote_count", 0),
        "upvoted_by": [str(user_id) for user_id in idea.get("upvoted_by", [])],
    }

def admin_helper(admin) -> dict:
    return {
        "id": str(admin["_id"]),
        "username": admin["username"],
        "hashed_password": admin["hashed_password"]
    }