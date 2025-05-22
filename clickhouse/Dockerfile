FROM python:3.12

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/click_house_etl

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=web:web . .

RUN chmod +x click_house.sh

RUN echo "Содержимое директории /opt/click_house_etl" && ls -la /opt/click_house_etl


CMD ["bash", "click_house.sh"]
