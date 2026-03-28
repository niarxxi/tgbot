from sqlalchemy import select
from bot.dao.database import async_session_maker
from bot.dao.models import User


async def get_or_create_user(telegram_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()

        return user