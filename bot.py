import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ADMIN USERNAME - замени на свой!
ADMIN_USERNAME = "kotovsky_0"

# Состояния для ConversationHandler
NAME, PASSWORD = range(2)
ADMIN_MENU, UPLOAD_WELCOME, UPLOAD_GRAFIK = range(2, 5)

# База данных работников (имя: пароль)
WORKERS = {
    "Иван": "1234",
    "Мария": "5678",
    "Петр": "9012",
    "Анна": "3456"
}

# Графики работы для каждого работника
SCHEDULES = {
    "Иван": [
        "📅 Понедельник: 9:00 - 18:00",
        "📅 Вторник: 9:00 - 18:00",
        "📅 Среда: Выходной",
        "📅 Четверг: 9:00 - 18:00",
        "📅 Пятница: 9:00 - 18:00",
        "📅 Суббота: Выходной",
        "📅 Воскресенье: Выходной"
    ],
    "Мария": [
        "📅 Понедельник: 10:00 - 19:00",
        "📅 Вторник: Выходной",
        "📅 Среда: 10:00 - 19:00",
        "📅 Четверг: 10:00 - 19:00",
        "📅 Пятница: Выходной",
        "📅 Суббота: 10:00 - 19:00",
        "📅 Воскресенье: 10:00 - 19:00"
    ],
    "Петр": [
        "📅 Понедельник: 14:00 - 22:00",
        "📅 Вторник: 14:00 - 22:00",
        "📅 Среда: 14:00 - 22:00",
        "📅 Четверг: Выходной",
        "📅 Пятница: 14:00 - 22:00",
        "📅 Суббота: 14:00 - 22:00",
        "📅 Воскресенье: Выходной"
    ],
    "Анна": [
        "📅 Понедельник: Выходной",
        "📅 Вторник: 12:00 - 20:00",
        "📅 Среда: 12:00 - 20:00",
        "📅 Четверг: 12:00 - 20:00",
        "📅 Пятница: 12:00 - 20:00",
        "📅 Суббота: Выходной",
        "📅 Воскресенье: Выходной"
    ]
}

# Пути к фото
PHOTO_WELCOME = "welcome.PNG"
PHOTO_GRAFIK = "grafik pictur.PNG"

def is_admin(update: Update) -> bool:
    """Проверка является ли пользователь админом"""
    return update.message.from_user.username == ADMIN_USERNAME

# ========== ОБЫЧНЫЕ ФУНКЦИИ БОТА ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало работы с ботом"""
    if os.path.exists(PHOTO_WELCOME):
        try:
            with open(PHOTO_WELCOME, 'rb') as photo:
                sent_message = await update.message.reply_photo(
                    photo=photo,
                    caption="<blockquote>👋 Привет! Я бот для просмотра графика работы.\n\n"
                            "Как тебя зовут?</blockquote>",
                    parse_mode='HTML'
                )
                context.user_data['last_bot_message'] = sent_message.message_id
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            sent_message = await update.message.reply_text(
                "<blockquote>👋 Привет! Я бот для просмотра графика работы.\n\n"
                "Как тебя зовут?</blockquote>",
                parse_mode='HTML'
            )
            context.user_data['last_bot_message'] = sent_message.message_id
    else:
        sent_message = await update.message.reply_text(
            "<blockquote>👋 Привет! Я бот для просмотра графика работы.\n\n"
            "Как тебя зовут?</blockquote>",
            parse_mode='HTML'
        )
        context.user_data['last_bot_message'] = sent_message.message_id
    
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение имени работника"""
    if 'last_bot_message' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['last_bot_message']
            )
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение: {e}")
    
    name = update.message.text.strip()
    context.user_data['name'] = name
    
    sent_message = await update.message.reply_text(
        f"<blockquote>Привет, {name}! 👤\n\n"
        "Теперь введи свой пароль:</blockquote>",
        parse_mode='HTML'
    )
    context.user_data['last_bot_message'] = sent_message.message_id
    
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверка пароля и показ графика"""
    if 'last_bot_message' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['last_bot_message']
            )
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение: {e}")
    
    password = update.message.text.strip()
    name = context.user_data.get('name')
    
    if name in WORKERS and WORKERS[name] == password:
        schedule = SCHEDULES.get(name, [])
        schedule_text = "\n".join(schedule)
        
        if os.path.exists(PHOTO_GRAFIK):
            try:
                with open(PHOTO_GRAFIK, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"<blockquote>✅ Вход выполнен успешно!\n\n"
                                f"📋 Твой график работы, {name}:\n\n"
                                f"{schedule_text}\n\n"
                                f"Чтобы посмотреть график снова, напиши /start</blockquote>",
                        parse_mode='HTML'
                    )
            except Exception as e:
                logger.error(f"Ошибка отправки фото: {e}")
                await update.message.reply_text(
                    f"<blockquote>✅ Вход выполнен успешно!\n\n"
                    f"📋 Твой график работы, {name}:\n\n"
                    f"{schedule_text}\n\n"
                    f"Чтобы посмотреть график снова, напиши /start</blockquote>",
                    parse_mode='HTML'
                )
        else:
            await update.message.reply_text(
                f"<blockquote>✅ Вход выполнен успешно!\n\n"
                f"📋 Твой график работы, {name}:\n\n"
                f"{schedule_text}\n\n"
                f"Чтобы посмотреть график снова, напиши /start</blockquote>",
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text(
            "<blockquote>❌ Неправильное имя или пароль!\n\n"
            "Попробуй ещё раз: /start</blockquote>",
            parse_mode='HTML'
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    await update.message.reply_text(
        "Операция отменена. Напиши /start, чтобы начать снова."
    )
    return ConversationHandler.END

# ========== АДМИН ПАНЕЛЬ ==========

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Админ панель - только для владельца"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа к админ-панели!")
        return ConversationHandler.END
    
    welcome_status = "✅ Есть" if os.path.exists(PHOTO_WELCOME) else "❌ Нет"
    grafik_status = "✅ Есть" if os.path.exists(PHOTO_GRAFIK) else "❌ Нет"
    
    await update.message.reply_text(
        f"<blockquote>🔧 <b>АДМИН ПАНЕЛЬ</b>\n\n"
        f"📊 Текущие файлы:\n"
        f"🖼 Фото приветствия: {welcome_status}\n"
        f"🖼 Фото графика: {grafik_status}\n\n"
        f"📝 Команды:\n"
        f"/upload_welcome - Загрузить фото приветствия\n"
        f"/upload_grafik - Загрузить фото графика\n"
        f"/delete_welcome - Удалить фото приветствия\n"
        f"/delete_grafik - Удалить фото графика\n"
        f"/status - Проверить статус файлов\n"
        f"/admin - Показать это меню</blockquote>",
        parse_mode='HTML'
    )
    return ConversationHandler.END

async def upload_welcome_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало загрузки фото приветствия"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "<blockquote>📤 Отправь мне фото или GIF для экрана приветствия\n\n"
        "Или напиши /cancel чтобы отменить</blockquote>",
        parse_mode='HTML'
    )
    return UPLOAD_WELCOME

async def upload_welcome_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение фото приветствия"""
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            await file.download_to_drive(PHOTO_WELCOME)
            await update.message.reply_text("✅ Фото приветствия загружено!")
        elif update.message.document:
            file = await context.bot.get_file(update.message.document.file_id)
            await file.download_to_drive(PHOTO_WELCOME)
            await update.message.reply_text("✅ Файл приветствия загружен!")
        else:
            await update.message.reply_text("❌ Отправь фото или файл!")
            return UPLOAD_WELCOME
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    
    return ConversationHandler.END

async def upload_grafik_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало загрузки фото графика"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "<blockquote>📤 Отправь мне фото или GIF для экрана графика\n\n"
        "Или напиши /cancel чтобы отменить</blockquote>",
        parse_mode='HTML'
    )
    return UPLOAD_GRAFIK

async def upload_grafik_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение фото графика"""
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            await file.download_to_drive(PHOTO_GRAFIK)
            await update.message.reply_text("✅ Фото графика загружено!")
        elif update.message.document:
            file = await context.bot.get_file(update.message.document.file_id)
            await file.download_to_drive(PHOTO_GRAFIK)
            await update.message.reply_text("✅ Файл графика загружен!")
        else:
            await update.message.reply_text("❌ Отправь фото или файл!")
            return UPLOAD_GRAFIK
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    
    return ConversationHandler.END

async def delete_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление фото приветствия"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа!")
        return
    
    try:
        if os.path.exists(PHOTO_WELCOME):
            os.remove(PHOTO_WELCOME)
            await update.message.reply_text("✅ Фото приветствия удалено!")
        else:
            await update.message.reply_text("❌ Фото приветствия не найдено!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def delete_grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление фото графика"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа!")
        return
    
    try:
        if os.path.exists(PHOTO_GRAFIK):
            os.remove(PHOTO_GRAFIK)
            await update.message.reply_text("✅ Фото графика удалено!")
        else:
            await update.message.reply_text("❌ Фото графика не найдено!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус файлов"""
    if not is_admin(update):
        await update.message.reply_text("❌ У вас нет доступа!")
        return
    
    welcome_status = "✅ Есть" if os.path.exists(PHOTO_WELCOME) else "❌ Нет"
    grafik_status = "✅ Есть" if os.path.exists(PHOTO_GRAFIK) else "❌ Нет"
    
    await update.message.reply_text(
        f"<blockquote>📊 Статус файлов:\n\n"
        f"🖼 Фото приветствия: {welcome_status}\n"
        f"🖼 Фото графика: {grafik_status}</blockquote>",
        parse_mode='HTML'
    )

def main():
    """Запуск бота"""
    TOKEN = '8553170248:AAE_IElMIxIHl9Wn4hTqHsfxOkQ73r1b7IM'
    
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик обычного диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Обработчик загрузки welcome
    upload_welcome_handler = ConversationHandler(
        entry_points=[CommandHandler('upload_welcome', upload_welcome_start)],
        states={
            UPLOAD_WELCOME: [MessageHandler(filters.PHOTO | filters.Document.ALL, upload_welcome_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Обработчик загрузки grafik
    upload_grafik_handler = ConversationHandler(
        entry_points=[CommandHandler('upload_grafik', upload_grafik_start)],
        states={
            UPLOAD_GRAFIK: [MessageHandler(filters.PHOTO | filters.Document.ALL, upload_grafik_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(upload_welcome_handler)
    application.add_handler(upload_grafik_handler)
    application.add_handler(CommandHandler('admin', admin))
    application.add_handler(CommandHandler('delete_welcome', delete_welcome))
    application.add_handler(CommandHandler('delete_grafik', delete_grafik))
    application.add_handler(CommandHandler('status', status))
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()


"""
📌 АДМИН ПАНЕЛЬ ГОТОВА!

ТВОЙ НИК УЖЕ ПРОПИСАН: kotovsky_0

КОМАНДЫ ДЛЯ ТЕБЯ (АДМИНА):
/admin - Открыть админ панель
/upload_welcome - Загрузить фото приветствия
/upload_grafik - Загрузить фото графика
/delete_welcome - Удалить фото приветствия
/delete_grafik - Удалить фото графика
/status - Проверить какие файлы есть

КАК РАБОТАЕТ:
1. Напиши боту /admin
2. Выбери команду (например /upload_welcome)
3. Отправь боту фото или GIF
4. Готово! Файл сохранён и бот будет его использовать

ТОЛЬКО ТЫ (@kotovsky_0) можешь использовать эти команды!
Другие пользователи будут видеть только обычный бот с графиком.
"""