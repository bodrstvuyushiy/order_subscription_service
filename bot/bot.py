import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy import create_engine, Table, MetaData

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
metadata = MetaData(bind=engine)
users = Table("users_customuser", metadata, autoload_with=engine)


def start(update):
    tg_id = update.message.chat_id
    update.message.reply_text("Привет! Отправь свой номер телефона для регистрации.")


def phone_handler(update):
    tg_id = update.message.chat_id
    phone = update.message.text.strip()

    with engine.begin() as conn:
        result = conn.execute(users.select().where(users.c.phone == phone)).first()
        if result:
            conn.execute(
                users.update()
                .where(users.c.id == result.id)
                .values(telegram_id=str(tg_id))
            )
            update.message.reply_text("Вы успешно зарегистрированы в системе!")
        else:
            update.message.reply_text("Пользователь с таким номером не найден.")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, phone_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
