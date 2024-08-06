import logging
import os
import sqlite3
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from dotenv import load_dotenv

# Загрузка токена из файла .env
load_dotenv()
secret_token = os.getenv('TELEGRAM_TOKEN')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_random_word_esp():
    """Получить случайное испанское слово для перевода."""
    try:
        conn = sqlite3.connect('words.db')
        c = conn.cursor()
        c.execute('SELECT spanish, russian FROM words ORDER BY RANDOM() LIMIT 1')
        word = c.fetchone()
        logger.info("Испанское слово получено: %s", word)
    except sqlite3.Error as e:
        logger.error(f"Ошибка доступа к базе данных: {e}")
        word = None
    finally:
        conn.close()
    return word

def get_random_word_rus():
    """Получить случайное русское слово для перевода."""
    try:
        conn = sqlite3.connect('words.db')
        c = conn.cursor()
        c.execute('SELECT russian, spanish FROM words ORDER BY RANDOM() LIMIT 1')
        word = c.fetchone()
        logger.info("Русское слово получено: %s", word)
    except sqlite3.Error as e:
        logger.error(f"Ошибка доступа к базе данных: {e}")
        word = None
    finally:
        conn.close()
    return word

def start(update, context):
    """Запуск бота и отправка приветственного сообщения."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['ESP_RUS'],
        ['RUS_ESP'],
        ['Перезапуск']
        ],
        resize_keyboard=True
    )

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name} 🖖\n'
             'Давай поупражняемся в испанском! 🇪🇦 '
             'Я буду писать слово, а ты будешь писать мне в ответ его перевод.\n'
             '\nВыбери режим работы или перезапусти бота, нажав одну из кнопок ниже:\n'
             '💡 переводить испанские слова на русский;\n'
             '💡 переводить русские слова на испанский;\n'
             '🔄 перезапуск бота.',
        reply_markup=button
    )
    context.user_data.clear()  # Очистка всех данных пользователя
    logger.info("Запуск бота для чата %s", chat.id)

def handle_message(update, context):
    """Обработка сообщений пользователя."""
    text = update.message.text
    chat_id = update.effective_chat.id

    if text in ['ESP_RUS', 'RUS_ESP']:
        # Выбор режима работы
        if text == 'ESP_RUS':
            word = get_random_word_esp()
            if word:
                spanish_word, russian_word = word
                context.user_data['selected_word'] = russian_word
                context.user_data['mode'] = 'ESP_RUS'
                context.user_data.setdefault('history', []).append({'spanish': spanish_word, 'russian': russian_word, 'correct': None})
                context.user_data['word_count'] = 0
                context.user_data['session_active'] = True
                context.bot.send_message(chat_id=chat_id, text=spanish_word)
                logger.info("Выбран режим ESP_RUS для чата %s", chat_id)
            else:
                context.bot.send_message(chat_id=chat_id, text="Нет доступных слов.")
                logger.warning("Нет доступных слов для режима ESP_RUS")
        elif text == 'RUS_ESP':
            word = get_random_word_rus()
            if word:
                russian_word, spanish_word = word
                context.user_data['selected_word'] = spanish_word
                context.user_data['mode'] = 'RUS_ESP'
                context.user_data.setdefault('history', []).append({'russian': russian_word, 'spanish': spanish_word, 'correct': None})
                context.user_data['word_count'] = 0
                context.user_data['session_active'] = True
                context.bot.send_message(chat_id=chat_id, text=russian_word)
                logger.info("Выбран режим RUS_ESP для чата %s", chat_id)
            else:
                context.bot.send_message(chat_id=chat_id, text="Нет доступных слов.")
                logger.warning("Нет доступных слов для режима RUS_ESP")
    elif text == 'Перезапуск':
        # Перезапуск бота
        start(update, context)
        logger.info("Бот перезапущен для чата %s", chat_id)
    elif context.user_data.get('session_active', False):
        # Проверка ответа в активной сессии
        user_answer = text.lower()
        correct_answer = context.user_data.get('selected_word', '').lower()
        
        if user_answer == correct_answer:
            bot_response = '✅ *Верно*! Следующее слово:'
            correct = True
        else:
            bot_response = f'❌ *Неверно*. Правильный ответ: {correct_answer}.\n\nПопробуй другое слово:'
            correct = False

        context.bot.send_message(chat_id=chat_id, text=bot_response, parse_mode='Markdown')
        logger.info("Пользователь %s ответил: '%s', правильный ответ: '%s'", chat_id, user_answer, correct_answer)

        # Обновление истории с результатом
        if 'history' in context.user_data and len(context.user_data['history']) > 0:
            context.user_data['history'][-1]['correct'] = correct

        # Увеличение счетчика слов
        context.user_data['word_count'] = context.user_data.get('word_count', 0) + 1

        # Проверка завершения сессии
        if context.user_data['word_count'] >= 10:
            incorrect_words = [entry for entry in context.user_data['history'] if not entry['correct']]
            result_message = 'Сессия завершена! Вот ваши ошибки:\n\n'
            for entry in incorrect_words:
                if context.user_data['mode'] == 'RUS_ESP':
                    result_message += f"{entry['russian']} -> {entry['spanish']}\n"
                else:
                    result_message += f"{entry['spanish']} -> {entry['russian']}\n"
            if not incorrect_words:
                result_message += "Нет ошибок! Отличная работа!"
            context.bot.send_message(chat_id=chat_id, text=result_message)
            logger.info("Сессия завершена для чата %s. Ошибки: %s", chat_id, incorrect_words)
            # Сброс сессии
            context.user_data.clear()
        else:
            # Проверка текущего режима и получение следующего слова
            if context.user_data.get('mode') == 'RUS_ESP':
                word = get_random_word_rus()
                if word:
                    russian_word, spanish_word = word
                    context.user_data['selected_word'] = spanish_word
                    context.user_data.setdefault('history', []).append({'russian': russian_word, 'spanish': spanish_word, 'correct': None})
                    context.bot.send_message(chat_id=chat_id, text=russian_word)
                    logger.info("Следующее русское слово для чата %s: %s", chat_id, russian_word)
                else:
                    context.bot.send_message(chat_id=chat_id, text="Нет доступных слов.")
                    logger.warning("Нет доступных слов для режима RUS_ESP")
            else:
                word = get_random_word_esp()
                if word:
                    spanish_word, russian_word = word
                    context.user_data['selected_word'] = russian_word
                    context.user_data.setdefault('history', []).append({'spanish': spanish_word, 'russian': russian_word, 'correct': None})
                    context.bot.send_message(chat_id=chat_id, text=spanish_word)
                    logger.info("Следующее испанское слово для чата %s: %s", chat_id, spanish_word)
                else:
                    context.bot.send_message(chat_id=chat_id, text="Нет доступных слов.")
                    logger.warning("Нет доступных слов для режима ESP_RUS")
    else:
        # Обработка неизвестных сообщений вне активной сессии
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, выберите режим работы из меню.")
        logger.info("Неизвестное сообщение от пользователя %s вне активной сессии: '%s'. Показаны кнопки.", chat_id, text)

def main():
    """Запуск бота и добавление обработчиков."""
    updater = Updater(token=secret_token)

    # Добавление обработчиков
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
