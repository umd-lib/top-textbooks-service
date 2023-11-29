# top-textbook-service

Top-Textbook Service for Drupal

## Purpose

This is a flask microservice for handling textbook availability in Drupal. It will make requests to the Alma API to retrieve metadata.

## Development Environment

Python version: 3.12

### Installation

```bash
git clone git@github.com:umd-lib/top-textbooks-service.git
cd top-textbooks-service
pyenv install --skip-existing $(cat .python-version)
python -m venv .venv --prompt textbooks
pip install -r requirements.test.txt -e .
```

### Configuration

Create a `.env` file with the following contents:

```bash
FLASK_DEBUG=1
```

### Running

To run the application in debug mode, with hot code reloading:

```bash
flask --app "textbooks.web:app()" run
```

The microservice will be available at <http://localhost:5000/>,
with a simple HTML landing page.

To change the port, add `-p {port number}` to the `flask` command:

```bash
# for example, to run on port 8000
flask --app "textbooks.web:app()" run -p 8000
```

### Testing

This project uses the [pytest] testing framework. To run the full
[test suite](tests):

```bash
pytest
```

To run the test suite with coverage information from [pytest-cov]:

```bash
pytest --cov src --cov-report term-missing
```

This project also uses [pycodestyle] as a style checker and linter:

```bash
pycodestyle src
```

Configuration of pycodestyle is found in the [tox.ini](tox.ini) file.

### Using VSCode Dev Containers

This repo has been configured to use VSCode's Development Containers.
Upon opening this codebase in VSCode:

- A notification will pop up asking if the folder should be re-opened in a container. Select "Yes". VS Code will restart and create a Docker container (this takes a minute or two, if the Docker image has not previously been downloaded).

- The pip install command is run as part of the Docker container setup, and various VS Code extensions are automatically added.

- To run PATSy commands and Python tools such as "pytest", open a terminal in VS Code (select "Terminal | New Terminal") from the menubar.

### Deploying using Docker

Build the image:

```bash
docker build -t docker.lib.umd.edu/top-textbooks-service:latest .
```

If you need to build for multiple architectures (e.g., AMD and ARM), you
can use `docker buildx`. This assumes you have a builder named "local"
configured for use with your docker buildx system, and you are logged in
to a Docker repository that you can push images to:

```bash
docker buildx build --builder local --platform linux/amd64,linux/arm64 \
    -t docker.lib.umd.edu/top-textbooks-service:latest --push .

# then pull the image so it is available locally
docker pull docker.lib.umd.edu/top-textbooks-service:latest
```

Run the container:

```bash
docker run -d -p 5000:5000 docker.lib.umd.edu/oaipmh-server:latest
```

If you created a `.env` file (see [Configuration](#configuration)), you
can run the Docker image using that file.

```bash
docker run -d -p 5000:5000 \
    --env-file .env \
    docker.lib.umd.edu/top-textbooks-service:latest
```

[pytest]: https://docs.pytest.org/en/7.3.x/
[pytest-cov]: https://pypi.org/project/pytest-cov/
[pycodestyle]: https://pycodestyle.pycqa.org/en/latest/
