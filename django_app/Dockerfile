FROM python:3.12-slim

# Install System Packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    fonts-nanum \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set WORKDIR
WORKDIR /blogi-backend/django_app

# install poetry
RUN pip install --upgrade pip && pip install poetry

# Set poetry environment
RUN poetry config virtualenvs.create false

# copy poetry setting files
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN poetry install --no-interaction --no-root

# copy project files
COPY . .