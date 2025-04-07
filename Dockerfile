FROM python:3.11-slim

# System dependencies + Upgrade pip the safe way
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    python -m ensurepip --upgrade && \
    python -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose port (Render will use PORT env var)
EXPOSE 10000

# Start with gunicorn and use $PORT
CMD ["gunicorn", "app:app", "--workers", "3", "--bind=0.0.0.0:$PORT", "--timeout", "300"]
