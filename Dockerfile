FROM python:3.12

WORKDIR /chats

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /chats

RUN typer src\cli.py run --username admin --email admin@email.com --first-name ADMIN --last-name ADMIN --password admin  

CMD ["fastapi", "run", "src/main.py", "--port", "80"]
