"""Main app module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import auth, chat
from src.utils import ConfigManager

app = FastAPI()

config = ConfigManager.get_config()

app.include_router(auth.router)
app.include_router(chat.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
