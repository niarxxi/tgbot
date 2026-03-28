import asyncio
from aiogram import Bot, Dispatcher
from config import settings

from bot.handlers.start import router as start_router
from bot.handlers.shop import router as shop_router
from bot.handlers.payment import router as payment_router
from bot.handlers.admin import router as admin_router

from bot.services.product import create_test_products


async def on_startup():
    print("🚀 Бот запускается...")
    await create_test_products()
    print("✅ Товары готовы")


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(shop_router)
    dp.include_router(payment_router)

    await on_startup()

    print("🤖 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())