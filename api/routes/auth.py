# library imports
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase


# module imports
from ..models import Token
from ..dbconn import get_database
from ..hashing import Hash
from .. import oauth


router = APIRouter(prefix="/login",tags=["Authentication"])


@router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),database: AsyncIOMotorDatabase = Depends(get_database),):

    user = await database["users"].find_one({"name": user_credentials.username})

    if user and Hash.verify(user_credentials.password, user["password"]):
        access_token = oauth.create_access_token(payload={
            "id": user["_id"],
        })
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user credentials"
        )