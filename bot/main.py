import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fastapi import FastAPI

from config import settings
from handlers import router
from api import app as fastapi_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для бота
bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
dp = Dispatcher()
dp.include_router(router)

async def start_bot():
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])
    await dp.start_polling(bot)

async def main():
    # Запускаем бота и FastAPI параллельно
    import threading

    # FastAPI в отдельном потоке
    def run_api():
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Бот в основном потоке
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())
