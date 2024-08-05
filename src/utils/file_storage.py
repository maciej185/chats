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

    @classmethod
    def save_message_image(
        cls, user_id: int, chat_id: int, message_id: int, image: UploadFile
    ) -> Path:
        """Save an image sent in a given chat.

        Args:
            user_id: ID of the user who is sending the image.
            chat_id: ID of the chat where the given image is sent.
            message_id: ID of the chat messages that the given image object
                is related to.
            image: An instance of the fastapi.UploadFile class, representing the image that is meant to be uploaded.
        Returns:
            Path to the saved image.
        """
        image_file_path = Path(
            cls.file_storage_root_path,
            "chat_messages",
            str(user_id),
            str(chat_id),
            str(message_id),
            image.filename,
        )
        image_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(image_file_path, "wb") as f:
            f.write(image.file.read())
        return image_file_path
