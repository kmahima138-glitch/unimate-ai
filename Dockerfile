FROM python:3.11-slim

# Install system dependencies needed for PyMuPDF and SQLite
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data directories exist
RUN mkdir -p data/uploads data/sample_docs data/chromadb

# Pre-seed sample university knowledge base
RUN python backend/scripts/seed_knowledge_base.py

# Expose port (default 8000)
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0
ENV APP_ENV=production

# Run using Uvicorn
CMD ["python", "run.py"]
