import pandas as pd
from utils.logger import logger
from db.models import Transaction
from io import BytesIO

def create_dataframe_from_object(transactions: list[Transaction]) -> pd.DataFrame:
    """
    Возвращает pandas.DataFrame по результатам get_all_with_joins.
    """
    try:
        rows = []
        for t in transactions:
            rows.append({
                "ID Транзакции": str(t.id),
                "Дата": t.date,
                "Счёт": t.bank_account.account_name if t.bank_account else None,
                "Сумма": t.balance,
                "Пользователь": t.user.name if t.user else None,
                "Группа": t.bank_account.group.name if t.bank_account and t.bank_account.group else None,

                "Комментарий": t.user_request,
                "Остаток": t.balance
            })

        df = pd.DataFrame(rows)
        return df

    except Exception as e:
        logger.error(f"Ошибка при формировании DataFrame из транзакций: {e}")
        raise e


def create_temp_excel_file(df: pd.DataFrame) -> bytes:
    bytes_io = BytesIO()
    df.to_excel(bytes_io, index=False)
    bytes_io.seek(0)
    return bytes_io

