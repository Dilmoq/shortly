# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app app

# Data location for the SQLite database inside the container,
# mount a volume here to persist it across restarts.
ENV SHORTLY_DATABASE_URL=sqlite:////data/shortly.db \
    SHORTLY_BASE_URL=http://localhost:8000/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
