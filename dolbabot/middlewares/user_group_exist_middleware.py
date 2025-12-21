from datetime import datetime, timedelta
from utils.logger import logger
from db.handlers import telegram_user_handler, telegram_group_handler, user_group_handler

CHECK_INTERVAL = timedelta(minutes=60)


async def user_group_middleware(update, context):
    """Middleware для управления связями пользователей и групп в Telegram"""
    if not update.effective_chat:
        return

    chat = update.effective_chat
    user = update.effective_user

    if not user:
        return

    # Работаем только в группах и супергруппах
    if chat.type not in ["group", "supergroup"]:
        return

    # Ключ для кэша
    cache_key = f"user_group_{chat.id}_{user.id}"
    cached = context.user_data.get(cache_key)
    last_check = context.user_data.get(f"{cache_key}_last_check")

    # Проверяем кэш
    if cached and last_check and datetime.now() - last_check < CHECK_INTERVAL:
        return

    try:
        # 1. Проверяем существование пользователя
        db_user = telegram_user_handler.get_one(id=user.id)
        if not db_user:
            # Пользователя нет - просто логируем и выходим
            logger.warning(f"User {user.id} not found in database. Skipping group link creation.")
            return

        # 2. Проверяем существование группы
        db_group = telegram_group_handler.get_one(id=chat.id)
        if not db_group:
            # Группы нет - просто логируем и выходим
            logger.warning(f"Group {chat.id} not found in database. Skipping group link creation.")
            return

        # 3. Проверяем/создаем связь user-group
        existing_link = user_group_handler.get_one(user_id=user.id, group_id=chat.id)

        if not existing_link:
            # Создаем связь
            user_group_handler.create(
                user_id=user.id,
                group_id=chat.id
            )
            logger.info(f"CREATED LINK: user {user.id} ({db_user.name}) -> group {chat.id} ({db_group.name})")
        else:
            logger.debug(f"Link exists: user {user.id} -> group {chat.id}")

        # 4. Сохраняем в кэш
        context.user_data[cache_key] = {
            "user_id": user.id,
            "group_id": chat.id,
            "timestamp": datetime.now().isoformat()
        }
        context.user_data[f"{cache_key}_last_check"] = datetime.now()

    except Exception as e:
        logger.error(f"Error in user_group_middleware for user {user.id}, group {chat.id}: {e}")


async def group_members_middleware(update, context):
    """Middleware для обработки новых участников группы"""
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    for new_member in update.message.new_chat_members:
        # Пропускаем ботов
        if new_member.is_bot:
            continue

        try:
            # Очищаем кэш для принудительной проверки
            cache_key = f"user_group_{chat.id}_{new_member.id}"
            context.user_data.pop(cache_key, None)
            context.user_data.pop(f"{cache_key}_last_check", None)

            logger.info(f"New member detected: {new_member.id} in group {chat.id}")

        except Exception as e:
            logger.error(f"Error processing new member {new_member.id} in group {chat.id}: {e}")


async def group_left_middleware(update, context):
    """Middleware для обработки выхода пользователя из группы"""
    if not update.message or not update.message.left_chat_member:
        return

    chat = update.effective_chat
    left_member = update.message.left_chat_member

    if chat.type not in ["group", "supergroup"]:
        return

    if left_member.is_bot:
        return

    try:
        # Удаляем связь
        deleted = user_group_handler.delete(user_id=left_member.id, group_id=chat.id)

        if deleted:
            logger.info(f"REMOVED LINK: user {left_member.id} from group {chat.id}")

        # Очищаем кэш
        cache_key = f"user_group_{chat.id}_{left_member.id}"
        context.user_data.pop(cache_key, None)
        context.user_data.pop(f"{cache_key}_last_check", None)

    except Exception as e:
        logger.error(f"Error removing user {left_member.id} from group {chat.id}: {e}")


async def group_migration_middleware(update, context):
    """Middleware для обработки миграции группы в супергруппу"""
    if not update.message or not update.message.migrate_from_chat_id or not update.message.migrate_to_chat_id:
        return

    old_chat_id = update.message.migrate_from_chat_id
    new_chat_id = update.message.migrate_to_chat_id

    try:
        # 1. Обновляем ID группы в базе
        group = telegram_group_handler.get_one(id=old_chat_id)
        if group:
            telegram_group_handler.update(
                filters={"id": old_chat_id},
                updates={"id": new_chat_id}
            )
            logger.info(f"Group migrated: {old_chat_id} -> {new_chat_id}")

        # 2. Обновляем все связи user-group
        # (зависит от реализации вашего user_group_handler)
        # Например:
        links = user_group_handler.get_group_links(old_chat_id)
        for link in links:
            link.group_id = new_chat_id
        if links:
            user_group_handler.session.commit()
            logger.info(f"Updated {len(links)} user-group links for migrated group")

        # 3. Очищаем весь кэш для старого chat_id
        keys_to_remove = [key for key in context.user_data.keys() if f"user_group_{old_chat_id}_" in key]
        for key in keys_to_remove:
            context.user_data.pop(key, None)

        logger.info(f"Cleared cache for migrated group {old_chat_id}")

    except Exception as e:
        logger.error(f"Error processing group migration {old_chat_id} -> {new_chat_id}: {e}")