FROM python:3.13-slim

# Install system dependencies.
RUN apt-get update && apt-get install -y build-essential curl && apt-get clean

# Prevent Python from buffering stdout and stderr.
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.4

# Install Poetry.
RUN pip install "poetry==$POETRY_VERSION"

# Set the working directory to the repository root.
WORKDIR /app

# Copy Poetry configuration files.
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating a virtual environment.
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the entire project into the container.
COPY . .

ENTRYPOINT ["python", "url_shortner/shortner.py"]
