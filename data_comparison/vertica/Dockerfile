FROM python:3.12-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/vertica

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=web:web . .

RUN chmod +x vertica.sh

RUN echo "Содержимое директории /opt/vertica" && ls -la /opt/vertica


CMD ["bash", "vertica.sh"]
