from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete

from bot.dao.database import async_session_maker
from bot.dao.models import Product, Purchase
from bot.filters.admin import IsAdmin
from bot.handlers.start import get_main_keyboard

router = Router()


# ================= FSM =================

class AddProduct(StatesGroup):
    name = State()
    price = State()
    content = State()


# ================= КНОПКИ =================

def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить", callback_data="admin_add"),
                InlineKeyboardButton(text="📋 Список", callback_data="admin_list"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data="admin_delete")
            ]
        ]
    )


def cancel_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )


# ================= МЕНЮ =================

@router.message(IsAdmin(), F.text.in_(["/admin", "⚙️ Админ Панель"]))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚙️ Админ панель", reply_markup=admin_keyboard())


# ================= ОТМЕНА =================

@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Действие отменено",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


# ================= НАЗАД =================

@router.message(F.text == "⬅️ Назад")
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AddProduct.price.state:
        await message.answer("Введите название товара:", reply_markup=cancel_back_keyboard())
        await state.set_state(AddProduct.name)

    elif current_state == AddProduct.content.state:
        await message.answer("Введите цену:", reply_markup=cancel_back_keyboard())
        await state.set_state(AddProduct.price)

    else:
        await state.clear()
        await message.answer(
            "⬅️ Возврат в меню",
            reply_markup=get_main_keyboard(message.from_user.id)
        )


# ================= ДОБАВИТЬ =================

@router.callback_query(IsAdmin(), F.data == "admin_add")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Введите название товара:",
        reply_markup=cancel_back_keyboard()
    )
    await state.set_state(AddProduct.name)
    await callback.answer()


@router.message(AddProduct.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену:", reply_markup=cancel_back_keyboard())
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число")
        return

    await state.update_data(price=int(message.text))
    await message.answer("Введите контент:", reply_markup=cancel_back_keyboard())
    await state.set_state(AddProduct.content)


@router.message(AddProduct.content)
async def add_content(message: Message, state: FSMContext):
    data = await state.get_data()

    async with async_session_maker() as session:
        product = Product(
            name=data["name"],
            price=data["price"],
            hidden_content=message.text
        )
        session.add(product)
        await session.commit()

    await state.clear()

    await message.answer(
        "✅ Товар добавлен",
        reply_markup=get_main_keyboard(message.from_user.id)
    )


# ================= СПИСОК =================

@router.callback_query(IsAdmin(), F.data == "admin_list")
async def list_products(callback: CallbackQuery):
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        await callback.message.answer("❌ Товаров нет")
        await callback.answer()
        return

    text = "\n\n".join(
        f"ID: {p.id}\n{p.name} — {p.price}₽"
        for p in products
    )

    await callback.message.answer(text)
    await callback.answer()


# ================= УДАЛЕНИЕ =================

@router.callback_query(IsAdmin(), F.data == "admin_delete")
async def delete_menu(callback: CallbackQuery):
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        await callback.message.answer("❌ Нет товаров")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{p.name} ❌",
                    callback_data=f"del_{p.id}"
                )
            ]
            for p in products
        ]
    )

    await callback.message.answer("Выбери товар для удаления:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(IsAdmin(), F.data.startswith("del_"))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])

    async with async_session_maker() as session:
        await session.execute(delete(Purchase).where(Purchase.product_id == product_id))
        await session.execute(delete(Product).where(Product.id == product_id))
        await session.commit()

    await callback.message.answer("🗑 Товар удалён")
    await callback.answer()