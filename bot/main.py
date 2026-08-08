import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import uvicorn

from config import settings
from handlers import router
from api import app as fastapi_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
dp = Dispatcher()
dp.include_router(router)

async def start_bot():
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ])
    logger.info("🤖 Bot polling started")
    await dp.start_polling(bot)

async def main():
    bot_task = asyncio.create_task(start_bot())
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"🚀 FastAPI starting on port {port}")
    await server.serve()
    bot_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())