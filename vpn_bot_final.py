import telebot
from telebot import types
import json
import os
from datetime import datetime

# ==================== تنظیمات ====================
BOT_TOKEN = "8883749112:AAGWXJgS-YuVwkHNBEysk0IAXNoLSrhoj7k"
ADMIN_ID = 775127399
CARD_NUMBER = "6219-8619-2246-1164"
CARD_NAME = "مصطفی پور"

# ==================== پلن‌ها ====================
PLANS = {
    "unlimited_1": {"name": "♾️ نامحدود — ۱ ماهه", "price": 600000},
    "unlimited_2": {"name": "♾️ نامحدود — ۲ ماهه", "price": 1150000},
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
    name = message.from_user.first_name or "کاربر"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("📞 پشتیبانی", callback_data="support"))
    bot.send_message(
        message.chat.id,
        f"✨ *سلام {name} عزیز!*\n"
        f"به *Lenshik VPN* خوش اومدی 🔐\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚡️ *سرعت فوق‌العاده بالا*\n"
        f"🌍 *دسترسی به تمام سایت‌ها*\n"
        f"🔒 *امنیت کامل و رمزنگاری*\n"
        f"🕐 *پشتیبانی ۲۴ ساعته*\n"
        f"📱 *پشتیبانی از همه دستگاه‌ها*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"برای شروع یه گزینه انتخاب کن 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== خرید ====================
@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♾️ اشتراک نامحدود", callback_data="cat_unlimited"))
    markup.add(types.InlineKeyboardButton("📦 اشتراک حجمی", callback_data="cat_limited"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))
    bot.edit_message_text(
        "🛒 *خرید اشتراک*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "نوع اشتراک مورد نظرت رو انتخاب کن:\n\n"
        "♾️ *نامحدود* — بدون محدودیت حجم\n"
        "📦 *حجمی* — با حجم مشخص\n"
        "━━━━━━━━━━━━━━━",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== نامحدود ====================
@bot.callback_query_handler(func=lambda call: call.data == "cat_unlimited")
def show_unlimited(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📅 ۱ ماهه — 600,000 تومان", callback_data="plan_unlimited_1"))
    markup.add(types.InlineKeyboardButton("📅 ۲ ماهه — 1,150,000 تومان", callback_data="plan_unlimited_2"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))
    bot.edit_message_text(
        "♾️ *اشتراک نامحدود*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "✅ بدون محدودیت حجم\n"
        "✅ سرعت پایدار\n"
        "✅ مناسب استفاده روزانه\n"
        "━━━━━━━━━━━━━━━\n\n"
        "مدت اشتراک رو انتخاب کن 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== حجمی ====================
@bot.callback_query_handler(func=lambda call: call.data == "cat_limited")
def show_limited(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    limited = [(k, v) for k, v in PLANS.items() if k.startswith("gb_")]
    buttons = [
        types.InlineKeyboardButton(
            f"📦 {v['name'].split()[1]} — {v['price']:,}",
            callback_data=f"plan_{k}"
        ) for k, v in limited
    ]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))
    bot.edit_message_text(
        "📦 *اشتراک حجمی — ۱ ماهه*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💰 هر گیگ: *6,000 تومان*\n"
        "━━━━━━━━━━━━━━━\n\n"
        "حجم مورد نظرت رو انتخاب کن 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== انتخاب پلن ====================
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
    markup.add(types.InlineKeyboardButton("✅ پرداخت کردم، رسید میفرستم", callback_data="send_receipt"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))

    bot.edit_message_text(
        f"💳 *اطلاعات پرداخت*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{plan['name']}*\n"
        f"💰 مبلغ: *{plan['price']:,} تومان*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"💳 *شماره کارت:*\n"
        f"`{CARD_NUMBER}`\n"
        f"👤 به نام: *{CARD_NAME}*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ بعد از واریز، دکمه زیر رو بزن\n"
        f"و تصویر رسید رو ارسال کن 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== رسید ====================
@bot.callback_query_handler(func=lambda call: call.data == "send_receipt")
def ask_receipt(call):
    bot.send_message(
        call.message.chat.id,
        "📸 *ارسال رسید*\n\n"
        "تصویر رسید پرداخت رو اینجا بفرست 👇",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(call.message, receive_receipt)

def receive_receipt(message):
    if not (message.photo or message.document):
        bot.send_message(
            message.chat.id,
            "❌ *خطا!*\n\nلطفاً تصویر رسید رو ارسال کن.",
            parse_mode="Markdown"
        )
        return

    orders = load_orders()
    order = orders.get(str(message.from_user.id), {})

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تایید و ارسال کانفیگ", callback_data=f"confirm_{message.from_user.id}"),
        types.InlineKeyboardButton("❌ رد کردن", callback_data=f"reject_{message.from_user.id}")
    )

    caption = (
        f"💰 *سفارش جدید!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 نام: *{order.get('first_name', '-')}*\n"
        f"🆔 یوزر: @{order.get('username', '-')}\n"
        f"🔢 آیدی: `{message.from_user.id}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{order.get('plan_name', '-')}*\n"
        f"💵 مبلغ: *{order.get('price', 0):,} تومان*\n"
        f"🕐 تاریخ: {order.get('date', '-')}\n"
        f"━━━━━━━━━━━━━━━"
    )

    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)

    orders[str(message.from_user.id)]["status"] = "waiting_confirm"
    save_orders(orders)

    bot.send_message(
        message.chat.id,
        "✅ *رسید دریافت شد!*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "⏳ در حال بررسی پرداخت...\n"
        "🕐 معمولاً زیر *۳۰ دقیقه* کانفیگت ارسال میشه\n"
        "━━━━━━━━━━━━━━━\n\n"
        "ممنون که Lenshik VPN رو انتخاب کردی 🙏",
        parse_mode="Markdown"
    )

# ==================== تایید ادمین ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data.split("_")[1])
    bot.answer_callback_query(call.id, "✅ کانفیگ رو بفرست")
    msg = bot.send_message(
        ADMIN_ID,
        f"📋 *ارسال کانفیگ*\n\n"
        f"کانفیگ کاربر `{user_id}` رو بفرست 👇",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: send_config(m, user_id))

def send_config(message, user_id):
    config = message.text.strip()
    orders = load_orders()
    order = orders.get(str(user_id), {})

    bot.send_message(
        user_id,
        f"🎉 *اشتراک شما فعال شد!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{order.get('plan_name', '-')}*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔐 *کانفیگ VPN شما:*\n\n"
        f"`{config}`\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 *راهنمای نصب:*\n\n"
        f"🍎 iOS → *Streisand*\n"
        f"🤖 Android → *V2RayNG*\n"
        f"💻 ویندوز → *Hiddify*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🙏 ممنون از اعتمادت\n"
        f"مشکل داشتی پیام بده 👉 @lenshikad",
        parse_mode="Markdown"
    )

    orders[str(user_id)]["status"] = "confirmed"
    save_orders(orders)
    bot.send_message(ADMIN_ID, f"✅ کانفیگ برای کاربر {user_id} ارسال شد.")

# ==================== رد ادمین ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data.split("_")[1])
    bot.send_message(
        user_id,
        "❌ *پرداخت تایید نشد*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "رسید ارسالی تایید نشد.\n\n"
        "🔹 رسید واضح‌تر ارسال کن\n"
        "🔹 یا با پشتیبانی تماس بگیر\n\n"
        "📞 پشتیبانی: @lenshikad\n"
        "━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "❌ رد شد")

# ==================== پشتیبانی ====================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    bot.send_message(
        call.message.chat.id,
        "📞 *پشتیبانی Lenshik VPN*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🕐 ساعات پاسخگویی: ۸ صبح تا ۱۲ شب\n"
        "👨‍💻 پشتیبان: @lenshikad\n"
        "━━━━━━━━━━━━━━━\n\n"
        "برای ارتباط روی یوزرنیم بالا کلیک کن 👆",
        parse_mode="Markdown"
    )

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
        bot.send_message(message.chat.id, "📭 هیچ سفارشی ثبت نشده.")
        return
    text = "📋 *لیست سفارشات:*\n\n━━━━━━━━━━━━━━━\n"
    for uid, o in orders.items():
        status_emoji = "✅" if o.get('status') == "confirmed" else "⏳"
        text += f"{status_emoji} *{o.get('first_name','-')}*\n"
        text += f"📦 {o.get('plan_name','-')}\n"
        text += f"🕐 {o.get('date','-')}\n"
        text += f"━━━━━━━━━━━━━━━\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

print("✅ ربات شروع به کار کرد...")
bot.infinity_polling()
