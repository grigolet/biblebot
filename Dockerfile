# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY . .

# Install dependencies with uv
RUN uv sync --frozen

# Set environment variables (override with .env or at runtime)
ENV OPENAI_API_KEY=""
ENV TELEGRAM_BOT_TOKEN=""

# Entrypoint
CMD ["uv", "run", "python", "bot.py"]
