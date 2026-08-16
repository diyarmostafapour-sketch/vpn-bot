import telebot
from telebot import types
import json
import os
import time
import threading
import schedule
import logging
import io
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

trial_lock = threading.Lock()

# ==================== تنظیمات ====================
BOT_TOKEN = "8883749112:AAGrF-iJD4zs9VF2-myRXaug1xubUF44uWg"
ADMIN_ID = 775127399
CARD_NUMBER = "6219-8619-2246-1164"
CARD_NAME = "مصطفی پور"

# ==================== پلن‌ها ====================
PLANS = {
    "unlimited_1": {"name": "♾️ نامحدود — ۱ ماهه", "price": 600000, "days": 30},
    "unlimited_2": {"name": "♾️ نامحدود — ۲ ماهه", "price": 1150000, "days": 60},
    "gb_30":  {"name": "📦 30 گیگ — ۱ ماهه",  "price": 180000, "days": 30},
    "gb_35":  {"name": "📦 35 گیگ — ۱ ماهه",  "price": 210000, "days": 30},
    "gb_40":  {"name": "📦 40 گیگ — ۱ ماهه",  "price": 240000, "days": 30},
    "gb_50":  {"name": "📦 50 گیگ — ۱ ماهه",  "price": 300000, "days": 30},
    "gb_60":  {"name": "📦 60 گیگ — ۱ ماهه",  "price": 360000, "days": 30},
    "gb_70":  {"name": "📦 70 گیگ — ۱ ماهه",  "price": 420000, "days": 30},
    "gb_80":  {"name": "📦 80 گیگ — ۱ ماهه",  "price": 480000, "days": 30},
    "gb_90":  {"name": "📦 90 گیگ — ۱ ماهه",  "price": 540000, "days": 30},
}

# ==================== تنظیمات رفرال / تخفیف ====================
REFERRALS_NEEDED_FOR_DISCOUNT = 3
REFERRAL_DISCOUNT_PERCENT = 15
EXPIRY_REMINDER_DAYS = [3, 1]
PENDING_ORDER_ALERT_HOURS = 2

# ==================== انبار کانفیگ تست رایگان ====================
TRIAL_CONFIGS = [
    "https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/91a65f32-0905-43c0-8fdb-e7a806b08367/#تست-1228",
    "https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/af43d5ae-4199-487e-84a1-7a544162c9b0/#تست1243",
    "https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/879493e1-4520-42a0-84a0-baf7db0097da/#تست-1256",
    "https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/18235ec0-3265-4415-972a-84cdf794b739/#تست-1262",
]
TRIAL_HOURS = 24

# ==================== انبار کانفیگ آماده (ذخیره دائمی در فایل) ====================
INITIAL_CONFIG_STOCK = {
    "unlimited_1": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/b8159021-44a4-40ca-9580-3f4c059ab981/auto/?asn=unknown#4151%7C%20lenshik%20vpn"],
    "unlimited_2": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/377338db-4aad-4384-8599-0c28bc947a96/auto/?asn=unknown#8695%20%7C%20lenshik%20vpn"],
    "gb_30": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/4b9dbd6b-2077-4aba-8784-5f698090f400/auto/?asn=unknown#5784%20%7C%20lenshik%20vpn"],
    "gb_35": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/4e73b8ce-1ab3-40b3-97ad-4955b3fcf2a6/auto/?asn=unknown#6841%20%7C%20lenshik%20vpn"],
    "gb_40": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/e9053691-e3de-436f-a3f8-23923e451d99/auto/?asn=unknown#3574%20%7C%20lenshik%20vpn"],
    "gb_50": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/cbe4f1e2-d660-43bd-bc34-8fb3f959b707/auto/?asn=unknown#8236%20%7C%20lenshik%20vpn"],
    "gb_60": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/85ace95b-57bd-4dad-869e-06663d77fc04/auto/?asn=unknown#3852%20%7C%20lenshik%20vpn"],
    "gb_70": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/f1740d17-7ffd-43d9-98d9-3c980f7bdcac/auto/?asn=unknown#8024%20%7C%20lenshik%20vpn"],
    "gb_80": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/7077ac5c-b709-43b4-9583-dc91c1e50cbd/auto/?asn=unknown#8695%20%7C%20lenshik%20vpn"],
    "gb_90": ["https://axonnetwork0market.patoghyou.ir/uBoJwwxhi28wz9KArkDJ/29959d0f-d198-4f52-946f-233e7c1887f2/auto/?asn=unknown#8084%20%7C%20lenshik%20vpn"],
}

# ==================== وضعیت سرویس ====================
SERVICE_STATUS = {
    "state": "ok",
    "message": "همه سرورها پایدار و در حال کار هستن ✅"
}

ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"
SUPPORT_FILE = "support_sessions.json"
TRIALS_FILE = "trials.json"
USAGE_FILE = "usage.json"
STOCK_FILE = "stock.json"
ACTIVITY_FILE = "activity.json"

bot = telebot.TeleBot(BOT_TOKEN)

admin_pending_action = {"name": None}

def register_admin_prompt(message, action_name, handler):
    previous = admin_pending_action["name"]
    if previous and previous != action_name:
        try:
            bot.send_message(
                ADMIN_ID,
                f"ℹ️ درخواست قبلی (که هنوز جواب ندادی) لغو شد و این یکی جاش فعاله."
            )
        except Exception as e:
            logger.exception(e)

    admin_pending_action["name"] = action_name

    def wrapped(m):
        if admin_pending_action["name"] != action_name:
            return
        admin_pending_action["name"] = None
        handler(m)

    bot.register_next_step_handler(message, wrapped)

# ==================== توابع کمکی فایل ====================
def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_orders():
    return load_json(ORDERS_FILE)

def save_orders(data):
    save_json(ORDERS_FILE, data)

def load_users():
    return load_json(USERS_FILE)

def save_users(data):
    save_json(USERS_FILE, data)

def load_support_sessions():
    return load_json(SUPPORT_FILE)

def save_support_sessions(data):
    save_json(SUPPORT_FILE, data)

def load_trials():
    return load_json(TRIALS_FILE)

def save_trials(data):
    save_json(TRIALS_FILE, data)

def load_usage():
    return load_json(USAGE_FILE)

def save_usage(data):
    save_json(USAGE_FILE, data)

def load_stock():
    if os.path.exists(STOCK_FILE):
        return load_json(STOCK_FILE)
    save_json(STOCK_FILE, INITIAL_CONFIG_STOCK)
    return dict(INITIAL_CONFIG_STOCK)

def save_stock(data):
    save_json(STOCK_FILE, data)

def load_activity():
    return load_json(ACTIVITY_FILE)

def save_activity(data):
    save_json(ACTIVITY_FILE, data)

# اسم فارسی هر بخش برای نمایش قشنگ‌تر توی آمار
SECTION_LABELS = {
    "buy": "خرید",
    "my_subscription": "اشتراک من",
    "get_trial": "تست رایگان",
    "referral_info": "معرفی به دوستان",
    "service_status": "وضعیت سرویس",
    "support": "پشتیبانی",
}

def log_activity(user, section_key):
    """هر بار کاربر وارد یه بخش میشه، این تابع صداش کن تا ثبت بشه"""
    label = SECTION_LABELS.get(section_key, section_key)
    activity = load_activity()
    uid = str(user.id)

    if uid not in activity:
        activity[uid] = {
            "first_name": user.first_name or "-",
            "username": user.username or "-",
            "visit_count": 0,
            "last_seen": "",
            "recent": []
        }

    activity[uid]["first_name"] = user.first_name or "-"
    activity[uid]["username"] = user.username or "-"
    activity[uid]["visit_count"] += 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    activity[uid]["last_seen"] = now_str

    activity[uid]["recent"].insert(0, {"section": label, "time": now_str})
    activity[uid]["recent"] = activity[uid]["recent"][:10]  # فقط ۱۰ تای آخر نگه دار

    save_activity(activity)

def relative_time(time_str):
    """تاریخ ذخیره‌شده رو به «۵ دقیقه

# ==================== کاربران / رفرال ====================
def ensure_user(user):
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "user_id": user.id,
            "username": user.username or "-",
            "first_name": user.first_name or "-",
            "referred_by": None,
            "referral_count": 0,
            "discount_percent": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_users(users)
    else:
        users[uid]["username"] = user.username or "-"
        users[uid]["first_name"] = user.first_name or "-"
        save_users(users)
    return users[uid]

def register_referral(new_user_id, referrer_id):
    users = load_users()
    new_uid = str(new_user_id)
    ref_uid = str(referrer_id)

    if new_uid == ref_uid:
        return

    if ref_uid not in users:
        return

    if users[new_uid].get("referred_by") is not None:
        return

    users[new_uid]["referred_by"] = int(ref_uid)
    users[ref_uid]["referral_count"] = users[ref_uid].get("referral_count", 0) + 1

    if users[ref_uid]["referral_count"] % REFERRALS_NEEDED_FOR_DISCOUNT == 0:
        users[ref_uid]["discount_percent"] = REFERRAL_DISCOUNT_PERCENT
        save_users(users)
        try:
            bot.send_message(
                int(ref_uid),
                f"🎁 *تبریک!*\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"با معرفی {REFERRALS_NEEDED_FOR_DISCOUNT} نفر، یک کد تخفیف "
                f"*{REFERRAL_DISCOUNT_PERCENT}٪* برات فعال شد 🎉\n"
                f"این تخفیف توی خرید بعدیت اعمال میشه.\n"
                f"━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception(e)
    else:
        save_users(users)

def get_user_discount(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("discount_percent", 0)

def clear_user_discount(user_id):
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]["discount_percent"] = 0
        save_users(users)

def apply_discount(price, percent):
    if percent <= 0:
        return price
    return int(price - (price * percent / 100))

# ==================== استارت (+ لینک رفرال) ====================
@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "کاربر"
    ensure_user(message.from_user)

    parts = message.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            referrer_id = int(parts[1].replace("ref_", ""))
            users = load_users()
            uid = str(message.from_user.id)
            if users.get(uid, {}).get("referred_by") is None and referrer_id != message.from_user.id:
                users[uid]["referred_by_pending"] = referrer_id
                save_users(users)
        except ValueError:
            pass

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("🎟️ اشتراک من", callback_data="my_subscription"))
    markup.add(types.InlineKeyboardButton("🧪 دریافت کانفیگ تست رایگان", callback_data="get_trial"))
    markup.add(types.InlineKeyboardButton("🎁 معرفی به دوستان", callback_data="referral_info"))
    markup.add(types.InlineKeyboardButton("📡 وضعیت سرویس", callback_data="service_status"))
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

# ==================== کانفیگ تست رایگان ====================
@bot.callback_query_handler(func=lambda call: call.data == "get_trial")
def get_trial(call):
    bot.answer_callback_query(call.id)
    uid = str(call.from_user.id)

    with trial_lock:
        trials = load_trials()

        if uid in trials:
            bot.send_message(
                call.message.chat.id,
                "⚠️ *قبلاً کانفیگ تست گرفتی*\n\n"
                "━━━━━━━━━━━━━━━\n"
                "هر کاربر فقط یک بار می‌تونه کانفیگ تست رایگان بگیره.\n"
                "برای استفاده کامل، از بخش «🛒 خرید اشتراک» اقدام کن.\n"
                "━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return

        given_count = len(trials)

        if given_count >= len(TRIAL_CONFIGS):
            bot.send_message(
                call.message.chat.id,
                "😔 *فعلاً کانفیگ تست موجود نیست*\n\n"
                "━━━━━━━━━━━━━━━\n"
                "انبار کانفیگ‌های تست تموم شده.\n"
                "می‌تونی مستقیم از بخش «🛒 خرید اشتراک» اقدام کنی.\n"
                "━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
            return

        index = given_count
        config = TRIAL_CONFIGS[index]

        trials[uid] = {
            "user_id": call.from_user.id,
            "first_name": call.from_user.first_name or "-",
            "username": call.from_user.username or "-",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "config_index": index
        }
        save_trials(trials)

    bot.send_message(
        call.message.chat.id,
        f"🧪 *کانفیگ تست رایگان شما*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏳ اعتبار: *{TRIAL_HOURS} ساعت*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"`{config}`\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 *راهنمای نصب:*\n\n"
        f"*پیشنهادی برای تجربه بهتر Hiddify ⭐*\n\n"
        f"🍎 iOS → *Hiddify - V2BOX*\n"
        f"🤖 Android → *Hiddify - V2ray*\n"
        f"💻 Windows → *Hiddify - V2ray*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"اگه راضی بودی، از بخش «🛒 خرید اشتراک» پلن کامل رو تهیه کن 🙏",
        parse_mode="Markdown"
    )

    remaining = len(TRIAL_CONFIGS) - (given_count + 1)

    try:
        bot.send_message(
            ADMIN_ID,
            f"🧪 کانفیگ تست برای کاربر {call.from_user.first_name or '-'} "
            f"(`{call.from_user.id}`) ارسال شد.\n"
            f"📦 کانفیگ باقی‌مانده در انبار: *{remaining}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.exception(e)

    if remaining == 1:
        try:
            bot.send_message(
                ADMIN_ID,
                "⚠️ *هشدار انبار کانفیگ تست*\n\n"
                "━━━━━━━━━━━━━━━\n"
                "فقط *۱ کانفیگ تست* توی انبار باقی مونده!\n"
                "برو توی کد لیست `TRIAL_CONFIGS` رو بروزرسانی کن\n"
                "━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception(e)
    elif remaining == 0:
        try:
            bot.send_message(
                ADMIN_ID,
                "🚨 *انبار کانفیگ تست تموم شد!*\n\n"
                "━━━━━━━━━━━━━━━\n"
                "همه‌ی کانفیگ‌های تست داده شدن.\n"
                "لیست `TRIAL_CONFIGS` رو بروزرسانی کن.\n"
                "━━━━━━━━━━━━━━━",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.exception(e)

# ==================== وضعیت سرویس ====================
@bot.callback_query_handler(func=lambda call: call.data == "service_status")
def service_status(call):
    bot.answer_callback_query(call.id)
    state = SERVICE_STATUS.get("state", "ok")
    emoji = {"ok": "🟢", "warning": "🟡", "down": "🔴"}.get(state, "🟢")
    label = {"ok": "پایدار", "warning": "اختلال جزئی", "down": "قطعی"}.get(state, "پایدار")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))

    bot.send_message(
        call.message.chat.id,
        f"📡 *وضعیت سرویس*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{emoji} وضعیت کلی: *{label}*\n\n"
        f"{SERVICE_STATUS.get('message', '-')}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== اشتراک من ====================
@bot.callback_query_handler(func=lambda call: call.data == "my_subscription")
def my_subscription(call):
    bot.answer_callback_query(call.id)
    orders = load_orders()
    order = orders.get(str(call.from_user.id))

    markup = types.InlineKeyboardMarkup()

    if not order or order.get("status") != "confirmed":
        markup.add(types.InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy"))
        markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))
        bot.send_message(
            call.message.chat.id,
            "🎟️ *اشتراک من*\n\n"
            "━━━━━━━━━━━━━━━\n"
            "هنوز اشتراک فعالی نداری.\n"
            "━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    expiry_str = order.get("expiry_date")
    days_left_text = ""
    if expiry_str:
        try:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            days_left = (expiry - datetime.now().date()).days
            if days_left >= 0:
                days_left_text = f"⏳ روزهای باقیمانده: *{days_left} روز*\n"
            else:
                days_left_text = "⚠️ *اشتراک شما منقضی شده*\n"
        except ValueError:
            pass

    markup.add(types.InlineKeyboardButton("🔄 تمدید همین پلن", callback_data=f"renew_{order.get('plan_key')}"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))

    bot.send_message(
        call.message.chat.id,
        f"🎟️ *اشتراک من*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{order.get('plan_name', '-')}*\n"
        f"📅 تاریخ انقضا: *{expiry_str or '-'}*\n"
        f"{days_left_text}"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== تمدید با یک کلیک ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("renew_"))
def renew_plan(call):
    plan_key = call.data.replace("renew_", "")
    fake_call = call
    fake_call.data = f"plan_{plan_key}"
    select_plan(fake_call)

# ==================== معرفی به دوستان ====================
@bot.callback_query_handler(func=lambda call: call.data == "referral_info")
def referral_info(call):
    bot.answer_callback_query(call.id)
    ensure_user(call.from_user)
    users = load_users()
    u = users.get(str(call.from_user.id), {})
    count = u.get("referral_count", 0)
    discount = u.get("discount_percent", 0)
    remaining = REFERRALS_NEEDED_FOR_DISCOUNT - (count % REFERRALS_NEEDED_FOR_DISCOUNT)
    if remaining == REFERRALS_NEEDED_FOR_DISCOUNT:
        remaining = 0

    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start=ref_{call.from_user.id}"

    discount_line = (
        f"🎉 الان *{discount}٪* تخفیف فعال داری، توی خرید بعدی اعمال میشه!\n\n"
        if discount > 0 else ""
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))

    bot.send_message(
        call.message.chat.id,
        f"🎁 *معرفی به دوستان*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"وقتی *{REFERRALS_NEEDED_FOR_DISCOUNT} نفر* با لینک تو خرید و تایید بشن،\n"
        f"یه کد تخفیف *{REFERRAL_DISCOUNT_PERCENT}٪* برات فعال میشه 🎉\n\n"
        f"👥 تعداد معرفی موفق: *{count}*\n"
        f"⏳ تا تخفیف بعدی: *{remaining if remaining else REFERRALS_NEEDED_FOR_DISCOUNT} نفر* دیگه\n\n"
        f"{discount_line}"
        f"پیام زیر رو برای دوستات بفرست تا با لینک تو وارد بشن 👇\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=markup
    )

    bot.send_message(
        call.message.chat.id,
        f"🔐 Lenshik VPN — سرعت بالا، بدون قطعی\n\n"
        f"من از این سرویس استفاده می‌کنم و راضی‌ام،\n"
        f"بهت پیشنهاد می‌کنم امتحانش کنی 👇\n\n"
        f"✈️ سرعت پایدار و بالا\n"
        f"🌍 دسترسی به همه سایت‌ها\n"
        f"🧪 کانفیگ تست رایگان قبل از خرید\n\n"
        f"👇 از همینجا شروع کن:\n{link}"
    )

# ==================== خرید ====================
@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♾️ اشتراک نامحدود", callback_data="cat_unlimited"))
    markup.add(types.InlineKeyboardButton("📦 اشتراک حجمی", callback_data="cat_limited"))
    markup.add(types.InlineKeyboardButton("🎟️ کد تخفیف دارم", callback_data="enter_discount"))
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

# ==================== وارد کردن دستی کد تخفیف ====================
@bot.callback_query_handler(func=lambda call: call.data == "enter_discount")
def enter_discount(call):
    bot.answer_callback_query(call.id)
    discount = get_user_discount(call.from_user.id)
    if discount > 0:
        text = (
            f"🎟️ *کد تخفیف فعال*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"تو یه تخفیف *{discount}٪* فعال داری که خودکار\n"
            f"توی خرید بعدیت اعمال میشه ✅\n"
            f"━━━━━━━━━━━━━━━"
        )
    else:
        text = (
            f"🎟️ *کد تخفیف*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"در حال حاضر تخفیف فعالی نداری.\n"
            f"با معرفی {REFERRALS_NEEDED_FOR_DISCOUNT} دوست از قسمت\n"
            f"«🎁 معرفی به دوستان» می‌تونی {REFERRAL_DISCOUNT_PERCENT}٪ تخفیف بگیری.\n"
            f"━━━━━━━━━━━━━━━"
        )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# ==================== نامحدود ====================
@bot.callback_query_handler(func=lambda call: call.data == "cat_unlimited")
def show_unlimited(call):
    bot.answer_callback_query(call.id)
    discount = get_user_discount(call.from_user.id)
    p1 = apply_discount(PLANS["unlimited_1"]["price"], discount)
    p2 = apply_discount(PLANS["unlimited_2"]["price"], discount)

    markup = types.InlineKeyboardMarkup()
    label1 = f"📅 ۱ ماهه — {p1:,} تومان" + (" 🎉" if discount else "")
    label2 = f"📅 ۲ ماهه — {p2:,} تومان" + (" 🎉" if discount else "")
    markup.add(types.InlineKeyboardButton(label1, callback_data="plan_unlimited_1"))
    markup.add(types.InlineKeyboardButton(label2, callback_data="plan_unlimited_2"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))

    discount_note = f"\n🎉 تخفیف *{discount}٪* روی این قیمت‌ها اعمال شده!\n" if discount else ""

    bot.edit_message_text(
        "♾️ *اشتراک نامحدود*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "✅ بدون محدودیت حجم\n"
        "✅ سرعت پایدار\n"
        "✅ مناسب استفاده روزانه\n"
        f"━━━━━━━━━━━━━━━\n{discount_note}\n"
        "مدت اشتراک رو انتخاب کن 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== حجمی ====================
@bot.callback_query_handler(func=lambda call: call.data == "cat_limited")
def show_limited(call):
    bot.answer_callback_query(call.id)
    discount = get_user_discount(call.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    limited = [(k, v) for k, v in PLANS.items() if k.startswith("gb_")]
    buttons = []
    for k, v in limited:
        price = apply_discount(v["price"], discount)
        label = f"📦 {v['name'].split()[1]} — {price:,}" + (" 🎉" if discount else "")
        buttons.append(types.InlineKeyboardButton(label, callback_data=f"plan_{k}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))

    discount_note = f"\n🎉 تخفیف *{discount}٪* روی این قیمت‌ها اعمال شده!\n" if discount else ""

    bot.edit_message_text(
        "📦 *اشتراک حجمی — ۱ ماهه*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💰 هر گیگ: *6,000 تومان*\n"
        f"━━━━━━━━━━━━━━━\n{discount_note}\n"
        "حجم مورد نظرت رو انتخاب کن 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== انتخاب پلن ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def select_plan(call):
    bot.answer_callback_query(call.id)
    plan_key = call.data.replace("plan_", "")
    plan = PLANS.get(plan_key)
    if not plan:
        return

    discount = get_user_discount(call.from_user.id)
    final_price = apply_discount(plan["price"], discount)

    orders = load_orders()
    uid = str(call.from_user.id)
    existing = orders.get(uid)

    if existing and existing.get("status") in ("waiting_confirm", "processing", "delivery_failed"):
        bot.send_message(
            call.message.chat.id,
            "⚠️ *یه سفارش در انتظار تایید داری*\n\n"
            "━━━━━━━━━━━━━━━\n"
            "قبلاً رسید فرستادی و در انتظار تایید ادمین هستی.\n"
            "لطفاً صبر کن تا اون سفارش تایید یا رد بشه،\n"
            "بعد سفارش جدید ثبت کن.\n\n"
            "اگه فکر می‌کنی مدت زیادی گذشته، از بخش پشتیبانی پیام بده.\n"
            "━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return

    if existing and existing.get("status") == "delivery_failed":
        bot.send_message(
            call.message.chat.id,
            "⚠️ *سفارش قبلی‌ات هنوز حل نشده*\n\n"
            "━━━━━━━━━━━━━━━\n"
            "پرداخت قبلیت تایید شده ولی ارسال کانفیگ باهاش مشکل داشته.\n"
            "لطفاً از بخش «📞 پشتیبانی» پیام بده تا برات حلش کنیم،\n"
            "قبل از ثبت سفارش جدید.\n"
            "━━━━━━━━━━━━━━━",
            parse_mode="Markdown"
        )
        return

    # 🆕 اگه سفارش قبلی confirmed بود، تاریخ انقضاش رو نگه می‌داریم تا موقع تمدید ازش استفاده کنیم
    previous_expiry = None
    if existing and existing.get("status") == "confirmed":
        previous_expiry = existing.get("expiry_date")

    order_id = f"{call.from_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    orders[uid] = {
        "order_id": order_id,
        "plan_key": plan_key,
        "plan_name": plan["name"],
        "price": final_price,
        "original_price": plan["price"],
        "discount_applied": discount,
        "days": plan["days"],
        "status": "waiting_receipt",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user_id": call.from_user.id,
        "username": call.from_user.username or "-",
        "first_name": call.from_user.first_name or "-",
        "previous_expiry": previous_expiry
    }
    save_orders(orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ پرداخت کردم، رسید میفرستم", callback_data="send_receipt"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="buy"))

    price_line = f"💰 مبلغ: *{final_price:,} تومان*\n"
    if discount:
        price_line = (
            f"💰 مبلغ اصلی: ~{plan['price']:,}~ تومان\n"
            f"🎉 مبلغ با تخفیف {discount}٪: *{final_price:,} تومان*\n"
        )

    bot.edit_message_text(
        f"💳 *اطلاعات پرداخت*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{plan['name']}*\n"
        f"{price_line}"
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
    bot.answer_callback_query(call.id)
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
    uid = str(message.from_user.id)
    order = orders.get(uid, {})

    order_id = order.get("order_id", f"{message.from_user.id}_unknown")
    confirm_cb = f"confirm_{message.from_user.id}_{order_id}"
    reject_cb = f"reject_{message.from_user.id}_{order_id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تایید و ارسال کانفیگ", callback_data=confirm_cb),
        types.InlineKeyboardButton("❌ رد کردن", callback_data=reject_cb)
    )

    discount_line = ""
    if order.get("discount_applied"):
        discount_line = f"🎟️ تخفیف اعمال‌شده: *{order.get('discount_applied')}٪*\n"

    caption = (
        f"💰 *سفارش جدید!*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 نام: *{order.get('first_name', '-')}*\n"
        f"🆔 یوزر: @{order.get('username', '-')}\n"
        f"🔢 آیدی: `{message.from_user.id}`\n"
        f"🧾 شماره سفارش: `{order_id}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📦 پلن: *{order.get('plan_name', '-')}*\n"
        f"{discount_line}"
        f"💵 مبلغ: *{order.get('price', 0):,} تومان*\n"
        f"🕐 تاریخ: {order.get('date', '-')}\n"
        f"━━━━━━━━━━━━━━━"
    )

    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)

    orders[uid]["status"] = "waiting_confirm"
    orders[uid]["receipt_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
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

    parts = call.data.split("_", 2)
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "⚠️ فرمت دکمه اشتباهه")
        return

    user_id = int(parts[1])
    button_order_id = parts[2]

    orders = load_orders()
    order = orders.get(str(user_id))

    if not order or order.get("status") != "waiting_confirm":
        bot.answer_callback_query(call.id, "⚠️ این سفارش قابل تایید نیست (شاید قبلاً پردازش شده)")
        return

    current_order_id = order.get("order_id", "")
    if button_order_id != current_order_id:
        bot.answer_callback_query(
            call.id,
            "⚠️ این دکمه مربوط به سفارش قبلیه! سفارش جدید کاربر رو ببین."
        )
        return

    # 🆕 قفل کردن فوری سفارش تا از کلیک دوباره / پردازش دوگانه جلوگیری بشه
    order["status"] = "processing"
    orders[str(user_id)] = order
    save_orders(orders)

    plan_key = order.get("plan_key")

    stock = load_stock()
    plan_stock = stock.get(plan_key, [])

    if plan_stock:
        config = plan_stock.pop(0)
        stock[plan_key] = plan_stock
        save_stock(stock)
        bot.answer_callback_query(call.id, "✅ از انبار ارسال شد")
        success = finalize_and_send_config(user_id, config)

        plan_name = order.get("plan_name", plan_key)
        remaining_stock = len(plan_stock)

        # 🆕 هشدار اتمام انبار فقط وقتی معنا داره که ارسال واقعاً موفق شده باشه
        if success:
            if remaining_stock == 0:
                try:
                    bot.send_message(
                        ADMIN_ID,
                        f"🚨 *انبار کانفیگ پلن تموم شد!*\n\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📦 پلن: *{plan_name}*\n"
                        f"آخرین کانفیگ همین الان برای مشتری ارسال شد.\n"
                        f"کانفیگ جدید از دوستت بگیر و به `stock.json` اضافه کن.\n"
                        f"━━━━━━━━━━━━━━━",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.exception(e)
            else:
                try:
                    bot.send_message(
                        ADMIN_ID,
                        f"📦 یه کانفیگ از انبار پلن *{plan_name}* فروخته شد.\n"
                        f"باقی‌مانده: *{remaining_stock}*",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.exception(e)

        return

    bot.answer_callback_query(call.id, "✅ کانفیگ رو بفرست")
    msg = bot.send_message(
        ADMIN_ID,
        f"📋 *ارسال کانفیگ*\n\n"
        f"کانفیگ کاربر `{user_id}` رو بفرست 👇\n"
        f"_(انبار این پلن خالیه، دستی وارد کن)_",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "send_config", lambda m: finalize_and_send_config(user_id, m.text.strip()))

def finalize_and_send_config(user_id, config):
    """
    سفارش رو نهایی می‌کنه و کانفیگ رو برای کاربر می‌فرسته.
    اگه ارسال fail بشه، status میشه delivery_failed (نه confirmed) و ادمین
    یه دکمه‌ی «ارسال مجدد» می‌گیره. کانفیگ استفاده‌شده ذخیره میشه تا موقع
    retry دوباره پرسیده نشه.
    برمی‌گردونه: True اگه ارسال موفق بود، False اگه fail شد.
    """
    orders = load_orders()
    uid = str(user_id)
    order = orders.get(uid, {})

    days = order.get("days", 30)
    now = datetime.now()

    # 🆕 منطق تمدید: اگه اشتراک قبلی هنوز تموم نشده، از تاریخ انقضای قبلی شروع کن نه از الان
    start_date = now
    previous_expiry_str = order.get("previous_expiry")
    if previous_expiry_str:
        try:
            previous_expiry = datetime.strptime(previous_expiry_str, "%Y-%m-%d")
            if previous_expiry > now:
                start_date = previous_expiry
        except ValueError:
            pass

    expiry_date = start_date + timedelta(days=days)

    order["confirm_date"] = now.strftime("%Y-%m-%d %H:%M")
    order["expiry_date"] = expiry_date.strftime("%Y-%m-%d")
    order["last_config"] = config  # 🆕 برای retry نگه می‌داریم
    orders[uid] = order
    save_orders(orders)

    # 🆕 اول تلاش می‌کنیم ارسال کنیم، بعد بر اساس نتیجه وضعیت رو ثبت می‌کنیم
    try:
        bot.send_message(
            user_id,
            f"🎉 *اشتراک شما فعال شد!*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📦 پلن: *{order.get('plan_name', '-')}*\n"
            f"📅 تاریخ انقضا: *{order.get('expiry_date', '-')}*\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔐 *کانفیگ VPN شما:*\n\n"
            f"`{config}`\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📱 *راهنمای نصب:*\n\n"
            f"*پیشنهادی برای تجربه بهتر Hiddify ⭐*\n\n"
            f"🍎 iOS → *Hiddify - V2BOX*\n"
            f"🤖 Android → *Hiddify - V2ray*\n"
            f"💻 Windows → *Hiddify - V2ray*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🙏 ممنون از اعتمادت\n"
            f"مشکل داشتی پیام بده 👉 @lenshikad",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.exception(e)

        # 🆕 ارسال fail شد → delivery_failed، نه confirmed
        orders = load_orders()
        orders[uid]["status"] = "delivery_failed"
        save_orders(orders)

        retry_markup = types.InlineKeyboardMarkup()
        retry_markup.add(types.InlineKeyboardButton("🔁 ارسال مجدد کانفیگ", callback_data=f"retry_{user_id}"))
        try:
            bot.send_message(
                ADMIN_ID,
                f"❌ *ارسال کانفیگ ناموفق بود!*\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"👤 کاربر: `{user_id}`\n"
                f"📦 پلن: *{order.get('plan_name', '-')}*\n"
                f"⚠️ خطا: `{e}`\n"
                f"احتمالاً کاربر بات رو بلاک کرده.\n"
                f"کانفیگ ذخیره شده — با دکمه زیر دوباره امتحان کن.\n"
                f"━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=retry_markup
            )
        except Exception as e2:
            logger.exception(e2)
        return False

    # 🆕 اینجا فقط وقتی می‌رسیم که ارسال واقعاً موفق بوده
    orders = load_orders()
    order = orders.get(uid, {})
    order["status"] = "confirmed"
    order["reminders_sent"] = []
    order["last_config"] = config
    orders[uid] = order
    save_orders(orders)

    users = load_users()
    pending_ref = users.get(uid, {}).get("referred_by_pending")
    if pending_ref:
        register_referral(user_id, pending_ref)
        users = load_users()
        if uid in users:
            users[uid].pop("referred_by_pending", None)
            save_users(users)

    if order.get("discount_applied"):
        clear_user_discount(user_id)

    if order.get("plan_key", "").startswith("gb_"):
        usage = load_usage()
        usage[uid] = {
            "plan_key": order.get("plan_key"),
            "plan_name": order.get("plan_name"),
            "total_gb": None,
            "used_gb": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_usage(usage)

    try:
        bot.send_message(ADMIN_ID, f"✅ کانفیگ برای کاربر {user_id} ارسال شد. (انقضا: {order.get('expiry_date')})")
    except Exception as e:
        logger.exception(e)

    return True

# 🆕 ==================== ارسال مجدد کانفیگ (retry) ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("retry_"))
def retry_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(call.data.replace("retry_", ""))
    except ValueError:
        bot.answer_callback_query(call.id, "⚠️ آیدی نامعتبره")
        return

    orders = load_orders()
    order = orders.get(str(user_id))

    if not order or order.get("status") != "delivery_failed":
        bot.answer_callback_query(call.id, "⚠️ این سفارش نیازی به ارسال مجدد نداره")
        return

    config = order.get("last_config")
    if not config:
        bot.answer_callback_query(call.id, "❌ کانفیگی برای این سفارش ذخیره نشده، دستی بفرست")
        return

    bot.answer_callback_query(call.id, "🔁 در حال تلاش مجدد...")
    success = finalize_and_send_config(user_id, config)
    if success:
        try:
            bot.send_message(ADMIN_ID, f"✅ این‌بار ارسال برای کاربر {user_id} موفق بود.")
        except Exception as e:
            logger.exception(e)

# ==================== رد ادمین ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    if call.from_user.id != ADMIN_ID:
        return

    parts = call.data.split("_", 2)
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "⚠️ فرمت دکمه اشتباهه")
        return

    user_id = int(parts[1])
    button_order_id = parts[2]

    orders = load_orders()
    order = orders.get(str(user_id))

    if not order or order.get("status") != "waiting_confirm":
        bot.answer_callback_query(call.id, "⚠️ این سفارش قبلاً پردازش شده")
        return

    current_order_id = order.get("order_id", "")
    if button_order_id != current_order_id:
        bot.answer_callback_query(
            call.id,
            "⚠️ این دکمه مربوط به سفارش قبلیه!"
        )
        return

    order["status"] = "rejected"
    order["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    orders[str(user_id)] = order
    save_orders(orders)

    try:
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
    except Exception as e:
        logger.exception(e)

    bot.answer_callback_query(call.id, "❌ رد شد")

# ==================== پشتیبانی ====================
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 ارسال پیام به پشتیبانی", callback_data="start_support_chat"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت", callback_data="back_start"))
    bot.send_message(
        call.message.chat.id,
        "📞 *پشتیبانی Lenshik VPN*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "🕐 ساعات پاسخگویی: ۸ صبح تا ۱۲ شب\n"
        "👨‍💻 پشتیبان: @lenshikad\n"
        "━━━━━━━━━━━━━━━\n\n"
        "می‌تونی از همینجا هم مستقیم برای پشتیبانی پیام بفرستی 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_support_chat")
def start_support_chat(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "💬 *پیامت رو بنویس*\n\n"
        "هر چی بفرستی مستقیم برای پشتیبانی ارسال میشه\n"
        "و بهت جواب میدن 👇",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(call.message, relay_support_message)

def relay_support_message(message):
    user = message.from_user
    sessions = load_support_sessions()
    sessions[str(user.id)] = {
        "user_id": user.id,
        "username": user.username or "-",
        "first_name": user.first_name or "-"
    }
    save_support_sessions(sessions)

    header = (
        f"📩 *پیام پشتیبانی جدید*\n\n"
        f"👤 نام: *{user.first_name or '-'}*\n"
        f"🆔 یوزر: @{user.username or '-'}\n"
        f"🔢 آیدی: `{user.id}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"برای پاسخ، روی پیام کاربر *ریپلای* کن.\n"
        f"━━━━━━━━━━━━━━━"
    )
    try:
        bot.send_message(ADMIN_ID, header, parse_mode="Markdown")
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except Exception as e:
        logger.exception(e)

    bot.send_message(
        message.chat.id,
        "✅ پیامت برای پشتیبانی ارسال شد.\n"
        "به‌زودی جواب می‌گیری 🙏"
    )

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.reply_to_message is not None)
def admin_reply_to_support(message):
    forwarded = message.reply_to_message

    target_user_id = None

    if forwarded.forward_from:
        target_user_id = forwarded.forward_from.id
    else:
        text = forwarded.text or forwarded.caption or ""
        import re
        match = re.search(r"آیدی:\s*`?(\d+)`?", text)
        if match:
            target_user_id = int(match.group(1))

    if not target_user_id:
        return

    try:
        bot.copy_message(target_user_id, message.chat.id, message.message_id)
        bot.send_message(target_user_id, "👆 پاسخ پشتیبانی")
        bot.send_message(ADMIN_ID, "✅ پیام برای کاربر ارسال شد.")
    except Exception as e:
        logger.exception(e)
        bot.send_message(ADMIN_ID, f"❌ خطا در ارسال پیام: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "back_start")
def back_start(call):
    bot.answer_callback_query(call.id)
    start(call.message)

# ==================== پنل ادمین ====================
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    show_admin_panel(message.chat.id)

def show_admin_panel(chat_id, message_id=None):
    orders = load_orders()
    pending_count = sum(1 for o in orders.values() if o.get("status") == "waiting_confirm")
    failed_count = sum(1 for o in orders.values() if o.get("status") == "delivery_failed")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        f"⏳ سفارشات در انتظار تایید ({pending_count})", callback_data="admin_pending"
    ))
    if failed_count:
        markup.add(types.InlineKeyboardButton(
            f"❌ ارسال‌های ناموفق ({failed_count})", callback_data="admin_failed"
        ))
    markup.add(types.InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_report"))
    markup.add(types.InlineKeyboardButton("📋 لیست کامل سفارشات", callback_data="admin_orders"))
    markup.add(types.InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton("📨 ارسال پیام به کاربر خاص", callback_data="admin_send_user"))
    markup.add(types.InlineKeyboardButton("📡 تغییر وضعیت سرویس", callback_data="admin_status"))
    markup.add(types.InlineKeyboardButton("🎟️ ثبت کد تخفیف دستی", callback_data="admin_manual_discount"))
    markup.add(types.InlineKeyboardButton("🧪 آمار کانفیگ‌های تست", callback_data="admin_trials"))
    markup.add(types.InlineKeyboardButton("📦 اضافه کردن کانفیگ به انبار", callback_data="admin_add_stock"))
    markup.add(types.InlineKeyboardButton("🧪 اضافه کردن کانفیگ تست", callback_data="admin_add_trial"))
    markup.add(types.InlineKeyboardButton("👥 آمار کاربران", callback_data="admin_users_stats"))
    markup.add(types.InlineKeyboardButton("💾 خروجی بکاپ", callback_data="admin_backup"))
    markup.add(types.InlineKeyboardButton("📥 ورودی بکاپ", callback_data="admin_restore"))
    

    text = (
        "🛠️ *پنل مدیریت Lenshik VPN*\n\n"
        "━━━━━━━━━━━━━━━\n"
        "از دکمه‌های زیر برای مدیریت ربات استفاده کن 👇\n"
        "━━━━━━━━━━━━━━━"
    )

    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
            return
        except Exception as e:
            logger.exception(e)
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel_back")
def admin_panel_back(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    show_admin_panel(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_orders")
def admin_orders_cb(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    show_orders(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "admin_pending")
def admin_pending(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    orders = load_orders()
    pending = {uid: o for uid, o in orders.items() if o.get("status") == "waiting_confirm"}

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))

    if not pending:
        bot.send_message(call.message.chat.id, "✅ سفارش در انتظار تاییدی وجود نداره.", reply_markup=markup)
        return

    text = "⏳ *سفارشات در انتظار تایید:*\n\n━━━━━━━━━━━━━━━\n"
    for uid, o in pending.items():
        text += f"👤 *{o.get('first_name','-')}* (`{uid}`)\n"
        text += f"📦 {o.get('plan_name','-')} — {o.get('price',0):,} تومان\n"
        text += f"🕐 رسید: {o.get('receipt_time', o.get('date','-'))}\n"
        text += "━━━━━━━━━━━━━━━\n"
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# 🆕 لیست سفارش‌هایی که ارسال کانفیگشون fail شده، هرکدوم با دکمه‌ی retry
@bot.callback_query_handler(func=lambda call: call.data == "admin_failed")
def admin_failed(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    orders = load_orders()
    failed = {uid: o for uid, o in orders.items() if o.get("status") == "delivery_failed"}

    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))

    if not failed:
        bot.send_message(call.message.chat.id, "✅ هیچ ارسال ناموفقی وجود نداره.", reply_markup=back_markup)
        return

    bot.send_message(call.message.chat.id, "❌ *سفارشات با ارسال ناموفق:*", parse_mode="Markdown")
    for uid, o in failed.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 ارسال مجدد", callback_data=f"retry_{uid}"))
        bot.send_message(
            call.message.chat.id,
            f"👤 *{o.get('first_name','-')}* (`{uid}`)\n"
            f"📦 {o.get('plan_name','-')}\n",
            parse_mode="Markdown",
            reply_markup=markup
        )
    bot.send_message(call.message.chat.id, "━━━━━━━━━━━━━━━", reply_markup=back_markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_report")
def admin_report(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return

    orders = load_orders()
    confirmed = [o for o in orders.values() if o.get("status") == "confirmed"]

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    month_str = now.strftime("%Y-%m")

    total_all = sum(o.get("price", 0) for o in confirmed)
    total_today = sum(o.get("price", 0) for o in confirmed if o.get("confirm_date", "").startswith(today_str))
    total_month = sum(o.get("price", 0) for o in confirmed if o.get("confirm_date", "").startswith(month_str))

    plan_counts = {}
    for o in confirmed:
        name = o.get("plan_name", "-")
        plan_counts[name] = plan_counts.get(name, 0) + 1

    top_plans = sorted(plan_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_plans_text = "\n".join([f"• {name}: {count} فروش" for name, count in top_plans]) or "—"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))

    bot.send_message(
        call.message.chat.id,
        f"📊 *گزارش مالی*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 درآمد امروز: *{total_today:,} تومان*\n"
        f"💰 درآمد این ماه: *{total_month:,} تومان*\n"
        f"💰 درآمد کل: *{total_all:,} تومان*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🧾 تعداد کل فروش‌ها: *{len(confirmed)}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏆 *پرفروش‌ترین پلن‌ها:*\n{top_plans_text}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_status")
def admin_status(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 پایدار", callback_data="setstatus_ok"))
    markup.add(types.InlineKeyboardButton("🟡 اختلال جزئی", callback_data="setstatus_warning"))
    markup.add(types.InlineKeyboardButton("🔴 قطعی", callback_data="setstatus_down"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))
    bot.send_message(
        call.message.chat.id,
        f"📡 *وضعیت فعلی:* {SERVICE_STATUS.get('state')}\n\n"
        f"وضعیت جدید رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("setstatus_"))
def set_status(call):
    if call.from_user.id != ADMIN_ID:
        return
    new_state = call.data.replace("setstatus_", "")
    SERVICE_STATUS["state"] = new_state
    bot.answer_callback_query(call.id, "✅ وضعیت بروزرسانی شد")
    msg = bot.send_message(
        call.message.chat.id,
        "متن توضیح وضعیت رو بنویس (برای نمایش به کاربرها):"
    )
    register_admin_prompt(msg, "status_message", save_status_message)

def save_status_message(message):
    if message.from_user.id != ADMIN_ID:
        return
    SERVICE_STATUS["message"] = message.text.strip()
    bot.send_message(ADMIN_ID, "✅ وضعیت سرویس ذخیره شد.")

@bot.callback_query_handler(func=lambda call: call.data == "admin_manual_discount")
def admin_manual_discount(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(
        call.message.chat.id,
        "🎟️ *ثبت تخفیف دستی*\n\n"
        "آیدی عددی کاربر و درصد تخفیف رو اینطوری بفرست:\n"
        "`123456789 15`",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "manual_discount", apply_manual_discount)

def apply_manual_discount(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.strip().split()
        target_id, percent = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        bot.send_message(ADMIN_ID, "❌ فرمت اشتباهه. مثال درست: 123456789 15")
        return

    users = load_users()
    uid = str(target_id)
    if uid not in users:
        bot.send_message(ADMIN_ID, "❌ همچین کاربری توی دیتابیس نیست.")
        return

    users[uid]["discount_percent"] = percent
    save_users(users)
    bot.send_message(ADMIN_ID, f"✅ تخفیف {percent}٪ برای کاربر {target_id} ثبت شد.")
    try:
        bot.send_message(
            target_id,
            f"🎁 یک کد تخفیف *{percent}٪* برات فعال شد! توی خرید بعدی اعمال میشه 🎉",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.exception(e)

@bot.callback_query_handler(func=lambda call: call.data == "admin_send_user")
def admin_send_user(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(
        call.message.chat.id,
        "📨 *ارسال پیام به کاربر خاص*\n\n"
        "یوزرنیم یا آیدی عددی کاربر رو بفرست:\n"
        "_(مثال: @username یا 123456789)_",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "send_user_id", get_user_id_for_message)

def get_user_id_for_message(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.strip().lstrip("@")

    users = load_users()
    target_id = None
    for uid, u in users.items():
        if u.get("username", "").lstrip("@").lower() == text.lower():
            target_id = int(uid)
            break

    if not target_id:
        try:
            target_id = int(text)
        except ValueError:
            bot.send_message(ADMIN_ID, "❌ کاربری با این یوزرنیم پیدا نشد.")
            return

    msg = bot.send_message(
        ADMIN_ID,
        f"✅ کاربر پیدا شد: `{target_id}`\n\nحالا پیامت رو بفرست 👇\n"
        f"_(متن، عکس، یا فایل)_",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "send_user_msg", lambda m: send_message_to_user(m, target_id))

def send_message_to_user(message, target_id):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.copy_message(target_id, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ پیام به کاربر `{target_id}` ارسال شد.", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطا: `{e}`", parse_mode="Markdown")

# ==================== اضافه کردن کانفیگ به انبار ====================
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_stock")
def admin_add_stock(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    for key, plan in PLANS.items():
        markup.add(types.InlineKeyboardButton(plan["name"], callback_data=f"addstock_{key}"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))
    
    bot.send_message(
        call.message.chat.id,
        "📦 *اضافه کردن کانفیگ به انبار*\n\n"
        "پلن مورد نظر رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("addstock_"))
def addstock_select_plan(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    
    plan_key = call.data.replace("addstock_", "")
    stock = load_stock()
    current_count = len(stock.get(plan_key, []))
    
    msg = bot.send_message(
        call.message.chat.id,
        f"📦 *پلن:* {PLANS[plan_key]['name']}\n"
        f"📊 موجودی فعلی: *{current_count}*\n\n"
        f"کانفیگ جدید رو بفرست 👇\n"
        f"_(هر خط یه کانفیگ — میتونی چند تا یکجا بفرستی)_",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, f"addstock_{plan_key}", lambda m: addstock_save(m, plan_key))

def addstock_save(message, plan_key):
    if message.from_user.id != ADMIN_ID:
        return
    
    new_configs = [line.strip() for line in message.text.strip().splitlines() if line.strip()]
    
    if not new_configs:
        bot.send_message(ADMIN_ID, "❌ چیزی وارد نشد.")
        return
    
    stock = load_stock()
    if plan_key not in stock:
        stock[plan_key] = []
    
    stock[plan_key].extend(new_configs)
    save_stock(stock)
    
    bot.send_message(
        ADMIN_ID,
        f"✅ *{len(new_configs)} کانفیگ* به انبار پلن *{PLANS[plan_key]['name']}* اضافه شد.\n"
        f"📊 موجودی جدید: *{len(stock[plan_key])}*",
        parse_mode="Markdown"
    )
    # ==================== اضافه کردن کانفیگ تست ====================
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_trial")
def admin_add_trial(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return

    trials = load_trials()
    given = len(trials)
    remaining = max(0, len(TRIAL_CONFIGS) - given)

    msg = bot.send_message(
        call.message.chat.id,
        f"🧪 *اضافه کردن کانفیگ تست*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 موجودی فعلی: *{remaining}*\n\n"
        f"کانفیگ‌های جدید رو بفرست 👇\n"
        f"_(هر خط یه کانفیگ)_",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "add_trial", save_trial_configs)

def save_trial_configs(message):
    if message.from_user.id != ADMIN_ID:
        return

    new_configs = [line.strip() for line in message.text.strip().splitlines() if line.strip()]

    if not new_configs:
        bot.send_message(ADMIN_ID, "❌ چیزی وارد نشد.")
        return

    TRIAL_CONFIGS.extend(new_configs)

    trials = load_trials()
    given = len(trials)
    remaining = max(0, len(TRIAL_CONFIGS) - given)

    bot.send_message(
        ADMIN_ID,
        f"✅ *{len(new_configs)} کانفیگ تست* اضافه شد.\n"
        f"📊 موجودی جدید: *{remaining}*",
        parse_mode="Markdown"
    )
@bot.callback_query_handler(func=lambda call: call.data == "admin_trials")
def admin_trials(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    trials = load_trials()
    given = len(trials)
    remaining = max(0, len(TRIAL_CONFIGS) - given)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))
    bot.send_message(
        call.message.chat.id,
        f"🧪 *آمار کانفیگ تست*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 تعداد کل تست‌های داده‌شده: *{given}*\n"
        f"📦 ظرفیت کل انبار: *{len(TRIAL_CONFIGS)}*\n"
        f"✅ باقی‌مانده در انبار: *{remaining}*\n"
        f"━━━━━━━━━━━━━━━" +
        ("\n⚠️ انبار تمومه، لیست TRIAL_CONFIGS رو بروزرسانی کن." if remaining == 0 else ""),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_users_stats")
def admin_users_stats(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    users = load_users()
    orders = load_orders()
    today = datetime.now().date()

    active = 0
    for o in orders.values():
        if o.get("status") != "confirmed":
            continue
        expiry_str = o.get("expiry_date")
        if not expiry_str:
            continue
        try:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if expiry >= today:
                active += 1
        except ValueError:
            pass

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 برگشت به پنل", callback_data="admin_panel_back"))
    users_text = ""
    for uid, u in users.items():
        users_text += f"👤 *{u.get('first_name', '-')}* | @{u.get('username', '-')} | `{uid}`\n"

    bot.send_message(
        call.message.chat.id,
        f"👥 *آمار کاربران*\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 کل کاربران ثبت‌شده: *{len(users)}*\n"
        f"✅ اشتراک‌های فعال (منقضی‌نشده): *{active}*\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{users_text}",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def admin_broadcast(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "📢 *پیام همگانی*\n\n"
        "پیامی که می‌خوای برای همه کاربرها ارسال بشه رو بفرست\n"
        "(می‌تونه متن، عکس، یا فایل باشه) 👇",
        parse_mode="Markdown"
    )
    register_admin_prompt(msg, "broadcast", do_broadcast)

def do_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    total = len(users)
    sent = 0
    failed = 0

    status_msg = bot.send_message(ADMIN_ID, f"⏳ در حال ارسال به {total} کاربر...")

    for uid in users.keys():
        try:
            bot.copy_message(int(uid), message.chat.id, message.message_id)
            sent += 1
            time.sleep(0.05)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Too Many Requests" in err_str:
                time.sleep(2)
                try:
                    bot.copy_message(int(uid), message.chat.id, message.message_id)
                    sent += 1
                except Exception as e2:
                    logger.exception(e2)
                    failed += 1
            else:
                logger.exception(e)
                failed += 1

    try:
        bot.edit_message_text(
            f"✅ *ارسال همگانی تمام شد*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👥 کل کاربران: {total}\n"
            f"✅ ارسال موفق: {sent}\n"
            f"❌ ارسال ناموفق: {failed}\n"
            f"━━━━━━━━━━━━━━━",
            ADMIN_ID,
            status_msg.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.exception(e)

# ==================== بکاپ ====================
@bot.callback_query_handler(func=lambda call: call.data == "admin_backup")
def admin_backup(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    try:
        orders  = load_orders()
        users   = load_users()
        stock   = load_stock()
        trials  = load_trials()
        backup  = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "users": users,
            "orders": orders,
            "stock": stock,
            "trials": trials,
        }
        data = json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        buf = io.BytesIO(data)
        buf.name = filename
        bot.send_document(ADMIN_ID, buf,
            caption=f"💾 *بکاپ کامل*\n📅 {backup['date']}\n\n"
                    f"👥 کاربران: *{len(users)}*\n"
                    f"📦 سفارشات: *{len(orders)}*\n\n"
                    f"برای restore این فایل رو از پنل بفرست.",
            parse_mode="Markdown")
    except Exception as e:
        logger.exception(e)
        bot.send_message(ADMIN_ID, f"❌ خطا در ساخت بکاپ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_restore")
def admin_restore(call):
    bot.answer_callback_query(call.id)
    if call.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(ADMIN_ID,
        "📥 *ورودی بکاپ*\n\n"
        "فایل JSON بکاپ رو اینجا بفرست.\n"
        "⚠️ اطلاعات فعلی با بکاپ جایگزین میشه.",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, receive_restore_file)

def receive_restore_file(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.document:
        bot.send_message(ADMIN_ID, "❌ لطفاً فایل JSON رو بفرست.")
        return
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        backup = json.loads(downloaded.decode("utf-8"))

        if "users" in backup:
            save_users(backup["users"])
        if "orders" in backup:
            save_orders(backup["orders"])
        if "stock" in backup:
            save_stock(backup["stock"])
        if "trials" in backup:
            save_trials(backup["trials"])

        bot.send_message(ADMIN_ID,
            f"✅ *بکاپ بازگردانی شد!*\n\n"
            f"📅 تاریخ بکاپ: {backup.get('date', '-')}\n"
            f"👥 کاربران: *{len(backup.get('users', {}))}*\n"
            f"📦 سفارشات: *{len(backup.get('orders', {}))}*",
            parse_mode="Markdown")
    except Exception as e:
        logger.exception(e)
        bot.send_message(ADMIN_ID, f"❌ خطا در بازگردانی: {e}")

def show_orders(message):
    if message.chat.id != ADMIN_ID:
        return
    orders = load_orders()
    if not orders:
        bot.send_message(message.chat.id, "📭 هیچ سفارشی ثبت نشده.")
        return
    text = "📋 *لیست سفارشات:*\n\n━━━━━━━━━━━━━━━\n"
    for uid, o in orders.items():
        status_emoji = {"confirmed": "✅", "delivery_failed": "❌"}.get(o.get('status'), "⏳")
        text += f"{status_emoji} *{o.get('first_name','-')}*\n"
        text += f"📦 {o.get('plan_name','-')}\n"
        if o.get('expiry_date'):
            text += f"📅 انقضا: {o.get('expiry_date')}\n"
        text += f"🕐 {o.get('date','-')}\n"
        text += f"━━━━━━━━━━━━━━━\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=["orders"])
def show_orders_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    show_orders(message)

# ==================== یادآوری انقضا ====================
def check_expiring_subscriptions():
    orders = load_orders()
    today = datetime.now().date()
    changed = False

    for uid, order in orders.items():
        if order.get("status") != "confirmed":
            continue
        expiry_str = order.get("expiry_date")
        if not expiry_str:
            continue

        try:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        days_left = (expiry - today).days
        reminders_sent = order.get("reminders_sent", [])

        if days_left in EXPIRY_REMINDER_DAYS and days_left not in reminders_sent:
            try:
                bot.send_message(
                    int(uid),
                    f"⏰ *یادآوری انقضای اشتراک*\n\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📦 پلن: *{order.get('plan_name', '-')}*\n"
                    f"📅 تاریخ انقضا: *{expiry_str}*\n"
                    f"⌛️ {days_left} روز دیگه اشتراکت تموم میشه!\n"
                    f"━━━━━━━━━━━━━━━\n\n"
                    f"برای تمدید /start رو بزن 🛒",
                    parse_mode="Markdown"
                )
                reminders_sent.append(days_left)
                order["reminders_sent"] = reminders_sent
                changed = True
            except Exception as e:
                logger.exception(e)

    if changed:
        save_orders(orders)

# ==================== هشدار سفارشات معلق ====================
def check_pending_orders():
    orders = load_orders()
    now = datetime.now()
    changed = False

    for uid, order in orders.items():
        if order.get("status") != "waiting_confirm":
            continue
        receipt_time_str = order.get("receipt_time")
        if not receipt_time_str:
            continue

        try:
            receipt_time = datetime.strptime(receipt_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        hours_passed = (now - receipt_time).total_seconds() / 3600

        if hours_passed >= PENDING_ORDER_ALERT_HOURS and not order.get("pending_alert_sent"):
            try:
                bot.send_message(
                    ADMIN_ID,
                    f"⚠️ *هشدار: سفارش معلق مونده!*\n\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👤 {order.get('first_name','-')} (`{uid}`)\n"
                    f"📦 {order.get('plan_name','-')}\n"
                    f"🕐 رسید ارسال‌شده: {receipt_time_str}\n"
                    f"⌛️ بیش از {PENDING_ORDER_ALERT_HOURS} ساعته منتظر تاییده!\n"
                    f"━━━━━━━━━━━━━━━",
                    parse_mode="Markdown"
                )
                order["pending_alert_sent"] = True
                changed = True
            except Exception as e:
                logger.exception(e)

    if changed:
        save_orders(orders)

def run_scheduler():
    schedule.every().day.at("10:00").do(check_expiring_subscriptions)
    schedule.every(30).minutes.do(check_pending_orders)
    while True:
        schedule.run_pending()
        time.sleep(30)

# ==================== اجرا ====================
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

print("✅ ربات شروع به کار کرد...")
bot.infinity_polling()
