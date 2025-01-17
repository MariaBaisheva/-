import telebot
from telebot import types
import requests

bot = telebot.TeleBot("BOT_API")
API_KEY = "API_KEY"
is_bot_running = True
selected_language = None

# Функция для перевода текста с использованием API
def translate_text(text, lang_from, lang_to):
    url = "URL"
    headers = {"Authorization": "Api-Key " + API_KEY}
    data = {
        "folder_id": "FOLDER_ID",
        "texts": [text],
        "sourceLanguageCode": lang_from,
        "targetLanguageCode": lang_to
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
    else:
        print("Ошибка при запросе на перевод текста:", response.text)
        return None

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    global is_bot_running
    is_bot_running = True
    send_language_keyboard(message.chat.id)

# Функция для выбора языка
def send_language_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Якутский'), types.KeyboardButton('Русский'), types.KeyboardButton('Английский'))
    bot.send_message(chat_id, "Выберите язык для перевода:", reply_markup=markup)

# Команда /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global is_bot_running
    is_bot_running = False
    bot.send_message(message.chat.id, "Бот остановлен!")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global selected_language
    global is_bot_running
    if not is_bot_running:
        bot.send_message(message.chat.id, "Бот остановлен!")
        return
    text = message.text.strip().lower()
    if not selected_language:
        # Установка выбранного языка
        if text == "якутский":
            selected_language = "sah"
        elif text == "русский":
            selected_language = "ru"
        elif text == "английский":
            selected_language = "en"
        else:
            send_language_keyboard(message.chat.id)
            return
        bot.send_message(message.chat.id, "Введите текст/слово:")
    else:
        original_text = message.text
        translations = {}

        # Перевод текста на другие языки, кроме выбранного
        if selected_language != "en":
            translations["English"] = translate_text(original_text, selected_language, "en")
        if selected_language != "ru":
            translations["Russian"] = translate_text(original_text, selected_language, "ru")
        if selected_language != "sah":
            translations["Yakut"] = translate_text(original_text, selected_language, "sah")
        response = "Переводы:\n"
        for lang, translation in translations.items():
            if translation:
                response += f"{lang}: {translation}\n"

        bot.send_message(message.chat.id, response)
        selected_language = None
        send_language_keyboard(message.chat.id)

# Запуск
bot.polling()