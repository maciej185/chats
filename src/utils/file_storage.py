"""Utilities for accessing the file storage."""

import shutil
from pathlib import Path

from fastapi import UploadFile

from .config import ConfigManager

config = ConfigManager.get_config()


class FileStorageManager:
    """Utility class for interacting with the file storage."""

    file_storage_root_path = config.file_storage_path
    """Path to the root of the file storage, fetched from the app's config."""

    @classmethod
    def save_profile_picture(cls, user_id: int, profile_pic_file: UploadFile) -> Path:
        """Save profile picture of a given user.

        Args:
            user_id: ID of the user whose profile is meant to be updated with
                        the new profile picture.
            profile_pic_file: An instance of the UploadFile class, representing
                            the file sent in the request with 'multipart/form-data'
                            set as the content-type.

        Returns:
            Instance of the pathlib.Path class with the location of the saved file.
        """
        profile_pic_file_path = Path(
            cls.file_storage_root_path,
            "auth",
            str(user_id),
            "profile_picture",
            profile_pic_file.filename,
        )
        if profile_pic_file_path.parent.exists():
            shutil.rmtree(profile_pic_file_path.parent)
        profile_pic_file_path.parent.mkdir(parents=True)
        with open(profile_pic_file_path, "wb") as f:
            f.write(profile_pic_file.file.read())
        return profile_pic_file_path
