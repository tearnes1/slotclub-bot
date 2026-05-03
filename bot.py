import telebot
import os
import json
import time

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# Твои ID
ADMINS = [7987479496, 7452023277]

# Укажи канал без https://
CHANNEL_USERNAME = "Slot Club | РФ"

PARTNER_LINK = "https://sneket.xyz/ref/834116"

# ---------------- БАЗА ----------------

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": [], "clicks": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ---------------- ПРОВЕРКА ПОДПИСКИ ----------------

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- /START ----------------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # анти-бот простая задержка
    time.sleep(0.5)

    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)

        # уведомление админу
        for admin in ADMINS:
            bot.send_message(admin, f"👤 Новый пользователь: {user_id}")

    markup = telebot.types.InlineKeyboardMarkup()

    if not is_subscribed(user_id):
        subscribe_button = telebot.types.InlineKeyboardButton(
            text="✅ Подписаться на канал",
            url=f"https://t.me/{CHANNEL_USERNAME}"
        )
        check_button = telebot.types.InlineKeyboardButton(
            text="🔄 Проверить подписку",
            callback_data="check_sub"
        )
        markup.add(subscribe_button)
        markup.add(check_button)

        bot.send_message(
            message.chat.id,
            "Чтобы получить доступ, подпишитесь на канал.",
            reply_markup=markup
        )
        return

    access_button = telebot.types.InlineKeyboardButton(
        text="🎰 Получить доступ",
        callback_data="get_access"
    )
    markup.add(access_button)

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в Slot Club | РФ\n\n"
        "Нажмите кнопку ниже, чтобы получить доступ.\n\n"
        "⚠ 18+ Играйте ответственно.",
        reply_markup=markup
    )

# ---------------- ПРОВЕРКА ПОДПИСКИ ----------------

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена")

        markup = telebot.types.InlineKeyboardMarkup()
        access_button = telebot.types.InlineKeyboardButton(
            text="🎰 Получить доступ",
            callback_data="get_access"
        )
        markup.add(access_button)

        bot.send_message(call.message.chat.id,
                         "Теперь можете получить доступ.",
                         reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ Вы не подписаны")

# ---------------- ВЫДАЧА ССЫЛКИ ----------------

@bot.callback_query_handler(func=lambda call: call.data == "get_access")
def send_link(call):
    data["clicks"] += 1
    save_data(data)

    for admin in ADMINS:
        bot.send_message(admin, f"🎯 Нажатие доступа от {call.from_user.id}")

    bot.send_message(
        call.message.chat.id,
        f"✅ Доступ активирован\n\nВот ссылка:\n{PARTNER_LINK}"
    )

# ---------------- СТАТИСТИКА ----------------

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id not in ADMINS:
        return

    total_users = len(data["users"])
    total_clicks = data["clicks"]

    bot.send_message(
        message.chat.id,
        f"📊 Статистика:\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🎯 Нажатий: {total_clicks}"
    )

# ---------------- РАССЫЛКА ----------------

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id not in ADMINS:
        return

    text = message.text.replace("/broadcast ", "")

    sent = 0
    for user_id in data["users"]:
        try:
            bot.send_message(user_id, text)
            sent += 1
        except:
            pass

    bot.send_message(message.chat.id, f"✅ Отправлено: {sent}")

bot.infinity_polling()
