FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run the manifold sweep precompute
CMD ["python", "-m", "precompute.manifold_sweep"]
