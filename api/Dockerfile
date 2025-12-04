FROM python:3.11-slim

# Install system deps (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Copy requirements from the build context (./api) and install

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
# Copy the API package into /app/api
COPY . /app/api

# Ensure /app is on PYTHONPATH so 'api' can be imported
ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
