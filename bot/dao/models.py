from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey
from bot.dao.database import Base


# ================= USER =================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    purchases: Mapped[list["Purchase"]] = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ================= PRODUCT =================

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    hidden_content: Mapped[str] = mapped_column(Text)

    purchases: Mapped[list["Purchase"]] = relationship(
        "Purchase",
        back_populates="product",
        cascade="all, delete-orphan"
    )


# ================= PURCHASE =================

class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )

    payment_id: Mapped[str]

    user: Mapped["User"] = relationship(
        "User",
        back_populates="purchases"
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="purchases"
    )