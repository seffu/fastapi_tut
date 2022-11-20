# library imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dbconn import get_database

# module imports
from api import oauth
from ..models import User, UserResponse
from ..hashing import Hash
from ..send_email import send_registration_email
import secrets


router = APIRouter(prefix="/users",tags=["Users"])

@router.post("/registration", response_description="Register New User", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registration(user_info: User, database: AsyncIOMotorDatabase = Depends(get_database)):
    user_info = jsonable_encoder(user_info)

    # check for duplications
    username_found = await database["users"].find_one({"name": user_info["name"]})
    email_found = await database["users"].find_one({"email": user_info["email"]})

    if username_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="There already is a user by that name")

    if email_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="There already is a user by that email")

    # hash the user password
    user_info["password"] = Hash.hasher(user_info["password"])
    # generate apiKey
    user_info["apiKey"] = secrets.token_hex(20)
    new_user = await database["users"].insert_one(user_info)
    created_user = await database["users"].find_one({"_id": new_user.inserted_id})
    # send email
    await send_registration_email("Registration successful", user_info["email"],
        {
            "title": "Registration successful",
            "name": user_info["name"]
        }
    )
    return created_user

@router.post("/details", response_description="Get user details", response_model=UserResponse)
async def details(current_user=Depends(oauth.get_current_user),database: AsyncIOMotorDatabase = Depends(get_database)):
    user = await database["users"].find_one({"_id": current_user["_id"]})
    return user