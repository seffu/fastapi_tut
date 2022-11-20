# library imports
from fastapi import APIRouter, HTTPException, status,Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# module imports
# from ..dbconn import get_database
from ..dbconn import database
from ..models import PasswordReset, PasswordResetRequest
from ..send_email import password_reset
from ..oauth import create_access_token, get_current_user
from ..hashing import Hash

router = APIRouter(prefix="/password",tags=["Password Reset"])

@router.post("/request", response_description="Password reset request")
async def reset_request(user_email: PasswordResetRequest):
    user = await database["users"].find_one({"email": user_email.email})
    if user is not None:
        token = create_access_token({"id": user["_id"]})
        print(token)
        reset_link = f"http://127.0.0.1:8000/password/reset?token={token}"
        await password_reset("Password Reset", user["email"],
            {
                "title": "Password Reset",
                "name": user["name"],
                "reset_link": reset_link
            }
        )
        return {"msg": "Email has been sent with instructions to reset your password."}

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your details not found, invalid email address"
        )

@router.put("/reset/", response_description="Password Reset")
async def reset(token: str, new_password: PasswordReset):

    request_data = {k: v for k, v in new_password.dict().items()
                    if v is not None}

    # get the hashed version of the password
    request_data["password"] = Hash.hasher(request_data["password"])

    if len(request_data) >= 1:
        # use token to get the current user
        user = await get_current_user(token)

        # update the password of the current user
        update_result = await database["users"].update_one({"_id": user["_id"]}, {"$set": request_data})

        if update_result.modified_count == 1:
            # get the newly updated current user and return as a response
            updated_user = await database["users"].find_one({"_id": user["_id"]})
            if(updated_user) is not None:
                return updated_user

    existing_user = await database["users"].find_one({"_id": user["_id"]})
    if(existing_user) is not None:
        return existing_user

    # Raise error if the user can not be found in the database
    raise HTTPException(status_code=404, detail=f"User not found")