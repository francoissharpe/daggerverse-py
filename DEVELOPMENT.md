# Development

## Prerequisites

- [Dagger CLI](https://docs.dagger.io/quickstart/729237/cli)
- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.11](https://www.python.org/downloads/)
- [venv](https://docs.python.org/3/library/venv.html)

## Working on an existing module

These steps are for when you want to develop an existing module. We will use the `mkdocs-material` module as an example.

### Steps

1. Clone the repository

    ```bash
    git clone <>
    ```

2. Change directory to the module

    ```bash
    cd mkdocs-material
    dagger develop
   cd dagger
    ```

3. Create a virtual environment

    ```bash
    python -m venv mkdocs-material-venv
   source mkdocs-material-venv/bin/activate
    ```

4. Install the dependencies

    ```bash
      pip install -e ./sdk
    ```
   
## Creating a new module

These steps are for when you want to develop a new module.

### Steps

1. Create a new module

    ```bash
    dagger dagger init --sdk=python my-awesome-module
   cd my-awesome-module
    ```
   
2. Create a virtual environment

    ```bash
   cd my-awesome-module
    python -m venv my-awesome-module-venv
    source my-awesome-module-venv/bin/activate
     ```
   
3. Install the dependencies

    ```bash
    pip install -e ./sdk
    ```

## Other

### Installing module as a dependency

```shell
# In the module directory
dagger install github.com/francoissharpe/daggerverse-python/python@main
```

## References

- [Dagger - Developing with Python](https://docs.dagger.io/manuals/developer/python)
- [Dagger - Developer Manual](https://docs.dagger.io/manuals/developer)
- [Dagger - Dependencies](https://docs.dagger.io/manuals/developer/dependencies)
- [Dagger - User Guide](https://docs.dagger.io/manuals/user)