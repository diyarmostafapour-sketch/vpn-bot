import telebot
from telebot import types
import json
import os
from datetime import datetime

# ==================== تنظیمات ====================
BOT_TOKEN = "8883749112:AAGWXJgS-YuVwkHNBEysk0IAXNoLSrhoj7k"   # از BotFather
ADMIN_ID = 775127399              # Chat ID تو
CARD_NUMBER = "6219-8619-2246-1164"
CARD_NAME = "مصطفی پور"

# ==================== پلن‌ها ====================
PLANS = {
    "unlimited_1": {"name": "🔥 نامحدود — ۱ ماهه", "price": 600000},
    "unlimited_2": {"name": "🔥 نامحدود — ۲ ماهه", "price": 1150000},
    "gb_30":  {"name": "📦 30 گیگ — ۱ ماهه",  "price": 180000},
    "gb_35":  {"name": "📦 35 گیگ — ۱ ماهه",  "price": 210000},
    "gb_40":  {"name": "📦 40 گیگ — ۱ ماهه",  "price": 240000},
    "gb_50":  {"name": "📦 50 گیگ — ۱ ماهه",  "price": 300000},
    "gb_60":  {"name": "📦 60 گیگ — ۱ ماهه",  "price": 360000},
    "gb_70":  {"name": "📦 70 گیگ — ۱ ماهه",  "price": 420000},
    "gb_80":  {"name": "📦 80 گیگ — ۱ ماهه",  "price": 480000},
    "gb_90":  {"name": "📦 90 گیگ — ۱ ماهه",  "price": 540000},
}

ORDERS_FILE = "orders.json"
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== توابع ====================
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_orders(data):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== استارت ====================
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("📞 پشتیبانی", callback_data="support"))
    bot.send_message(
        message.chat.id,
        "🔐 *Lenshik VPN*\n\n"
        "✅ سرعت بالا\n"
        "✅ پایدار ۲۴ ساعته\n"
        "✅ پشتیبانی سریع\n\n"
        "یه گزینه انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== خرید ====================
@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔥 نامحدود", callback_data="cat_unlimited"))
    markup.add(types.InlineKeyboardButton("📦 حجمی", callback_data="cat_limited"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))
    bot.edit_message_text(
        "📋 نوع اشتراک رو انتخاب کن:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "cat_unlimited")
def show_unlimited(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("۱ ماهه — 600,000 تومان", callback_data="plan_unlimited_1"))
    markup.add(types.InlineKeyboardButton("۲ ماهه — 1,150,000 تومان", callback_data="plan_unlimited_2"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))
    bot.edit_message_text(
        "🔥 *پلن نامحدود:*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "cat_limited")
def show_limited(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    limited = [(k, v) for k, v in PLANS.items() if k.startswith("gb_")]
    buttons = [
        types.InlineKeyboardButton(
            f"{v['name'].split()[1]} — {v['price']:,}",
            callback_data=f"plan_{k}"
        ) for k, v in limited
    ]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))
    bot.edit_message_text(
        "📦 *پلن حجمی — ۱ ماهه:*\nهر گیگ 6,000 تومان",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def select_plan(call):
    plan_key = call.data.replace("plan_", "")
    plan = PLANS.get(plan_key)
    if not plan:
        return

    orders = load_orders()
    orders[str(call.from_user.id)] = {
        "plan_key": plan_key,
        "plan_name": plan["name"],
        "price": plan["price"],
        "status": "waiting_receipt",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user_id": call.from_user.id,
        "username": call.from_user.username or "-",
        "first_name": call.from_user.first_name or "-"
    }
    save_orders(orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ رسید فرستادم", callback_data="send_receipt"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))

    bot.edit_message_text(
        f"💳 *اطلاعات پرداخت:*\n\n"
        f"پلن: {plan['name']}\n"
        f"مبلغ: *{plan['price']:,} تومان*\n\n"
        f"💳 شماره کارت:\n`{CARD_NUMBER}`\n"
        f"به نام: {CARD_NAME}\n\n"
        f"⚠️ بعد از واریز دکمه زیر رو بزن و رسید بفرست.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== رسید ====================
@bot.callback_query_handler(func=lambda call: call.data == "send_receipt")
def ask_receipt(call):
    bot.send_message(call.message.chat.id, "📸 تصویر رسید پرداخت رو ارسال کن:")
    bot.register_next_step_handler(call.message, receive_receipt)

def receive_receipt(message):
    if not (message.photo or message.document):
        bot.send_message(message.chat.id, "❌ لطفاً تصویر رسید رو ارسال کن.")
        return

    orders = load_orders()
    order = orders.get(str(message.from_user.id), {})

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تایید", callback_data=f"confirm_{message.from_user.id}"),
        types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{message.from_user.id}")
    )

    caption = (
        f"💰 *پرداخت جدید*\n\n"
        f"👤 {order.get('first_name', '-')} | @{order.get('username', '-')}\n"
        f"🆔 `{message.from_user.id}`\n"
        f"📦 {order.get('plan_name', '-')}\n"
        f"💵 {order.get('price', 0):,} تومان\n"
        f"🕐 {order.get('date', '-')}"
    )

    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)

    orders[str(message.from_user.id)]["status"] = "waiting_confirm"
    save_orders(orders)

    bot.send_message(message.chat.id, "✅ رسید دریافت شد!\n⏳ معمولاً زیر ۳۰ دقیقه کانفیگت ارسال میشه.")

# ==================== تایید ادمین ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data.split("_")[1])
    bot.answer_callback_query(call.id, "کانفیگ رو بفرست")
    msg = bot.send_message(ADMIN_ID, f"📋 کانفیگ کاربر `{user_id}` رو بفرست:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: send_config(m, user_id))

def send_config(message, user_id):
    config = message.text.strip()
    orders = load_orders()
    order = orders.get(str(user_id), {})

    bot.send_message(
        user_id,
        f"✅ *اشتراک فعال شد!*\n\n"
        f"📦 {order.get('plan_name', '-')}\n\n"
        f"🔐 کانفیگ VPN:\n\n"
        f"`{config}`\n\n"
        f"📱 *نصب:*\n"
        f"iOS: Streisand\n"
        f"Android: V2RayNG\n"
        f"ویندوز: Hiddify\n\n"
        f"مشکل داشتی: @lenshikadmin 🙏",
        parse_mode="Markdown"
    )

    orders[str(user_id)]["status"] = "confirmed"
    save_orders(orders)
    bot.send_message(ADMIN_ID, f"✅ کانفیگ برای {user_id} ارسال شد.")

# ==================== رد ادمین ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ رسید تایید نشد.\nرسید واضح‌تر بفرست یا با پشتیبانی تماس بگیر:\n@lenshikadmin")
    bot.answer_callback_query(call.id, "❌ رد شد")

# ==================== پشتیبانی ====================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    bot.send_message(call.message.chat.id, "📞 پشتیبانی:\n@lenshikadmin")

@bot.callback_query_handler(func=lambda call: call.data == "back_start")
def back_start(call):
    start(call.message)

# ==================== دستورات ادمین ====================
@bot.message_handler(commands=["orders"])
def show_orders(message):
    if message.from_user.id != ADMIN_ID:
        return
    orders = load_orders()
    if not orders:
        bot.send_message(message.chat.id, "هیچ سفارشی نیست.")
        return
    text = "📋 *سفارشات:*\n\n"
    for uid, o in orders.items():
        text += f"👤 {o.get('first_name','-')} | {o.get('plan_name','-')} | {o.get('status','-')} | {o.get('date','-')}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ==================== اجرا ====================
print("✅ ربات شروع به کار کرد...")
bot.infinity_polling()
