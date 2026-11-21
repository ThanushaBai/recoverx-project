FROM python:3.11-slim
WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

# Patch the zlib1g vulnerability (CVE-2026-85091)
RUN apt-get update && apt-get install -y --no-install-recommends zlib1g && rm -rf /var/lib/apt/lists/*

# Remove build tools (pip, setuptools, wheel) to eliminate CVEs
RUN pip uninstall -y pip setuptools wheel && \
    rm -rf /usr/local/lib/python3.11/site-packages/pip* \
           /usr/local/lib/python3.11/site-packages/setuptools* \
           /usr/local/lib/python3.11/site-packages/wheel* \
           /usr/local/lib/python3.11/site-packages/_distutils_hack

COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
