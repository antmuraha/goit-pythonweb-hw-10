FROM python:3.12-slim

# Keep python output unbuffered and avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system packages needed to build some Python packages (e.g. psycopg2)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# install uv from PyPI (safe under podman rootless)
RUN pip install --upgrade pip \
	&& pip install uv

# Copy only pyproject first (leverage cache) and install dependencies
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Install project dependencies
RUN uv pip install --system --no-cache .

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
