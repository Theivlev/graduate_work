FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/elastic

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=web:web . .

RUN chmod +x elastic.sh

RUN echo "Содержимое директории /opt/elastic:" && ls -la /opt/elastic


CMD ["bash", "elastic.sh"]
