from sqlalchemy import (
    Column, Integer, String, Date, Float, ForeignKey, Table, Boolean, BigInteger, DateTime, func
)
from sqlalchemy.orm import (
    relationship, declarative_base
)


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True  # чтобы сам класс не создавал таблицу

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    telegram_tag = Column(String)

    groups = relationship("Group", secondary=user_group, back_populates="users", passive_deletes=True)

    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", passive_deletes=True)
    transaction_history = relationship("TransactionHistory", back_populates="user", passive_deletes=True)


class Group(BaseModel):
    __tablename__ = "group"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    telegram_tag = Column(String)

    users = relationship("User", secondary=user_group, back_populates="groups", passive_deletes=True)
    bank_accounts = relationship("BankAccount", back_populates="group", cascade="all, delete-orphan")


class BankAccount(BaseModel):
    __tablename__ = "bank_account"

    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    amount = Column(Float, default=0)
    decimals = Column(Integer)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"))
    group_id = Column(BigInteger, ForeignKey("group.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="bank_accounts")
    group = relationship("Group", back_populates="bank_accounts")

    transactions = relationship("Transaction", back_populates="bank_account", cascade="all, delete-orphan")
    transaction_history = relationship("TransactionHistory", back_populates="bank_account", cascade="all, delete-orphan")


class Transaction(BaseModel):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    date = Column(Date)
    user_request = Column(String)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    balance = Column(Float)
    bank_account_id = Column(BigInteger, ForeignKey("bank_account.id", ondelete="CASCADE"))
    is_checked = Column(Boolean)

    user = relationship("User", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")


class TransactionHistory(BaseModel):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    date = Column(Date)
    user_request = Column(String)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    balance = Column(Float)
    bank_account_id = Column(BigInteger, ForeignKey("bank_account.id", ondelete="CASCADE"))
    is_checked = Column(Boolean)

    user = relationship("User", back_populates="transaction_history")
    bank_account = relationship("BankAccount", back_populates="transaction_history")

class RegionIndex(BaseModel):
    __tablename__ = "region_index"

    id = Column(Integer, primary_key=True)
    city = Column(String,  unique=True)
    index = Column(Float)

    def __repr__(self):
        return "<RegionIndex(city='%s', index='%s')>" % (self.city, self.index)