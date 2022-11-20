from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os

from dotenv import load_dotenv
load_dotenv()

motor_client = AsyncIOMotorClient(
    os.getenv('MONGODB_URI')
)  # Connection to the whole server
# database = motor_client["blogapi"]  # Single database instance
database = motor_client.blogapi # Single database instance


def get_database() -> AsyncIOMotorDatabase:
    return database