#!/usr/bin/env bash
set -e

echo "Waiting for PostgreSQL to be ready..."
python << END
import time
import asyncpg
import asyncio
import os

dsn = os.environ.get("POSTGRES_DSN")
if dsn:
    async def wait_for_db():
        while True:
            try:
                conn = await asyncpg.connect(dsn)
                await conn.close()
                break
            except Exception as e:
                print(f"PostgreSQL is not ready yet: {e}. Sleeping...")
                time.sleep(2)

    asyncio.run(wait_for_db())
    print("PostgreSQL is up!")
END
# === ДОБАВЛЯЕМ СОЗДАНИЕ СХЕМЫ AUTH ===
echo "Ensuring schema 'auth' exists..."
python << END
import asyncpg
import asyncio
import os

dsn = os.environ.get("POSTGRES_DSN")
if dsn:
    async def create_schema():
        conn = await asyncpg.connect(dsn)
        await conn.execute('CREATE SCHEMA IF NOT EXISTS auth;')
        await conn.close()
        print("Schema 'auth' ensured.")

    asyncio.run(create_schema())
END

# Запуск переданного процесса (с переменными окружения)
echo "Starting main process: $@"
exec "$@"
