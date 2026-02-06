from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON
from typing import List
from db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    reg_date: Mapped[datetime] = mapped_column(DateTime)
    subscription: Mapped["Subscription"] = relationship(
        back_populates="user",
        uselist=False
    )


class Subscription(Base):

    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    subs_tg_id: Mapped[int] = mapped_column(unique=True)
    key: Mapped[str] = mapped_column(String, nullable=False)

    uuid: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    expired: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='subscription')

