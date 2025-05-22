import logging
import datetime
from datetime import timedelta
import asyncio
from src.service.notifications import get_notifications_service
from src.shemas.delivery import DeliveryDTO

MAX_RETRIES = 3
RETRY_DELAY = 1
TIMEZONE = "UTC"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def weekly_messages(expiration_days: int = 2, retry_count: int = MAX_RETRIES):
    """
    Асинхронная задача для отправки недельных уведомлений о популярных фильмах.
    """
    try:
        exp_date = datetime.datetime.now(tz=datetime.timezone.utc) + timedelta(days=expiration_days)
        delivery_data = DeliveryDTO(
            notification="popular_movies",
            data_store={
                "expiration_date": exp_date.strftime("%d-%m-%Y"),
                "timezone": TIMEZONE
            }
        )
        service = get_notifications_service()
        if not service:
            logger.error("Не удалось получить сервис уведомлений")
            return
        for attempt in range(retry_count + 1):
            try:
                await service.notification(delivery_data)
                logger.info(f"Уведомление '{delivery_data.notification}' успешно отправлено")
                break
            except Exception as e:
                if attempt < retry_count:
                    logger.warning(
                        f"Попытка {attempt + 1} отправить уведомление не удалась. Ошибка: {str(e)}. Повтор через {RETRY_DELAY} сек..."
                    )
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(
                        f"Не удалось отправить уведомление после {retry_count} попыток. Ошибка: {str(e)}"
                    )

    except Exception as outer_error:
        logger.error(f"Критическая ошибка в задаче weekly_messages: {str(outer_error)}", exc_info=True)