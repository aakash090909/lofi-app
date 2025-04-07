# Base image with Python and FFmpeg
FROM python:3.11-slim

# Install ffmpeg and other dependencies
RUN apt-get update &&     apt-get install -y ffmpeg &&     pip install --upgrade pip
RUN pip install --upgrade pip==25.0.1

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 10000

# Start the app with more workers and higher timeout
CMD ["gunicorn", "app:app", "--workers", "3", "--bind", "0.0.0.0:10000", "--timeout", "300"]
