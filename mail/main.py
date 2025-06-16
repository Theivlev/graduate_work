import asyncio
import logging

import aio_pika
import backoff
from aio_pika.exceptions import AMQPConnectionError, ChannelClosed, ConnectionClosed
from core.config import mail_queue_settings, rabbit_settings
from services.mail_consumers import on_failed_message, on_message
from services.recom_consumers import on_recom_message

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

        mail_queue = await channel.get_queue(mail_queue_settings.mail_queue)
        failed_queue = await channel.get_queue(mail_queue_settings.failed_queue)
        recom_queue = await channel.get_queue(mail_queue_settings.recom_queue)

        await mail_queue.consume(lambda msg: on_message(msg, channel))
        await failed_queue.consume(on_failed_message)
        await recom_queue.consume(lambda msg: on_recom_message(msg, channel))

        logger.info("Ожидаем сообщений...")
        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == "__main__":
    logger.info("Старт сервиса")
    asyncio.run(main())
