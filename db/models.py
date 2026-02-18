from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, BigInteger
from db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    reg_date: Mapped[datetime] = mapped_column(DateTime)
    referal_count: Mapped[int] = mapped_column(Integer)

    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="user",uselist=False)
    shop: Mapped['Shoping']  = relationship('Shoping', back_populates='user')
    referal: Mapped['Referal'] = relationship('Referal', back_populates='user')
    vpn_account: Mapped['Vpn_Account'] = relationship('Vpn_Account', back_populates='user')


class Subscription(Base):

    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    subs_tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[bool] = mapped_column(String)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='subscription')

class Vpn_Account(Base):

    __tablename__ = 'vpn_accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String, nullable=False)
    uuid: Mapped[str] = mapped_column(String)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='vpn_account')

class Shoping(Base):

    __tablename__ = 'shoping'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    money: Mapped[int] = mapped_column(Integer) 
    shop_date: Mapped[str] = mapped_column(String)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='shop')
    

class Referal(Base):
    __tablename__ = 'referals'

    id: Mapped[int] = mapped_column(primary_key=True)
    invited_by_tg_id: Mapped[int] = mapped_column(BigInteger)
    ref_tg_id: Mapped[int] = mapped_column(unique=True)
    bonus_given: Mapped[bool] = mapped_column(Boolean, default=False) 

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='referal')
    