from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from bot.dao.database import async_session_maker
from bot.dao.models import Product

router = Router()


@router.message(F.text == "🛒 Каталог")
async def shop_handler(message: Message):
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        await message.answer("❌ Товары не найдены")
        return

    for product in products:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"💳 Купить за {product.price}₽",
                    callback_data=f"buy_{product.id}"
                )]
            ]
        )

        await message.answer(
            f"{product.name}\n💰 Цена: {product.price}₽",
            reply_markup=keyboard
        )