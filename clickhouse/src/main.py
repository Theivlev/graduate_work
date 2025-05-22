import asyncio
import logging

from etl.extract.kafka_read import KafkaReader
from etl.load.clickhouse_writer import ClickHouseWriter
from etl.transform.data_transform import MessagesTransformer
from utils.backoff import backoff

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
async def run_etl(writer: ClickHouseWriter, batch_size: int = 10):
    async with KafkaReader() as reader:
        transformer = MessagesTransformer()

        try:
            async for messages in reader.read(batch_size):
                transformed_messages = [msg async for msg in transformer.transform(messages)]

                if not transformed_messages:
                    logging.warning("Нет данных для записи после трансформации.")
                    continue

                await writer.write(transformed_messages)
                await reader.commit()
                logging.info(f"Успешно записано {len(transformed_messages)} сообщений в ClickHouse.")

                await asyncio.sleep(3)
        except Exception as e:
            logging.error(f"Ошибка при обработке батча: {e}")
            raise


async def main():
    while True:
        try:
            logging.info("Запуск ETL-процесса...")
            async with ClickHouseWriter() as writer:
                await run_etl(writer)
        except Exception as e:
            logging.error(f"Ошибка в ETL-процессе: {e}")
            logging.info("Повторная попытка через 5 секунд...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.info("Старт приложения ETL.")
    asyncio.run(main())
