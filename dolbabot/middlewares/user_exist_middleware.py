from datetime import datetime, timedelta
from utils.logger import logger
from db.handlers import telegram_user_handler


CHECK_INTERVAL = timedelta(minutes=60)  # можешь поменять на 60, 1440 и т.д.


async def user_middleware(update, context):
    tg_user = update.effective_user
    if not tg_user:
        return

    cached_user = context.user_data.get("user")
    last_check = context.user_data.get("last_user_check")

    if cached_user and last_check and datetime.now() - last_check < CHECK_INTERVAL:
        return

    db_user = telegram_user_handler.get_one(id=tg_user.id)

    if not db_user:
        logger.info(f"ADD: {tg_user.id} to database")
        db_user = telegram_user_handler.create(
            id=tg_user.id,
            name=tg_user.full_name,
            telegram_tag=tg_user.username or str(tg_user.id),
        )
    else:
        new_name = tg_user.full_name
        new_tag = tg_user.username or str(tg_user.id)

        update_fields = {}

        if db_user.name != new_name:
            update_fields["name"] = new_name

        if db_user.telegram_tag != new_tag:
            update_fields["telegram_tag"] = new_tag

        if update_fields:
            try:
                telegram_user_handler.update(
                    filters={"id": db_user.id},
                    updates=update_fields,
                )
                logger.info(f"UPDATED USER {db_user.id} fields: {update_fields}")
            except Exception as e:
                logger.error(f"Ошибка при обновлении пользователя {db_user.id}: {e}")

    context.user_data["user"] = {
        "id": tg_user.id,
        "name": db_user.name,
        "telegram_tag": db_user.telegram_tag,
        "is_admin": db_user.is_admin,
    }
    context.user_data["last_user_check"] = datetime.now()
