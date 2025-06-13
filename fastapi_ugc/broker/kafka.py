from aiokafka import AIOKafkaProducer

from src.core.config import kafka_settings

kafka_producer = AIOKafkaProducer(bootstrap_servers=kafka_settings.host)
