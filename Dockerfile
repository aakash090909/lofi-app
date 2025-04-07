FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --upgrade pip==25.0.1

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["gunicorn", "app:app", "--workers", "3", "--bind=0.0.0.0:$PORT", "--timeout", "300"]
