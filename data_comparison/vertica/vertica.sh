#!/bin/bash

echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - Ожидание 5 минут перед запуском скрипта...ждем clickhouse_research"

sleep 900

echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - Ожидание завершено, запуск vertica_research.py..."

python vertica_research.py
