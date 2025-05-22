#! /bin/bash -x

echo "Проверка доступности брокеров Kafka..."
brokers="kafka-0:9093 kafka-1:9093 kafka-2:9093"

for broker in $brokers; do
    echo "Обработка брокера: $broker..."
    IFS=":" read -r host port <<< "$broker"
    echo "Парсинг: хост - $host, порт - $port"

    if [ -z "$host" ] || [ -z "$port" ]; then
        echo "Ошибка: не удалось распарсить строку брокера: $broker"
        exit 1
    fi

    echo "Проверка доступности брокера: $host:$port..."
    until nc -z -v -w5 "$host" "$port"; do
        echo "Ожидание доступности $host:$port..."
        sleep 5
    done
    echo "Брокер $broker доступен!"
done

echo "Все брокеры доступны. Ожидание 30 секунд ClickHouse ETL..."

sleep 30

echo "Запуск процесса ClickHouse ETL..."

python src/main.py
