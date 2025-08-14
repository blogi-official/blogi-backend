FROM python:3.12-slim-bookworm

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
# 🧪 6. Install Playwright + 필수 deps
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libgbm1 \
 && rm -rf /var/lib/apt/lists/* \
 && poetry run playwright install --with-deps

# ----------------------------
# 📁 7. Copy app files
# ----------------------------
COPY . .

# ----------------------------
# 🚀 8. Start FastAPI
# ----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
