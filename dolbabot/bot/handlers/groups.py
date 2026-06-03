from telegram import Update
from telegram.ext import ContextTypes

from db.handlers import telegram_group_handler, user_group_handler

from ..constants import Msg
from ..decorators import admin_only
from ..keyboards import group_tag_kb


# === /группы ===

@admin_only
async def get_groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    groups_id = [ug.group_id for ug in user_group_handler.filter_many(user_id=user_id)]
    groups = telegram_group_handler.filter_many(id=groups_id)

    msg_lines = [
        "<b>Список групп:</b>",
        "<pre>",
        f"{'ID':<12} | {'Группа':<30} | {'Тег':<10}",
        "-" * 59,
    ]
    for group in groups:
        name = str(group.name) if group.name else "Без названия"
        tag = str(group.group_tag) if group.group_tag else "-"
        msg_lines.append(f"{group.id:<12} | {name:<30} | {tag:<10}")
    msg_lines.append("</pre>")

    await update.message.reply_text("\n".join(msg_lines), parse_mode="HTML")


# === /группа ===

@admin_only
async def change_group_tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_groups_ids = [
        g.group_id for g in user_group_handler.filter_many(user_id=user_id)
    ]

    args = update.message.text.split()[1:]
    if len(args) != 2:
        await update.message.reply_text(Msg.TAG_ARGS_REQUIRED)
        return

    group_id_arg, new_tag = args
    if len(new_tag) > 150:
        await update.message.reply_text(Msg.TAG_TOO_LONG)
        return
    if not new_tag.startswith("#"):
        await update.message.reply_text(Msg.TAG_MUST_START_HASH)
        return

    group = telegram_group_handler.get_one(id=group_id_arg)
    if not group:
        await update.message.reply_text(Msg.TAG_GROUP_NOT_EXISTS)
        return
    if int(group_id_arg) not in user_groups_ids:
        await update.message.reply_text(Msg.TAG_USER_NOT_IN)
        return

    msg = "\n".join((
        f"Вы собираетесь заменить тег у группы *{group.name}*",
        f"`{group.group_tag} -> {new_tag}`",
        f"Вы действительно хотите это сделать?",
    ))
    message = await update.message.reply_text(
        msg, parse_mode="Markdown", reply_markup=group_tag_kb(),
    )
    context.user_data[f"data_for_{message.message_id}"] = {
        "user_id": user_id,
        "group_id": group.id,
        "new_tag": new_tag,
    }