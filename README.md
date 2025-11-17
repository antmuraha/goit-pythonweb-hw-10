# GoIT Full-Stack Python — FastAPI (Homework 08)

## Summary

This repository contains the code for GoIT homework 08. The project uses the FastAPI framework with a PostgreSQL database, SQLAlchemy models, and Alembic for schema migrations.

## Prerequisites

-   Docker or Podman
-   Python 3.12+

Copy the example env file and edit values as needed:

```bash
cp .env.example .env
# Edit .env to set your POSTGRES_PASSWORD and other values
```

## Local development

From the project root run the environment helper. This project uses the `uv` helper to create and sync virtual environments.

Recommended (using `uv`):

```bash
# Create a virtual environment and install dependencies
uv venv
uv sync

# Activate the created environment (choose the path created by your tool):
source .venv/bin/activate
```

If you don't use `uv`, create and activate a virtual environment with your preferred tool and install dependencies from the lock/manifest used in the project.

## Run Alembic migrations

Create a migration locally (only if you need to generate one):

```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply migrations to the database (only when necessary manually):

```bash
alembic upgrade head
```

Note: Alembic reads configuration from `alembic.ini` and from `migrations/env.py`. Ensure your database URL is set either in those files or via the environment variables expected by the application (for example `SQLALCHEMY_DATABASE_URL`).

## Run with Docker

This repository includes a Docker Compose setup that runs the FastAPI app and a PostgreSQL database. To build and start services locally:

```bash
docker compose up --build
```

The FastAPI server will be available at http://localhost:8000 by default. The application reads the DB connection string from the `SQLALCHEMY_DATABASE_URL` environment variable (or from `.env` if you load environment variables locally).

## Entrypoint script and automatic migrations

The Docker image uses the repository `entrypoint.sh` (included at the project root) as the container entrypoint. On container start the script performs the following steps:

-   If present, it loads environment variables from `/app/.env` so Alembic and the application see the same environment.
-   Runs `alembic upgrade head` to apply schema migrations. The script uses a simple retry loop (the bundled script sets `MAX_RETRIES=1` and waits 2 seconds between attempts). If migrations fail after the configured retries the container exits with a non-zero status.
-   After migrations complete successfully the script execs the container CMD, making the app process PID 1.

This behavior is convenient for development and simple deployments because it ensures the database schema is applied automatically on startup. For production environments, this is not recommended to be used without understanding this process.

## Contributing / Next steps

This project was created for educational purposes as part of the GoIT curriculum. You are welcome to:

-   Improve error handling and validation
-   Add automated tests
-   Enhance logging or add a dry-run mode

## License

Created for educational purposes.
