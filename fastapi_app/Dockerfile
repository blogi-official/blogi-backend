FROM python:3.12-slim

# ----------------------------
# 🧱 1. Install System Packages (Java + build tools)
# ----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    openjdk-17-jdk \
    fonts-nanum \
    g++ \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ----------------------------
# 🌍 2. Set JAVA environment (필수!)
# ----------------------------
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# ----------------------------
# 📂 3. Set WORKDIR
# ----------------------------
WORKDIR /blogi-backend/fastapi_app

# ----------------------------
# 📦 4. Install poetry
# ----------------------------
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false

# ----------------------------
# 📄 5. Copy poetry setting & install deps
# ----------------------------
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root

# ----------------------------
# 🧪 6. Install Playwright
# ----------------------------
RUN poetry run playwright install --with-deps

# ----------------------------
# 📁 7. Copy app files
# ----------------------------
COPY . .

# ----------------------------
# 🚀 8. Start FastAPI
# ----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
