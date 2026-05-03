import telebot
import os
import json
import time

TOKEN = os.environ.get("BOT_TOKEN")

ADMINS = [7987479496, 7452023277]

CHANNEL_USERNAME = "slotclubrf"  # без @
PARTNER_LINK = "https://sneket.xyz/ref/834116"

DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)


# -------- БАЗА --------

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "clicks": 0}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


data = load_data()


# -------- УТИЛИТА ЮЗЕРА --------

def format_user(user):
    username = f"@{user.username}" if user.username else None
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    user_id = user.id

    if username:
        return f"{username} | {full_name} | ID: {user_id}"
    else:
        return f"{full_name} | ID: {user_id}"


# -------- ПРОВЕРКА ПОДПИСКИ --------

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# -------- START --------

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)

    time.sleep(0.3)

    if user_id not in data["users"]:
        data["users"][user_id] = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        save_data(data)

        for admin in ADMINS:
            try:
                bot.send_message(admin,
                                 f"👤 Новый пользователь:\n{format_user(user)}")
            except:
                pass

    markup = telebot.types.InlineKeyboardMarkup()

    if not is_subscribed(user.id):
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


# -------- ПРОВЕРКА --------

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


# -------- ДОСТУП --------

@bot.callback_query_handler(func=lambda call: call.data == "get_access")
def send_link(call):
    user = call.from_user

    data["clicks"] += 1
    save_data(data)

    for admin in ADMINS:
        try:
            bot.send_message(admin,
                             f"🎯 Клик доступа:\n{format_user(user)}")
        except:
            pass

    bot.send_message(
        call.message.chat.id,
        f"✅ Доступ активирован\n\n{PARTNER_LINK}"
    )


# -------- СТАТИСТИКА --------

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


# -------- СПИСОК ЮЗЕРОВ --------

@bot.message_handler(commands=['users'])
def users_list(message):
    if message.from_user.id not in ADMINS:
        return

    text = "👥 Пользователи:\n\n"

    for uid, info in data["users"].items():
        username = f"@{info['username']}" if info["username"] else None
        full_name = f"{info['first_name'] or ''} {info['last_name'] or ''}".strip()

        if username:
            text += f"{username} | {full_name} | ID: {uid}\n"
        else:
            text += f"{full_name} | ID: {uid}\n"

    bot.send_message(message.chat.id, text[:4000])


bot.infinity_polling()
