"""Tests for the chat endpoints."""

import pytest
from fastapi import status

from src.test.client import client


class TestChat:
    """Tests for the chat ednpoints."""

    def test_create_chat_user_not_logged_in_exception_raised(self) -> None:
        res = client.post("/chat/add", json={"name": "Chat name"})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json()["detail"] == "Not authenticated"

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_correct_data_sent_chat_created(self) -> None:
        res = client.post("/chat/add", json={"name": "Chat name"})

        assert res.status_code == status.HTTP_201_CREATED

        res_data = res.json()
        assert res_data["name"] == "Chat name"
        assert res_data["chat_id"] == 1

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_incorrect_data_sent_empty_body_exception_raised(self) -> None:
        res = client.post("/chat/add", json={})

        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
