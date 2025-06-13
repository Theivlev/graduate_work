import aio_pika

from core.config import mail_queue_settings


async def setup_rabbit(connection):
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    mail_exchange = await channel.declare_exchange(mail_queue_settings.mail_exchange, aio_pika.ExchangeType.DIRECT)
    retry_exchange = await channel.declare_exchange(mail_queue_settings.retry_exchange, aio_pika.ExchangeType.DIRECT)
    failed_exchange = await channel.declare_exchange(mail_queue_settings.failed_exchange, aio_pika.ExchangeType.DIRECT)

    mail_queue = await channel.declare_queue(
        mail_queue_settings.mail_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": mail_queue_settings.retry_exchange,
            "x-dead-letter-routing-key": mail_queue_settings.retry_routing_key,
        },
    )

    retry_queue = await channel.declare_queue(
        mail_queue_settings.retry_queue,
        durable=True,
        arguments={
            "x-message-ttl": 60000,
            "x-dead-letter-exchange": mail_queue_settings.mail_exchange,
            "x-dead-letter-routing-key": mail_queue_settings.retry_routing_key,
        },
    )

    failed_queue = await channel.declare_queue(
        mail_queue_settings.failed_queue,
        durable=True,
    )

    await mail_queue.bind(mail_exchange, routing_key=mail_queue_settings.mail_routing_key)
    await retry_queue.bind(retry_exchange, routing_key=mail_queue_settings.retry_routing_key)
    await failed_queue.bind(failed_exchange, routing_key=mail_queue_settings.failed_routing_key)

    return channel, mail_queue, failed_queue
