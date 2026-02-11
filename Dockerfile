# Stage 1: Build Tailwind CSS
FROM node:20-slim AS css-builder
WORKDIR /build
COPY package.json ./
RUN npm install
COPY static/css/main.css static/css/main.css
COPY templates/ templates/
RUN npx @tailwindcss/cli -i static/css/main.css -o static/css/output.css --minify

# Stage 2: Python runtime
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . .
COPY --from=css-builder /build/static/css/output.css static/css/output.css

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "120"]
