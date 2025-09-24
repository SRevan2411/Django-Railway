FROM python:3.12.0-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000


CMD sh -c "gunicorn DjangoApp.wsgi:application --bind 0.0.0.0:${PORT:-8000}"