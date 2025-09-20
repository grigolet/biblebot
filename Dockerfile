# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Set environment variables (override with .env or at runtime)
ENV OPENAI_API_KEY=""
ENV TELEGRAM_BOT_TOKEN=""

# Entrypoint
CMD ["python", "bot.py"]
