from fastapi import FastAPI

from .routes import users,posts,auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
