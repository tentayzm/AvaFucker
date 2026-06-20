import asyncio
import os
import re
import json
import io
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from flask import Flask
import edge_tts

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ===== پوشه ذخیره تنظیمات گروه‌ها =====
CONFIG_DIR = "configs"
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# ===== تنظیمات پیش‌فرض برای هر گروه =====
DEFAULT_CONFIG = {
    "target": "مسعود",
    "output_mode": "text",
    "users_stats": {},
    "daily_limits": {
        "max_insults_per_day": 20,
        "max_insults_per_request": 50,
        "max_sudos": 10,
        "max_insults_stored": 200
    }
}

# ===== لیست سودوها =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== فحش‌های متنی =====
TEXT_INSULTS = [
    "مادرجنده",
    "بی‌ناموس",
    "کسمادر",
    "کونی",
    "پدرسگ",
    "حرومزاده",
    "خارکونی",
    "بی‌شرف",
    "بی‌غیرت",
    "کثافت",
    "هرزه",
    "لاابالی",
    "ولنگار",
    "بی‌بندوبار",
    "بی‌سروپا",
    "بی‌ریشه",
    "بی‌اصل",
    "بی‌نسب",
    "بی‌تبار",
    "بی‌خانواده",
    "بی‌پدر",
    "بی‌مادر",
    "یتیم",
    "طردشده",
    "رانده‌شده",
    "لعنتی",
    "ملعون",
    "گناهکار",
    "مجرم",
    "خبیث",
    "پلید",
    "ناپاک",
    "چرکین",
    "کثیف",
    "متعفن",
    "گندیده",
    "مرده",
    "زامبی",
    "اهریمن",
    "شیطان",
    "کیر و کس",
    "دالگت",
    "زیرمه",
    "گاوصفت",
    "ننه‌جنده",
    "خایه‌مال",
    "جنده",
    "کون",
    "کس",
]

# ===== فحش‌های صوتی (با حرکت درست) =====
VOICE_INSULTS = [
    "مادرجنده",
    "بی‌ناموس",
    "کُسمادَر",
    "کونی",
    "پدرسگ",
    "حرومزاده",
    "خارکونی",
    "بی‌شرف",
    "بی‌غیرت",
    "کثافت",
    "هرزه",
    "لاابالی",
    "ولنگار",
    "بی‌بندوبار",
    "بی‌سروپا",
    "بی‌ریشه",
    "بی‌اصل",
    "بی‌نسب",
    "بی‌تبار",
    "بی‌خانواده",
    "بی‌پدر",
    "بی‌مادر",
    "یتیم",
    "طردشده",
    "رانده‌شده",
    "لعنتی",
    "ملعون",
    "گناهکار",
    "مجرم",
    "خبیث",
    "پلید",
    "ناپاک",
    "چرکین",
    "کثیف",
    "متعفن",
    "گندیده",
    "مرده",
    "زامبی",
    "اهریمن",
    "شیطان",
    "کیر و کس",
    "دالگت",
    "زیرمه",
    "گاوصفت",
    "ننه‌جنده",
    "خایه‌مال",
    "جنده",
    "کون",
    "کس",
]

# ===== تابع چسباندن با فرمت خاص =====
def join_insults_custom(target, insult_list):
    """
    چسباندن فحش‌ها با فرمت خاص:
    - فحش اول: {فحش}ی
    - فحش دوم به بعد: {فحش}ِ
    مثال: مسعود + مادرجنده + بیناموس + کسمادر + کونی
    → مسعود مادرجنده‌ی بیناموسِ کسمادرِ کونی
    """
    if not insult_list:
        return target
    
    result = target + " "
    for i, insult in enumerate(insult_list):
        if i == 0:
            result += insult + "‌ی "
        elif i == len(insult_list) - 1:
            result += insult
        else:
            result += insult + "ِ "
    
    return result.strip()

# ===== بارگذاری تنظیمات گروه =====
def load_group_config(chat_id):
    file_path = os.path.join(CONFIG_DIR, f"group_{chat_id}.json")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        config = DEFAULT_CONFIG.copy()
        save_group_config(chat_id, config)
        return config

def save_group_config(chat_id, config):
    file_path = os.path.join(CONFIG_DIR, f"group_{chat_id}.json")
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

# ===== حالت‌های انتظار =====
waiting_states = {}

def convert_persian_to_english(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    return text

async def send_voice_insult(reply_to_message, insult_text):
    try:
        voice = "fa-IR-FaridNeural"
        communicate = edge_tts.Communicate(text=insult_text, voice=voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        await reply_to_message.reply_voice(
            voice=BufferedInputFile(audio_data, filename="insult.mp3")
        )
    except Exception as e:
        await reply_to_message.reply(f"❌ خطا در ساخت ویس: {e}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def panel_keyboard(config):
    mode_text = "🔊 ویس" if config.get("output_mode") == "voice" else "📝 متن"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 تغییر تارگت", callback_data="change_target"),
            InlineKeyboardButton(text="➕ اضافه کردن سودو", callback_data="add_sudo")
        ],
        [
            InlineKeyboardButton(text="➕ اضافه کردن فحش", callback_data="add_insult"),
            InlineKeyboardButton(text=f"🎙️ حالت خروجی: {mode_text}", callback_data="output_mode")
        ],
        [
            InlineKeyboardButton(text="📖 راهنما", callback_data="help"),
            InlineKeyboardButton(text="👨‍💻 سازنده", url="https://t.me/TaakaaOrg")
        ]
    ])
    return keyboard

@dp.message(Command("panel"))
async def panel_command(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in AUTHORIZED_USERS:
        await message.reply("⛔ شما دسترسی به این پنل ندارید!")
        return
    config = load_group_config(chat_id)
    await message.reply(
        f"🔧 **تنظیمات ربات فاکر - گروه {chat_id}**\n\n"
        f"👤 تارگت فعلی: {config['target']}\n"
        f"🎙️ حالت خروجی: {'ویس' if config.get('output_mode') == 'voice' else 'متن'}\n"
        f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}\n"
        f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
        f"یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=panel_keyboard(config)
    )

@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    if user_id not in AUTHORIZED_USERS:
        await callback.answer("⛔ شما دسترسی ندارید!", show_alert=True)
        return
    config = load_group_config(chat_id)
    
    if callback.data == "change_target":
        await callback.message.edit_text(
            "🎯 **تغییر تارگت**\nلطفاً نام شخص جدید را وارد کنید.\n"
            f"تارگت فعلی: {config['target']}"
        )
        waiting_states[f"{chat_id}_waiting_for_target"] = True
        await callback.answer()
    elif callback.data == "add_sudo":
        await callback.message.edit_text(
            "➕ **اضافه کردن سودو جدید**\nلطفاً آیدی عددی سودو جدید را وارد کنید."
        )
        waiting_states[f"{chat_id}_waiting_for_sudo"] = True
        await callback.answer()
    elif callback.data == "add_insult":
        await callback.message.edit_text(
            "➕ **اضافه کردن فحش جدید**\nلطفاً فحش جدید را وارد کنید."
        )
        waiting_states[f"{chat_id}_waiting_for_insult"] = True
        await callback.answer()
    elif callback.data == "output_mode":
        config["output_mode"] = "voice" if config.get("output_mode") == "text" else "text"
        save_group_config(chat_id, config)
        await callback.message.edit_text(
            f"✅ حالت خروجی به **{'ویس' if config.get('output_mode') == 'voice' else 'متن'}** تغییر کرد!",
            reply_markup=panel_keyboard(config)
        )
        await callback.answer()
    elif callback.data == "help":
        await callback.message.edit_text(
            "📖 **راهنما**\n\n"
            f"دستور فحش دادن: `{config['target']} رو بگا {{عدد}}`\n"
            "مثال: `مسعود رو بگا 5`\n\n"
            "1️⃣ روی پیام ریپلای بزنید\n"
            "2️⃣ دستور را بنویسید\n"
            "3️⃣ ربات فحش می‌دهد"
        )
        await callback.answer()

@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""
    config = load_group_config(chat_id)

    # تغییر تارگت
    if waiting_states.get(f"{chat_id}_waiting_for_target") and user_id in AUTHORIZED_USERS:
        if text:
            old_target = config['target']
            config['target'] = text
            save_group_config(chat_id, config)
            waiting_states[f"{chat_id}_waiting_for_target"] = False
            await message.reply(f"✅ تارگت از `{old_target}` به `{text}` تغییر کرد!")
        else:
            await message.reply("❌ لطفاً یک نام معتبر وارد کنید.")
        return

    # اضافه کردن فحش
    if waiting_states.get(f"{chat_id}_waiting_for_insult") and user_id in AUTHORIZED_USERS:
        if text:
            TEXT_INSULTS.append(text)
            VOICE_INSULTS.append(text)
            waiting_states[f"{chat_id}_waiting_for_insult"] = False
            await message.reply(f"✅ فحش `{text}` اضافه شد! ({len(TEXT_INSULTS)} عدد)")
        else:
            await message.reply("❌ لطفاً یک فحش وارد کنید.")
        return

    # اضافه کردن سودو
    if waiting_states.get(f"{chat_id}_waiting_for_sudo") and user_id in AUTHORIZED_USERS:
        if text.isdigit():
            new_sudo = int(text)
            if new_sudo not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.append(new_sudo)
                await message.reply(f"✅ سودو با آیدی `{new_sudo}` اضافه شد!")
            else:
                await message.reply("❌ این کاربر قبلاً سودو است!")
        else:
            await message.reply("❌ لطفاً یک آیدی عددی وارد کنید.")
        waiting_states[f"{chat_id}_waiting_for_sudo"] = False
        return

    # دستور فحش دادن
    if user_id not in AUTHORIZED_USERS:
        return
    if not message.reply_to_message:
        return

    pattern = rf'^{config["target"]} رو بگا\s+(\d+)$'
    match = re.match(pattern, text)
    if not match:
        return

    number_text = match.group(1)
    number_text_english = convert_persian_to_english(number_text)
    if not number_text_english.isdigit():
        return
    number = int(number_text_english)
    if not (1 <= number <= 100):
        return

    CHUNK_SIZE = 4
    insult_list = VOICE_INSULTS if config.get("output_mode") == "voice" else TEXT_INSULTS
    
    for i in range(number):
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(insult_list)
            chunk.append(insult_list[index])
        
        insult_text = join_insults_custom(config['target'], chunk)
        
        if config.get("output_mode") == "voice":
            await send_voice_insult(message.reply_to_message, insult_text)
        else:
            await message.reply_to_message.reply(insult_text)
        await asyncio.sleep(2)

# ===== Flask =====
app = Flask(__name__)
@app.route('/')
@app.route('/health')
def health():
    return "ربات فعال است!", 200

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import threading
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    print("🤖 ربات در حال اجراست...")
    asyncio.run(main())
