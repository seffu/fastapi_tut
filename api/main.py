from fastapi import FastAPI

from .routes import users,posts

app = FastAPI()

app.include_router(posts.router)
