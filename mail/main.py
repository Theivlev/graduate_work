import asyncio
import logging

import aio_pika
import backoff
from aio_pika.exceptions import AMQPConnectionError, ChannelClosed, ConnectionClosed
from core.config import rabbit_settings
from core.rabbit import setup_rabbit
from services.consumers import on_failed_message, on_message

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, (AMQPConnectionError, ConnectionClosed, ChannelClosed))
async def main():
    connection = await aio_pika.connect_robust(
        login=rabbit_settings.user,
        password=rabbit_settings.password,
        host=rabbit_settings.host,
        port=rabbit_settings.port,
        virtual_host="/",
    )
    async with connection:
        channel = await connection.channel()

        channel, mail_queue, failed_queue = await setup_rabbit(connection)

        await mail_queue.consume(lambda msg: on_message(msg, channel))
        await failed_queue.consume(on_failed_message)
        logger.info("Ожидаем сообщений...")

        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == "__main__":
    logger.info("Старт сервиса")
    asyncio.run(main())
