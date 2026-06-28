#!/bin/sh
echo "Starting Qdrant..."
/qdrant/qdrant &

# Give Qdrant a few seconds to bind its port before the backend tries to connect.
# The backend's own connect_to_qdrant() also retries, so this is just a head start.
sleep 3

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
