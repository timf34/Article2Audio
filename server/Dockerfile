# server/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . .
EXPOSE 8001
CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]
