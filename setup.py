"""Python setup.py for chats package"""
import io
import os
from setuptools import setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="chats",
    version="1.0.0",
    description="FastAPI Backend for a web chat application.",
    url="https://github.com/maciej185/chats",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Maciej Lisowski",
    packages=["src"],
)