import logging

import requests
from django.conf import settings

try:
    from celery import shared_task
except ModuleNotFoundError:

    def shared_task(*dargs, **dkwargs):
        def decorator(func):
            def delay(*args, **kwargs):
                return func(*args, **kwargs)

            func.delay = delay
            return func

        if dargs and callable(dargs[0]):
            return decorator(dargs[0])
        return decorator


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=10,
    max_retries=5,
)
def send_order_notification(self, order_id: int):
    from .models import Order

    try:
        order = Order.objects.select_related("user").get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s not found for notification", order_id)
        return

    telegram_id = getattr(order.user, "telegram_id", None)
    if not telegram_id:
        logger.info("User %s has no telegram_id, skipping notification", order.user_id)
        return

    message = f"Оформлен новый заказ! #{order.id} на {order.product_name}"
    logger.info("Sending order %s notification to Telegram", order.id)
    response = requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": telegram_id, "text": message},
        timeout=10,
    )
    response.raise_for_status()
    logger.info(
        "Telegram responded with %s for order %s", response.status_code, order.id
    )
