"""Initialize the engine."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class MissingDataConnectionStringComponenet(Exception):
    """Raised when a piece information required for DB connection was not supplied."""


def get_db_connection_string() -> str:
    """Build a connection string using environment variables."""
    db_data = {
        "db_engine": os.getenv("DB_ENGINE"),
        "db_username": os.getenv("DB_USERNAME"),
        "db_password": os.getenv("DB_PASSWORD"),
        "db_port": os.getenv("DB_PORT"),
        "db_name": os.getenv("DB_NAME"),
        "db_host": os.getenv("DB_HOST"),
    }

    for db_data_componenet in db_data.keys():
        if db_data[db_data_componenet] is None:
            raise MissingDataConnectionStringComponenet(
                f"{db_data_componenet} is missing from the environment variables."
            )

    return f"{db_data["db_engine"]}://{db_data['db_username']}:{db_data['db_password']}@{db_data['db_host']}:{db_data['db_port']}/{db_data['db_name']}"


engine = create_engine(get_db_connection_string())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
