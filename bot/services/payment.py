from aiogram import Router, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery

router = Router()

PROVIDER_TOKEN = "381764678:TEST:172962"


@router.message(F.text.startswith("buy"))
async def buy_product(message: Message):
    price = 100  # тестовая цена

    await message.answer_invoice(
        title="🔥 VIP доступ",
        description="Тестовая покупка",
        payload="vip_access",
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="VIP", amount=price * 100)]
    )