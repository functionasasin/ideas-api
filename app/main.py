from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from app.routes import idea_routes, admin_routes
from app.config import MONGO_URI

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["idea_db"]  # Replace with your own db name
    app.state.db_client = client
    app.state.db = db

    yield

    print("Shutting down MongoDB connection...")
    client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def main_page():
    return {"message": "Test 1"}

# Routes
app.include_router(idea_routes.router)
app.include_router(admin_routes.router)

# uvicorn app.main:app --reload



