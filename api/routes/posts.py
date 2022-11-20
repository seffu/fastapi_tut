from fastapi import APIRouter,Depends,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId, errors

from ..dbconn import get_database
from ..utils import pagination,get_object_id
from ..models import (CommentCreate,PostDB,PostCreate,PostPartialUpdate)

router = APIRouter(tags=['posts'])

async def get_post_or_404(
    id: ObjectId = Depends(get_object_id),
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> PostDB:
    raw_post = await database["posts"].find_one({"_id": id})

    if raw_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return PostDB(**raw_post)


@router.get("/posts")
async def list_posts(
    pagination: tuple[int, int] = Depends(pagination),
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> list[PostDB]:
    skip, limit = pagination
    query = database["posts"].find({}, skip=skip, limit=limit)

    results = [PostDB(**raw_post) async for raw_post in query]

    return results

@router.get("/posts/{id}", response_model=PostDB)
async def get_post(post: PostDB = Depends(get_post_or_404)) -> PostDB:
    return post


@router.post("/posts", response_model=PostDB, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate, database: AsyncIOMotorDatabase = Depends(get_database)
) -> PostDB:
    post_db = PostDB(**post.dict())
    await database["posts"].insert_one(post_db.dict(by_alias=True))

    post_db = await get_post_or_404(post_db.id, database)

    return post_db


@router.patch("/posts/{id}", response_model=PostDB)
async def update_post(
    post_update: PostPartialUpdate,
    post: PostDB = Depends(get_post_or_404),
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> PostDB:
    await database["posts"].update_one(
        {"_id": post.id}, {"$set": post_update.dict(exclude_unset=True)}
    )

    post_db = await get_post_or_404(post.id, database)

    return post_db


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: PostDB = Depends(get_post_or_404),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    await database["posts"].delete_one({"_id": post.id})


@router.post("/posts/{id}/comments", response_model=PostDB, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate,post: PostDB = Depends(get_post_or_404),database: AsyncIOMotorDatabase = Depends(get_database)) -> PostDB:
    await database["posts"].update_one(
        {"_id": post.id}, {"$push": {"comments": comment.dict()}}
    )

    post_db = await get_post_or_404(post.id, database)

    return post_db