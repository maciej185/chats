
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

> **_TO BE ADDED_**