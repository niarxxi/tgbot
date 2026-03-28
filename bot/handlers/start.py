from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bot.services.user import get_or_create_user
from config import settings

router = Router()


def get_main_keyboard(user_id: int):
    if user_id in settings.admin_ids:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛒 Каталог")],
                [KeyboardButton(text="⚙️ Админ Панель")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛒 Каталог")]
            ],
            resize_keyboard=True
        )


@router.message(F.text == "/start")
async def start_handler(message: Message):
    await get_or_create_user(message.from_user.id)

    await message.answer(
        "👋 Добро пожаловать! Нажми на кнопку 🛒 Каталог",
        reply_markup=get_main_keyboard(message.from_user.id)
    )