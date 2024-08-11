"""Configuration-related utilites."""

import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl

load_dotenv()


class LoggingConfigView(BaseModel):
    """Model for storing logging configuration.

    Attributes:
        file_path: Path to a file where where the logs will be saved,
        level: Logging level,
        filemode: Indicate whether now logs will overwrite the existing ones or be appended at the end of the file.,
        format: Format of the logging message.
    """

    file_path: FilePath
    level: str
    filemode: str
    format: str


class ConfigView(BaseModel):
    """Model for storing config information.

    Attributes:
        app_name: Name displayed in the Swagger docs.
        token_signing_key: Secret key used to sign the JWTs.
        token_signing_algorithm: Name of the algorithm used to sign the
                                    token.
    """

    app_name: str
    token_signing_key: str
    token_signing_algorithm: str
    file_storage_path: DirectoryPath
    default_profile_pic_path: FilePath
    allowed_origins: list[HttpUrl | Literal["*"]]
    logging_config: LoggingConfigView


class ConfigManager:
    """Configuration parser."""

    _instance: ConfigView | None = None
    _config_file_path: Path = Path(os.getenv("CONFIG_PATH"))

    @classmethod
    def load_from_file(cls) -> None:
        """Load given config file.

        Args:
            config_file_path (Path): config file path.
        """
        with open(cls._config_file_path) as f:
            config_file = json.load(f)
        cls._instance = ConfigView(**config_file)

    @classmethod
    def get_config(cls) -> ConfigView | None:
        """Get current configuration.

        Returns:
            Current configuration.
        """
        if not cls._instance:
            cls.load_from_file()
        return cls._instance
