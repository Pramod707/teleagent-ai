FROM python:3.13-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python output from being buffered
ENV PYTHONUNBUFFERED=1

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies from the lock file
RUN uv sync --locked --no-dev

# Copy application code
COPY main.py .

# Start TeleAgent
CMD ["uv", "run", "--no-dev", "python", "main.py"]