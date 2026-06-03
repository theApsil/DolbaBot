from dataclasses import dataclass
from datetime import datetime

from db.handlers.model_handlers import bank_account_handler, transaction_handler
from utils.calculator import evaluate


class AccountError(Exception): ...
class AccountNotFound(AccountError): ...
class InvalidExpression(AccountError): ...

class TxCancelError(Exception): ...
class TxNotFound(TxCancelError): ...
class TxAlreadyChecked(TxCancelError): ...
class TxAccountMissing(TxCancelError): ...


@dataclass
class DepositResult:
    tx_id: int
    amount: float
    decimals: int
    new_balance: float
    account_name: str


@dataclass
class CancelResult:
    amount: float
    decimals: int
    new_balance: float
    account_name: str


def deposit(group_id, account_name: str, expression: str, user_id: int) -> DepositResult:
    account = bank_account_handler.get_one(account_name=account_name, group_id=group_id)
    if not account:
        raise AccountNotFound(account_name)

    try:
        amount = round(float(evaluate(expression)), account.decimals)
    except Exception as e:
        raise InvalidExpression(str(e)) from e

    new_balance = (account.amount or 0) + amount
    bank_account_handler.update(
        filters={"group_id": group_id, "account_name": account_name},
        updates={"amount": new_balance},
    )
    tx = transaction_handler.create(
        amount=amount,
        date=datetime.now().date(),
        user_request=expression,
        user_id=user_id,
        balance=new_balance,
        bank_account_id=account.id,
        is_checked=False,
    )
    return DepositResult(
        tx_id=tx.id,
        amount=amount,
        decimals=account.decimals,
        new_balance=new_balance,
        account_name=account.account_name,
    )


def cancel_transaction(transaction_id) -> CancelResult:
    tx = transaction_handler.get_one(id=transaction_id)
    if not tx:
        raise TxNotFound
    if tx.is_checked:
        raise TxAlreadyChecked

    account = bank_account_handler.get_one(id=tx.bank_account_id)
    if not account:
        raise TxAccountMissing

    new_balance = (account.amount or 0) - tx.amount

    bank_account_handler.update(
        filters={"id": account.id}, updates={"amount": new_balance},
    )
    transaction_handler.update(
        filters={"id": tx.id},
        updates={"user_request": f"[Отмена] {tx.user_request}"},
    )
    return CancelResult(
        amount=tx.amount,
        decimals=account.decimals,
        new_balance=new_balance,
        account_name=account.account_name,
    )


def reconcile_group(group_id) -> int:
    """Переносит все непроверенные транзакции группы в историю."""
    accounts = bank_account_handler.filter_many(group_id=group_id)
    count = 0
    for account in accounts:
        count += transaction_handler.transfer_to_history(
            filters={"is_checked": False, "bank_account_id": account.id},
        )
    return count