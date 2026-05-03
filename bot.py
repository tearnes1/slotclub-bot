import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text="🎰 Получить доступ",
        url="ТВОЯ_ПАРТНЕРСКАЯ_ССЫЛКА"
    )
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в Slot Club | РФ\n\n"
        "Нажмите кнопку ниже, чтобы получить доступ.\n\n"
        "⚠ 18+ Играйте ответственно.",
        reply_markup=markup
    )

bot.infinity_polling()
