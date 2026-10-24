FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
RUN pip uninstall -y pip setuptools wheel && \
    rm -rf /usr/local/lib/python3.11/site-packages/pip* \
           /usr/local/lib/python3.11/site-packages/setuptools* \
           /usr/local/lib/python3.11/site-packages/wheel* \
           /usr/local/lib/python3.11/site-packages/_distutils_hack
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
