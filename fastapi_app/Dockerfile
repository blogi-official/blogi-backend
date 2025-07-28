FROM python:3.12-slim

# Install System Packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set WORKDIR
WORKDIR /blogi-backend/fastapi_app

# Install poetry
RUN pip install --upgrade pip && pip install poetry

# Set poetry environment
RUN poetry config virtualenvs.create false

# copy poetry setting files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-root

# Install Playwright
RUN poetry run playwright install --with-deps

# Copy project files
COPY . .

# Run FastAPI application with uvicorn on host 0.0.0.0 and port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]