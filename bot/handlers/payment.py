from aiogram import Router, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery
from config import settings
from sqlalchemy import select
from bot.dao.database import async_session_maker
from bot.dao.models import Product, Purchase, User

router = Router()


@router.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: CallbackQuery):
    await callback.answer()

    product_id = int(callback.data.split("_")[1])

    async with async_session_maker() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one()

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=product.name,
        description="Покупка товара",
        payload=str(product.id),
        provider_token=settings.PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=product.name, amount=product.price * 100)]
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    product_id = int(message.successful_payment.invoice_payload)

    async with async_session_maker() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = user_result.scalar_one()

        product_result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one()

        purchase = Purchase(
            user_id=user.id,
            product_id=product_id,
            payment_id=message.successful_payment.telegram_payment_charge_id
        )

        session.add(purchase)
        await session.commit()

    await message.answer(
        f"✅ Оплата успешна!\n\n📦 Твой товар:\n{product.hidden_content}"
    )