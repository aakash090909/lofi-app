# Base image with Python and FFmpeg
FROM python:3.11-slim

# Install ffmpeg and other dependencies
RUN apt-get update &&     apt-get install -y ffmpeg &&     pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 10000

# Start the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "180"]