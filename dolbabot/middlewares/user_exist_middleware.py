from db.models import User
from db.handlers import telegram_user_handler
from utils.logger import logger


async def user_middleware(update, context):
    """Промежуточная функция, проверяющая и создающая пользователя."""
    user = update.effective_user

    user_exist = context.user_data.get('user_exist')
    if user_exist:
        return

    db_user = telegram_user_handler.get_one(id=user.id)

    if not db_user:
        logger.info(f"ADD: {user.id} to database")
        db_user = telegram_user_handler.create(
            id=user.id,
            name=update.effective_user.full_name,
            telegram_tag=user.username or str(user.id),
        )

    context.user_data["user_exists"] = True
    context.user_data["user"] = {
        "id": db_user.id,
        "name": db_user.name,
        "telegram_tag": db_user.telegram_tag
    }
