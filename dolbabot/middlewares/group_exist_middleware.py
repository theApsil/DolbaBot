from datetime import datetime, timedelta
from utils.logger import logger
from db.handlers import telegram_group_handler


GROUP_CHECK_INTERVAL = timedelta(minutes=60)  # настроено как у user_middleware


async def group_middleware(update, context):
    chat = update.effective_chat
    if not chat or chat.type == "private":
        return  # Нас не интересуют личные диалоги

    # Кэшируем группу так же, как пользователя
    cached_group = context.chat_data.get("group")
    last_check = context.chat_data.get("last_group_check")

    # Проверяем не чаще, чем интервал
    if cached_group and last_check and datetime.now() - last_check < GROUP_CHECK_INTERVAL:
        return

    db_group = telegram_group_handler.get_one(id=chat.id)

    if not db_group:
        logger.info(f"ADD GROUP: {chat.id} ({chat.title})")
        db_group = telegram_group_handler.create(
            id=chat.id,
            name=chat.title or "Без названия",
            telegram_tag=chat.username or None
        )
    else:
        update_fields = {}

        new_name = chat.title or "Без названия"
        new_tag = chat.username or None

        if db_group.name != new_name:
            update_fields["name"] = new_name

        if db_group.telegram_tag != new_tag:
            update_fields["telegram_tag"] = new_tag

        if update_fields:
            try:
                telegram_group_handler.update(
                    filters={"id": db_group.id},
                    updates=update_fields
                )
                logger.info(f"UPDATED GROUP {db_group.id}: {update_fields}")
            except Exception as e:
                logger.error(f"Ошибка при обновлении группы {db_group.id}: {e}")

    # Кэшируем группу, чтобы не перезапрашивать каждый апдейт
    context.chat_data["group"] = {
        "id": db_group.id,
        "name": db_group.name,
        "telegram_tag": db_group.telegram_tag
    }
    context.chat_data["last_group_check"] = datetime.now()
