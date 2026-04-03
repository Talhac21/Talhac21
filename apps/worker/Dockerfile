FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .[dev]
COPY worker ./worker
COPY tests ./tests
CMD ["python", "-m", "worker.main"]
