import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") # Example in .env is mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.<NAME>.mongodb.net/

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30