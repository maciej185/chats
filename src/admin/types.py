"""Types for the admin package."""

from typing import Literal, TypedDict


class HTMLInfoDict(TypedDict):
    """Dicitionary with fields describing the best html input option for a given field."""

    html_tag: str
    html_tag_args: dict[str, str | int]


class ColumnDict(TypedDict):
    """Dicitionary with fields describing a single column from a DB table."""

    type: str
    html: list[HTMLInfoDict]
    primary_key: bool
    foreign_key: None | list[dict[Literal["table", "column"], str]]
