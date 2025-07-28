FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# Install system dependencies (for pdfplumber and PyMuPDF)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY process_pdfs.py .

# Run the processor
CMD ["python", "process_pdfs.py"]
