FROM python:3.11-slim

WORKDIR /app

# Copy requirements first and install before copying the rest of the code.
# Docker caches this layer — if you change app code but not requirements.txt,
# rebuilds skip re-downloading every package, making them much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8000

# --host 0.0.0.0 is required inside Docker — without it, the server only
# listens on the container's internal loopback and is unreachable from outside,
# even with port mapping set up correctly.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
