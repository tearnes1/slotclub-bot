import telebot
import os
import json
import time

# ==== НАСТРОЙКИ ====

TOKEN = os.environ.get("BOT_TOKEN")

ADMINS = [7987479496, 7452023277]  # твои ID

CHANNEL_USERNAME = "slotclubrf"  # без @

PARTNER_LINK = "https://sneket.xyz/ref/834116"

DATA_FILE = "data.json"

# ====================

bot = telebot.TeleBot(TOKEN)


# ---------- БАЗА ----------

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


# ---------- ПРОВЕРКА ПОДПИСКИ ----------

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ---------- START ----------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    time.sleep(0.3)

    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)

        for admin in ADMINS:
            try:
                bot.send_message(admin, f"👤 Новый пользователь: {user_id}")
            except:
                pass

    markup = telebot.types.InlineKeyboardMarkup()

    if not is_subscribed(user_id):
        btn1 = telebot.types.InlineKeyboardButton(
            text="✅ Подписаться",
            url=f"https://t.me/{CHANNEL_USERNAME}"
        )
        btn2 = telebot.types.InlineKeyboardButton(
            text="🔄 Проверить подписку",
            callback_data="check_sub"
        )
        markup.add(btn1)
        markup.add(btn2)

        bot.send_message(
            message.chat.id,
            "Для получения доступа подпишитесь на канал.",
            reply_markup=markup
        )
        return

    btn = telebot.types.InlineKeyboardButton(
        text="🎰 Получить доступ",
        callback_data="get_access"
    )
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в Slot Club | РФ\n\n"
        "Нажмите кнопку ниже для получения доступа.\n\n"
        "⚠ 18+ Играйте ответственно.",
        reply_markup=markup
    )


# ---------- ПРОВЕРКА ----------

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена")

        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(
            text="🎰 Получить доступ",
            callback_data="get_access"
        )
        markup.add(btn)

        bot.send_message(call.message.chat.id,
                         "Теперь можете получить доступ.",
                         reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ Вы не подписаны")


# ---------- ДОСТУП ----------

@bot.callback_query_handler(func=lambda call: call.data == "get_access")
def send_link(call):
    data["clicks"] += 1
    save_data(data)

    for admin in ADMINS:
        try:
            bot.send_message(admin,
                             f"🎯 Клик доступа от {call.from_user.id}")
        except:
            pass

    bot.send_message(
        call.message.chat.id,
        f"✅ Доступ активирован\n\n{PARTNER_LINK}"
    )


# ---------- СТАТИСТИКА ----------

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


# ---------- РАССЫЛКА ----------

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
