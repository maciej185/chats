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

    def test_user_not_logged_in_attempting_to_add_member_exception_raised(self) -> None:
        res = client.post("/chat/add_member", json={"user_id": 1, "chat_id": 1})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json()["detail"] == "Not authenticated"

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_logged_in_chat_doesnt_exist_attempting_to_add_member_exception_raised(self) -> None:
        client.register_user(username="user1", password="password")
        res = client.post("/chat/add_member", json={"user_id": 100, "chat_id": 2})
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json()["detail"] == "Chat with the given ID was not found in the DB."

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_chat_exists_new_member_doesnts_attemptint_to_add_member_exception_raised(
        self,
    ) -> None:
        client.register_user(username="user1", password="password")
        client.create_chat(chat_name="Chat")
        res = client.post("/chat/add_member", json={"user_id": 100, "chat_id": 2})
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json()["detail"] == "User with the given ID was not found in the DB."

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_is_not_member_chat_exists_new_member_exists_attemptint_to_add_member_exception_raised(
        self,
    ) -> None:
        client.register_user(username="user1", password="password")
        client.register_user(username="user2", password="password")
        client.create_chat(chat_name="Chat")
        client.logout()
        client.login(username="user1", password="password")
        res = client.post("/chat/add_member", json={"user_id": 3, "chat_id": 2})
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert (
            res.json()["detail"]
            == "Currently authorized user is not a member of the chat. Only chat members can add new members."
        )

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_is_member_chat_exists_new_member_already_added_attemptint_to_add_member_exception_raised(
        self,
    ) -> None:
        client.create_chat(chat_name="Chat")
        res = client.post("/chat/add_member", json={"user_id": 1, "chat_id": 2})
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert res.json()["detail"] == "The user is already a member of the given chat."

    @pytest.mark.usefixtures("register_login_and_logout")
    def test_user_logged_in_is_member_chat_exists_new_member_exists_attemptint_to_add_member_created_successfully(
        self,
    ) -> None:
        client.create_chat(chat_name="Chat")
        res = client.post("/chat/add_member", json={"user_id": 3, "chat_id": 2})
        assert res.status_code == status.HTTP_201_CREATED
