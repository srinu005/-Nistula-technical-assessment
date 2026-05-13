FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
# 1. Prevents Python from writing .pyc files to disc
# 2. Ensures console output is sent straight to terminal (no buffering)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/nistula_user/.local/bin:$PATH"

# Install system dependencies
# build-essential is required for compiling C-extensions in packages like asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r nistula && useradd -r -g nistula nistula_user

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Adjust permissions so our non-root user can access the app files
RUN chown -R nistula_user:nistula /app

# Switch to the non-root user
USER nistula_user

# Expose the port FastAPI runs on
EXPOSE 8000

# Use 'fastapi run' (provided by fastapi[standard])
# This handles production-grade serving automatically
CMD ["fastapi", "run", "main.py", "--port", "8000"]