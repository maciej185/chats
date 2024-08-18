## Installation

There are two options of installing the project. It can either be run locally or in a Docker container.

### Local

To run the project locally it is recommended to create a virtual Python environment with the following command executed in the project's root directory:

```bash
    python -m venv venv
```

The next step is to activate the environment and install the necessary packages:

```bash
    venv\Scripts\activate.bat
    pip install -r requirements.txt
```

To ensure that the imports are resolved correctly please ensure to install the the application package locally in an editable mode. This can be achieved by running the following command in a directory where the `setup.py` file is placed:

```bash
    pip install -e .
```

When running the project locally ensure that you have the database engine running on a correct port as well.

### Docker

You can either create an image from the included `Dockerfile` and create a container on it's own in which case you also need to provide the following environment variables with information about the DB:

- DB_HOST: mysql
- DB_ENGINE: mysql+pymysql
- DB_USERNAME: root
- DB_PASSWORD: secret
- DB_PORT: 3306
- DB_NAME: mysql

One other variable you need to provide is a path to the `config.json` file:

- CONFIG_PATH: config.json

In the example above the `config.json` file would be placed in the root of the project.

## Getting started

### Create an admin user

There is a small CLI tool included with a single command for creating an admin user. After creating the virtual environment and installing the required dependencies, navigate to the root of the project and run the following command:

```bash
    typer src\cli.py run
```

You will prompted for the profile information and credentials. Afterwards the new admin user is created and can be used to access the admin dashboard.

When creating an image using the `Dockerfile` the command is run automatically after the environment is ready. You can control the credentials of the default admin user by modifying the line number 11 of the `Dockerfile`:

```dockerfile
    RUN typer src\cli.py run --username admin --email admin@email.com --first-name ADMIN --last-name ADMIN --password admin
```
