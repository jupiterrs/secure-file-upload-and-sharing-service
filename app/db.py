import os

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient

from app.security import get_password_hash

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client["file_service"]
users = db["users"]
files_collection = db["files"]


async def add_user(user):
    existing_user = await users.find_one({"username": user.username})
    if existing_user:
        return False
    await users.insert_one(
        {"username": user.username, "hashed_password": get_password_hash(user.password)}
    )
    return True


async def get_user(username):
    user = await users.find_one({"username": username})
    return user
