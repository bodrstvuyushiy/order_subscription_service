# Order Subscription Service

Мини‑платформа для оформления заказов по подписке:

- Django REST API, Redis‑кеш и Celery‑воркер для уведомлений.
- Telegram‑бот, который связывает аккаунт по телефону.
- Docker Compose поднимает PostgreSQL, Redis, web и worker сервисы.


- `GET /api/products/` – публичный каталог товаров (кешируется 5 минут в Redis)
- `GET /api/products/<id>/` – детальная карточка
- `GET /api/orders/` – заказы текущего пользователя
- `POST /api/orders/` – оформить заказ `{product_name, quantity}`
- `GET/PATCH/DELETE /api/orders/<id>/` – управление своим заказом (staff видит все)

При создании заказа Celery‑воркер отправляет уведомление в Telegram.

### Subscriptions

- `GET /api/subscriptions/` – публичный список планов (возвращает цену, тип тарифа, скидку и `price_with_discount`)
- `GET /api/subscriptions/<id>/` – конкретный план
- `GET /api/subscriptions/user-subscriptions/` – активная подписка пользователя
- `POST /api/subscriptions/user-subscriptions/` – покупка подписки `{subscribe_type}`
- `GET/PATCH/DELETE /api/subscriptions/user-subscriptions/<id>/` – управление подпиской

### Telegram bot

Находится в `bot/bot.py`. Слушает входящие сообщения, ищет пользователя по номеру телефона и сохраняет `telegram_id`, чтобы уведомления из Celery доходили в чат.


## Структура

```
src/
  apps/
    products/        # товары и заказы, Celery таск
    subscriptions/   # планы и пользовательские подписки
    users/           # кастомная модель пользователя
  core/              # настройки Django, celery, urls
bot/                 # Telegram бот
docker-compose.yml   # web + redis + postgres + celery + bot
Makefile             # команды для dev/workflow
tests/api            # интеграционные тесты API
```

