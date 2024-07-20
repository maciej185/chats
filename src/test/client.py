from datetime import datetime

from fastapi.testclient import TestClient

from src.main import app


class IncorrectCredentialsException(Exception):
    """Raised when provided login credentials are incorrect."""

    def __init__(self, *args: object) -> None:
        self.message = "Incorrect username or password."
        super().__init__(self.message, *args)


class BaseTestClient(TestClient):
    """TestClient with additional utilities for the app."""

    AUTHENTICATION_ENDPOINT_URL = "/auth/token"
    REGISTRATION_ENDPOINT_URL = "/auth/register"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def register_user(self, username: str, password: str) -> None:
        """Register a user with given credentials.

        The method sends a request to an appropriate endpoint
        that then triggers the creation of a new user. Data
        for the Profile related to the newly created
        user consists of mock values only.

        Args:
            username: Username for the new user.
            passsword: Password for the new user.
        """
        client.post(
            "/auth/register",
            json={
                "user_data": {
                    "username": username,
                    "email": f"{username}@email.com",
                    "plain_text_password": password,
                },
                "profile_data": {
                    "first_name": "First name",
                    "last_name": "Last name",
                    "date_of_birth": datetime.now().date().strftime("%Y-%m-%d"),
                },
            },
        )

    def login(self, username: str, password: str) -> None:
        """Add authentication headers to every request.

        The method sends a request to an appropriate endpoint
        to get an authentication token that is then attached to every
        request as the value of the 'Authorization' header.

        Args:
            username: Username of the user that is meant to be logged in.
            password: Password of the user that is meant to be logged in.

        Raises:
            IncorrectCredentialsException: Raised when the credentials
                are invalid and thus the request did not return a token.
        """
        token_res = self.post(
            self.AUTHENTICATION_ENDPOINT_URL, data={"username": username, "password": password}
        )

        if token_res.status_code == 401:
            raise IncorrectCredentialsException

        self.headers = {"Authorization": f"Bearer {token_res.json()["access_token"]}"}

    def logout(self) -> None:
        """Remove authentication headers.

        The method mimics logging the user out by removing the 'Authorization'
        header from the headers sent with with every request if such header
        is present. If not, the raised exception is caught and ignored.
        """
        try:
            self.headers.pop("Authorization")
        except KeyError:
            pass


client = BaseTestClient(app)
