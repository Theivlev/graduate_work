from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from typing import List, Callable
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
            self,
            mongo_uri: str,
            database: str = 'scheduler_db',
            collection: str = 'jobs',
            timezone: str = "UTC",
            default_job_kwargs: dict = None,
    ):
        """
        Инициализирует асинхронный планировщик с MongoDB в качестве хранилища задач.
        """
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        jobstore = MongoDBJobStore(
            host=mongo_uri,
            database=database,
            collection=collection
        )
        self.scheduler.add_jobstore(jobstore)
        self.default_job_kwargs = default_job_kwargs or {}

    def add_job(
            self,
            func: Callable,
            trigger: str = 'interval',
            **trigger_args,
    ):
        """
        Добавляет задачу в планировщик.
        """
        job_kwargs = {**self.default_job_kwargs, 'trigger': trigger, **trigger_args}
        self.scheduler.add_job(func, **job_kwargs)
        logger.info(f"Добавлена задача: {func.__name__}, триггер: {trigger}, параметры: {trigger_args}")

    def start(self):
        """Запускает планировщик задач."""
        if self.scheduler.running:
            logger.warning("Планировщик уже запущен.")
            return
        try:
            self.scheduler.start()
            logger.info('Планировщик задач успешно запущен')
        except Exception as e:
            logger.error(f"Ошибка запуска планировщика: {e}")
            raise

    def stop(self, wait: bool = True):
        if not self.scheduler.running:
            logger.info('Планировщик уже остановлен')
            return

        try:
            self.scheduler.shutdown(wait=wait)
            logger.info("Планировщик задач успешно остановлен.")
        except Exception as e:
            logger.error(f"Ошибка остановки планировщика: {e}")
            raise

    def list_jobs(self) -> List:
        """Возвращает список активных задач."""
        return self.scheduler.get_jobs()


scheduler = Scheduler(
    mongo_uri="mongodb://notifications_mongo_db:27017",
    database="scheduler_db",
    collection="jobs",
    timezone="Europe/Moscow",
    default_job_kwargs={"misfire_grace_time": 60}
)