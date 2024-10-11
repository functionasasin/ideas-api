from .idea_routes import router as idea_router
from .admin_routes import router as admin_router

__all__ = [
    "idea_router",
    "admin_router",
]