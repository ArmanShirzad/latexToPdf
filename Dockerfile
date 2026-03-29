FROM python:3.11-slim

# Prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install TeX Live (adjust packages based on your templates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-xetex \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
# We use the existing requirements.txt. Some packages in it (like PyQT5) might fail or be unnecessary for a pure API server,
# but we'll try to install them or you can clean it up further later.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Expose port 80
EXPOSE 80

# Command to run the API via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
