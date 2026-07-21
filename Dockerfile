FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libjpeg62-turbo-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

ENV DJANGO_SETTINGS_MODULE=trackant.settings_docker
RUN python manage.py collectstatic --noinput 2>/dev/null || true

RUN mkdir -p /root/.trackant

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "trackant.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
