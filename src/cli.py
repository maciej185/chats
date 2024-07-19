"""CLI tool for managing internal workings of the app."""

from datetime import datetime
from typing import Annotated

import typer
from rich import print

from src.db import SessionLocal
from src.roles import Roles
from src.routes.auth.crud import create_user
from src.routes.auth.models import ProfileAdd, UserAdd

app = typer.Typer(no_args_is_help=True)


@app.command()
def add_admin(
    username: Annotated[str, typer.Option(prompt=True)],
    email: Annotated[str, typer.Option(prompt=True)],
    first_name: Annotated[str, typer.Option(prompt=True)],
    last_name: Annotated[str, typer.Option(prompt=True)],
    password: Annotated[str, typer.Option(prompt=True)],
) -> None:
    db = SessionLocal()
    user_data = UserAdd(
        username=username,
        email=email,
        plain_text_password=password,
    )
    profile_data = ProfileAdd(
        first_name=first_name, last_name=last_name, date_of_birth=datetime.now().date()
    )
    admin_user = create_user(
        db=db, user_data=user_data, profile_data=profile_data, role=Roles.ADMIN.value
    )

    print("User created successdully")
    print(admin_user.__dict__)

    db.close()


if __name__ == "__main__":
    app()
