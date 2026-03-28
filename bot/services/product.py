from sqlalchemy import select
from bot.dao.database import async_session_maker
from bot.dao.models import Product


async def create_test_products():
    async with async_session_maker() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

        if products:
            return

        products = [
            Product(
                name="🔥 VIP доступ",
                price=100,
                hidden_content="🔐 https://vip-link.com"
            ),
            Product(
                name="💎 Премиум",
                price=200,
                hidden_content="💎 https://premium-link.com"
            ),
        ]

        session.add_all(products)
        await session.commit()