"""Main app module."""

from fastapi import FastAPI

from src.routes import auth, chat

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)
