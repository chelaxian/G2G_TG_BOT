import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from telegram.error import BadRequest

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка токена
with open("bot_token.txt", "r") as f:
    TOKEN = f.read().strip()

# Пути к файлам
USERS_FILE = "users.txt"
ADMINS_FILE = "admins.txt"

# Кэш состояний
states = {}

def load_groups(filename: str):
    try:
        with open(filename, "r") as f:
            groups = [line.strip() for line in f if line.strip()]
            if not groups:
                logger.warning(f"Файл {filename} пуст")
            return groups
    except Exception as e:
        logger.error(f"Ошибка чтения файла {filename}: {e}")
        return []

def update_file(filename: str, chat_id: str, add: bool = True):
    try:
        with open(filename, "r+") as f:
            ids = {line.strip() for line in f}
            if add:
                ids.add(chat_id)
            else:
                ids.discard(chat_id)
            f.seek(0)
            f.truncate()
            f.write("\n".join(ids))
        return True
    except Exception as e:
        logger.error(f"Error updating file {filename}: {e}")
        return False

async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Проверяет, является ли текущий чат админским, основываясь на списке групп из admins.txt.
    """
    chat_id = str(update.effective_chat.id)
    # Загружаем список админских групп
    admin_chats = set(load_groups(ADMINS_FILE))
    # Проверяем, входит ли текущий чат в список админских групп
    return chat_id in admin_chats

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        return
    await update.message.reply_text("Бот запущен и готов к работе!")

async def toggle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: bool):
    chat_id = str(update.effective_chat.id)
    user_chats = set(load_groups(USERS_FILE))
    admin_chats = set(load_groups(ADMINS_FILE))

    is_user_chat = chat_id in user_chats
    is_admin_chat = chat_id in admin_chats

    if not (is_user_chat or is_admin_chat):
        await update.message.reply_text("Эта команда доступна только в разрешенных группах.")
        return

    # Определяем тип группы
    group_type = "Пользовательская" if is_user_chat else "Админская"
    states[chat_id] = mode
    status = "ВКЛЮЧЕН" if mode else "ВЫКЛЮЧЕН"
    await update.message.reply_text(f"{group_type} режим отслеживания {status}")

async def on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await toggle_mode(update, context, True)

async def off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await toggle_mode(update, context, False)

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context):
        await update.message.reply_text("Эта команда доступна только в группах администраторов.")
        return
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("Использование: /all [текст сообщения]")
        return
    escaped_message = escape_markdownv2(message)
    admin = update.message.from_user
    header = f"Важное сообщение от администратора @{escape_markdownv2(admin.username)}\n\n"
    with open(USERS_FILE, "r") as f:
        user_chats = [line.strip() for line in f]
    for user_chat in user_chats:
        try:
            await context.bot.send_message(
                chat_id=user_chat,
                text=header + escaped_message,
                parse_mode='MarkdownV2'
            )
        except BadRequest as e:
            logger.error(f"BadRequest error while sending to {user_chat}: {e}")
            await update.message.reply_text(f"Ошибка при отправке сообщения в группу {user_chat}.")
        except Exception as e:
            logger.error(f"Unexpected error while sending to {user_chat}: {e}")
            await update.message.reply_text(f"Непредвиденная ошибка при отправке в группу {user_chat}.")
    await update.message.reply_text("Сообщение отправлено во все пользовательские группы")

async def get_groups_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context):
        await update.message.reply_text("Эта команда доступна только в группах администраторов.")
        return
    groups = []
    for filename in [USERS_FILE, ADMINS_FILE]:
        with open(filename, "r") as f:
            for chat_id in f.readlines():
                chat_id = chat_id.strip()
                if chat_id:
                    try:
                        chat = await context.bot.get_chat(chat_id)
                        title = escape_markdownv2(chat.title)
                        group_type = 'Пользовательская' if filename == USERS_FILE else 'Админская'
                        groups.append(f"{group_type} группа: *{title}* \nID: `{chat_id}`")
                    except Exception as e:
                        logger.error(f"Ошибка получения информации о чате {chat_id}: {e}")
    response = "Список групп:\n\n" + "\n\n".join(groups)
    await update.message.reply_text(response, parse_mode='MarkdownV2')

async def handle_group_management(update: Update, context: ContextTypes.DEFAULT_TYPE, file: str, add: bool):
    if not await check_admin(update, context):
        await update.message.reply_text("Эта команда доступна только в группах администраторов.")
        return
    chat_id = update.message.text.split()[-1]
    if not chat_id.startswith('-'):
        await update.message.reply_text("Неверный формат ID группы")
        return
    success = update_file(file, chat_id, add)
    action = "добавлена" if add else "удалена"
    if success:
        await update.message.reply_text(f"Группа {chat_id} {action}")
    else:
        await update.message.reply_text("Ошибка при обновлении списка групп")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        return
    chat_id = str(update.effective_chat.id)
    message = update.message

    # Проверка принадлежности чата к разрешенным группам
    user_chats = set(load_groups(USERS_FILE))
    admin_chats = set(load_groups(ADMINS_FILE))
    is_user_chat = chat_id in user_chats
    is_admin_chat = chat_id in admin_chats

    if not (is_user_chat or is_admin_chat):
        return

    # Обработка сообщений
    if is_user_chat:
        await handle_user_message(update, context)
    elif is_admin_chat:
        await handle_admin_message(update, context)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = str(update.effective_chat.id)

    # Проверка триггеров
    triggered = (
        message.reply_to_message and 
        message.reply_to_message.from_user.id == context.bot.id
    ) or (
        message.text and 
        (f"@{context.bot.username}" in message.text)
    ) or states.get(chat_id, False)
    if not triggered:
        return

    # Отправка сообщения админам
    admin_chats = load_groups(ADMINS_FILE)
    user = message.from_user
    chat = await context.bot.get_chat(chat_id)
    header = (
        f"Сообщение из группы *{escape_markdownv2(chat.title)}*\n"
        f"От: @{escape_markdownv2(user.username)}\n"
        f"ID: `{chat_id}`\n\n"
    )

    for admin_chat in admin_chats:
        try:
            await context.bot.send_message(
                chat_id=admin_chat,
                text=header + escape_markdownv2(message.text),
                parse_mode='MarkdownV2'
            )
        except BadRequest as e:
            logger.error(f"BadRequest error while sending to {admin_chat}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while sending to {admin_chat}: {e}")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = str(update.effective_chat.id)

    # Если сообщение содержит упоминание бота или включён режим /on,
    # выводим меню с кнопками для выбора пользовательской группы
    if (message.text and f"@{context.bot.username}" in message.text) or states.get(chat_id, False):
        user_chats = load_groups(USERS_FILE)
        if not user_chats:
            await update.message.reply_text("Список пользовательских групп пуст.")
            return
        keyboard = []
        keyboard.append([InlineKeyboardButton("Отправить всем", callback_data="send_to_all")])
        for user_chat in user_chats:
            try:
                chat = await context.bot.get_chat(user_chat)
                button_text = chat.title[:20]
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"send_to_group_{user_chat}")])
            except Exception as e:
                logger.error(f"Ошибка при получении информации о чате {user_chat}: {e}")
                continue
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите группу для отправки сообщения:", reply_markup=reply_markup)
        return

    # Обработка ответов на сообщения бота (например, когда админ отвечает на сообщение, отправленное ботом)
    if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        original_text = message.reply_to_message.text
        if "Сообщение из группы" in original_text:
            try:
                parts = original_text.split('\n')
                group_id = parts[2].split(': ')[-1].strip('`')  # Извлекаем ID группы
                admin = message.from_user
                header = (
                    f"Ответ из группы *{escape_markdownv2(update.effective_chat.title)}*\n"
                    f"От: @{escape_markdownv2(admin.username)}\n\n"
                )
                await context.bot.send_message(
                    chat_id=group_id,
                    text=header + escape_markdownv2(message.text),
                    parse_mode='MarkdownV2'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения в чат: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем данные кнопки
    action = query.data
    admin_chat_id = str(query.message.chat.id)

    # Проверяем, что это админская группа
    if not await check_admin(update, context):
        await query.edit_message_text("Эта функция доступна только в группах администраторов.")
        return

    # Загружаем список пользовательских групп
    user_chats = load_groups(USERS_FILE)
    if not user_chats:
        await query.edit_message_text("Список пользовательских групп пуст.")
        return

    # Получаем исходное сообщение админа
    original_message = query.message.reply_to_message
    if not original_message:
        await query.edit_message_text("Не удалось найти исходное сообщение.")
        return

    admin = original_message.from_user
    admin_chat = await context.bot.get_chat(admin_chat_id)
    header = f"Сообщение из админской группы *{escape_markdownv2(admin_chat.title)}*\nОт: @{escape_markdownv2(admin.username)}\n\n"
    message_text = header + escape_markdownv2(original_message.text)

    # Обработка нажатия кнопки
    if action == "send_to_all":
        for user_chat in user_chats:
            try:
                await context.bot.send_message(
                    chat_id=user_chat,
                    text=message_text,
                    parse_mode='MarkdownV2'
                )
            except BadRequest as e:
                logger.error(f"BadRequest error while sending to {user_chat}: {e}")
                await query.edit_message_text(f"Ошибка при отправке сообщения в группу {user_chat}.")
            except Exception as e:
                logger.error(f"Unexpected error while sending to {user_chat}: {e}")
                await query.edit_message_text(f"Непредвиденная ошибка при отправке в группу {user_chat}.")
        await query.edit_message_text("Сообщение отправлено во все пользовательские группы.")
    elif action.startswith("send_to_group_"):
        group_id = action.split("_")[-1]
        if group_id in user_chats:
            try:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=message_text,
                    parse_mode='MarkdownV2'
                )
                await query.edit_message_text(f"Сообщение отправлено в группу {group_id}.")
            except BadRequest as e:
                logger.error(f"BadRequest error while sending to {group_id}: {e}")
                await query.edit_message_text(f"Ошибка при отправке сообщения в группу {group_id}.")
            except Exception as e:
                logger.error(f"Unexpected error while sending to {group_id}: {e}")
                await query.edit_message_text(f"Непредвиденная ошибка при отправке в группу {group_id}.")
        else:
            await query.edit_message_text(f"Группа {group_id} не найдена в списке пользовательских групп.")

def escape_markdownv2(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2.
    """
    reserved_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in reserved_chars else char for char in text)

def main():
    application = Application.builder().token(TOKEN).connection_pool_size(8).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("on", on_command))
    application.add_handler(CommandHandler("off", off_command))
    application.add_handler(CommandHandler("all", all_command))
    application.add_handler(CommandHandler("get_groups_id", get_groups_id))
    # Обработчики управления группами
    application.add_handler(CommandHandler("add_user_group", 
        lambda u,c: handle_group_management(u,c, USERS_FILE, True)))
    application.add_handler(CommandHandler("del_user_group", 
        lambda u,c: handle_group_management(u,c, USERS_FILE, False)))
    application.add_handler(CommandHandler("add_admin_group", 
        lambda u,c: handle_group_management(u,c, ADMINS_FILE, True)))
    application.add_handler(CommandHandler("del_admin_group", 
        lambda u,c: handle_group_management(u,c, ADMINS_FILE, False)))
    # Обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == "__main__":
    main()
