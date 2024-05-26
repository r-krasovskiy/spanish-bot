import logging
import os

import random
# import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

from exceptions import TelegramError
from words import WORDS

from dotenv import load_dotenv

load_dotenv()
secret_token = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def words_esp_rus(update, context):
    """Select a new word for translation."""
    selected_word = random.choice(list(WORDS))

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=selected_word)
    # Saves a word provided to the user
    # for further checking of its correctness.
    context.user_data['selected_word'] = selected_word


def check_answer(update, context):
    """Check user's answer and provide feedback."""
    uses_answer = update.message.text
    uses_answer = str.lower(uses_answer)

    correct_answer = WORDS[context.user_data['selected_word']]
    if uses_answer == correct_answer:
        bot_response = '✅ *Верно*! Следующее слово:'
    else:
        bot_response = ('❌ *Неверно*. Правильный ответ: {}.'
                        '\n'
                        '\nПопробуй другое слово:'.format(correct_answer))
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=bot_response,
                             parse_mode='Markdown')
    words_esp_rus(update, context)


def wake_up(update, context):
    """Launch Telegram bot."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/ESP_RUS'],
        ['/RUS_ESP'],
        ],
        resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {} 🖖'
             '\n'
             'Давай поупражняемся в испанском! 🇪🇦 '
             'Я буду писать слово, а ты будешь писать мне в ответ его перевод.'
             '\n'
             '\nВыбери режим работы, нажав одну из кнопок ниже:'
             '\n 💡 переводить испанские слова на русский;'
             '\n 💡 переводить русские слова на испанский.'.format(name),
        reply_markup=button
    )


def main():
    """Contain handlers and other basic data."""
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('ESP_RUS',
                                                  words_esp_rus,
                                                  pass_args=True
                                                  ))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, check_answer))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
