# ata-pipeline0
Snowplow to Redshift data processing.

## Run

The code is primarily intended to be run on AWS Lambda, and there is a backfill CLI when needed.

### Backfill
To run a backfill, make sure you have AWS credentials on your machine and that you have any MFA commands run already
as well (e.g. `aws-mfa`). Provide the target database's credentials via environment variables and run the backfill
script for the intended partner site, a given date, and the number of days starting from said date.

Example run for `afro-la` for 7 days starting from 2022-11-20:
`HOST=fakehost PORT=5432 USERNAME=fake PASSWORD=fake DB_NAME=fake python ata_pipeline0/backfill.py --start-date 2022-11-20 --days 7 afro-la`

### Docker

The `Dockerfile` in the root of the project is the correct target for building.

To build locally: `docker build -t {desired-name-and-tag} .`. For example: `docker build -t lnl/ata-p0:latest .`
Don't forget the `.` at the end to reference the `Dockerfile` in the current directory (assuming you run the command
from the root of the project).

To run the Docker image locally (with the Lambda set up):
`docker run --rm -p {local_port}:{container_port} {name-and-tag} {command}`.
For example: `docker run --rm -p 9000:8080 lnl/ata-p0:latest`. This will serve it on `localhost:9000`. To ping
the handler (and confirm it works), you can then make an HTTP request to it. For example:
`curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"field1":"b", "field2":"a"}'`

## Development Tools

We use [Poetry](https://python-poetry.org/) to manage dependencies. It also helps with pinning dependency and python
versions. We also use [pre-commit](https://pre-commit.com/) with hooks for [isort](https://pycqa.github.io/isort/),
[black](https://github.com/psf/black), and [flake8](https://flake8.pycqa.org/en/latest/) for consistent code style and
readability. Note that this means code that doesn't meet the rules will fail to commit until it is fixed.

We also use [mypy](https://mypy.readthedocs.io/en/stable/index.html) for static type checking. This can be run manually,
and the CI runs it on PRs.

### Setup

1. [Install Poetry](https://python-poetry.org/docs/#installation).
2. [Install pyenv](https://github.com/pyenv/pyenv)
3. Install the correct Python version for this project, here Python 3.9: `pyenv install 3.9`
4. Activate the installed Python version in the current shell: `pyenv shell 3.9`
5. Create a virtual environment from this Python version using Poetry: `poetry env use 3.9`
6. Activate the virtual environment: `source $(poetry env list --full-path)/bin/activate`
7. Run `poetry install --no-root`
8. Run  `pre-commit install` to set up `pre-commit`

You're all set up! Your local environment should include all dependencies, including dev dependencies like `black`.
This is done with Poetry via the `poetry.lock` file. As for the containerized code, that still pulls dependencies from
`requirements.txt`. Any containerized dependency requirements need to be updated in `pyproject.toml` then exported to
`requirements.txt`.

The next times you open this directory on your IDE, make sure the virtual environment is activated (i.e., Step 6).

### Run Code Format and Linting

To manually run isort, black, and flake8 all in one go, simply run `pre-commit run --all-files`.

### Run Static Type Checking

To manually run mypy, simply run `mypy` from the root directory of the project. It will use the default configuration
specified in the mypy.ini file.

### Update Dependencies

To update dependencies in your local environment, make changes to the `pyproject.toml` file then run `poetry update`.

## Tests

We use [pytest](https://docs.pytest.org) to run our tests. Simply run `pytest` to run all tests or `pytest <path>`
to run tests in a specific directory/file/module. You can also run `pytest -m unit` to run only unit tests, and 
`pytest -m integration` to run only integration tests. We run continuous integration (CI) via GitHub actions. We have
actions to run MyPy and run the tests.

Running integration tests requires a postgres instance. An easy way to spin one up is via Docker:
`docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_HOST_AUTH_METHOD=trust -p 127.0.0.1:5432:5432/tcp postgres`

Notably, the host is `127.0.0.1`, the port is `5432`, the username, password, and db name are all "postgres". You can
override these with environment variables for `HOST`, `PORT`, `USERNAME`, `PASSWORD`, and `DB_NAME`.

## Deployment

Deployment for the Local News Lab (LNL) is handled via AWS CodePipeline, defined elsewhere in the ata-infrastructure repo.
We use Docker to containerize our code. The LNL deploys this project on AWS Lambda.
