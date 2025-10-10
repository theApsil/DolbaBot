from sqlalchemy import (
    Column, Integer, String, Date, Float, ForeignKey, Table, Boolean
)
from sqlalchemy.orm import (
    relationship, declarative_base
)

Base = declarative_base()

user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    telegram_tag = Column(String)

    groups = relationship("Group", secondary=user_group, back_populates="users", passive_deletes=True)

    transactions = relationship("Transaction", back_populates="user", passive_deletes=True)
    transaction_history = relationship("TransactionHistory", back_populates="user", passive_deletes=True)


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    telegram_tag = Column(String)

    users = relationship("User", secondary=user_group, back_populates="groups", passive_deletes=True)
    bank_accounts = relationship("BankAccount", back_populates="group", cascade="all, delete-orphan")


class BankAccount(Base):
    __tablename__ = "bank_account"

    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    amount = Column(Float)
    decimals = Column(Integer)
    group_id = Column(Integer, ForeignKey("group.id", ondelete="CASCADE"))

    group = relationship("Group", back_populates="bank_accounts")

    transactions = relationship("Transaction", back_populates="bank_account", cascade="all, delete-orphan")
    transaction_history = relationship("TransactionHistory", back_populates="bank_account", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    date = Column(Date)
    user_request = Column(String)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    balance = Column(Float)
    bank_account_id = Column(Integer, ForeignKey("bank_account.id", ondelete="CASCADE"))
    is_checked = Column(Boolean)

    user = relationship("User", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")


class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    date = Column(Date)
    user_request = Column(String)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    balance = Column(Float)
    bank_account_id = Column(Integer, ForeignKey("bank_account.id", ondelete="CASCADE"))
    is_checked = Column(Boolean)

    user = relationship("User", back_populates="transaction_history")
    bank_account = relationship("BankAccount", back_populates="transaction_history")
