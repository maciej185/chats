"""Main app module."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import admin
from src.routes import auth, chat
from src.utils import ConfigManager

app = FastAPI()

config = ConfigManager.get_config()

config_logging_levels_mapping = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logging.basicConfig(
    level=config_logging_levels_mapping[config.logging_config.level],
    filename=config.logging_config.file_path,
    filemode=config.logging_config.filemode,
    format=config.logging_config.format,
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
