"""Module for configuring and instantiating a logger."""

import logging

from src.utils import ConfigManager

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
