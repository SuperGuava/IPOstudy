FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      "fastapi>=0.115.0,<1.0.0" \
      "sqlalchemy>=2.0.0,<3.0.0" \
      "alembic>=1.13.0,<2.0.0" \
      "psycopg[binary]>=3.1.0,<4.0.0" \
      "uvicorn>=0.30.0,<1.0.0"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
