FROM python:3.12

WORKDIR /chats

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /chats

CMD ["fastapi", "run", "src/main.py", "--port", "80"]
