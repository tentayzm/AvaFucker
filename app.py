import asyncio
import os
import re
import json
import io
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from flask import Flask
from gtts import gTTS

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ===== لیست سودوها (آیدی عددی) =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== تنظیمات پیش‌فرض =====
CONFIG = {
    "target": "مسعود",
    "output_mode": "text",  # "text" یا "voice"
}

# ===== فحش‌های متنی (بدون حرکات، برای پیام) =====
TEXT_INSULTS = [
    "بی شرف کون طاقار",
    "مادرجنده کثافت",
    "خارکونی پدرسگ",
    "پدرسگ مادرکونی",
    "حرومزاده کسکش",
    "بی‌غیرت مادرجنده",
    "بی‌شرف پدرکونی",
    "کثننت مادرکونی",
    "کسننه پدرسگ",
    "مادرکونی بی‌شرف",
    "کیر و کس دالگت مادرجنده",
    "مادرت زیرمه پدرسگ",
    "مادرتو از کس دار زدم کونی",
    "گاوصفت مادرجنده",
    "ننه‌جنده پدرکونی",
    "کیرتو تو کونت پدرسگ",
    "مادرت تو سگ‌خونه کسکش",
    "پدرت خایه‌مال مادرجنده",
    "خواهرت جنده‌ست کونی",
    "کونی حرومزاده پدرسگ",
    "اهل کون و کس مادرجنده",
    "مادرتو گاییدن بی‌شرف",
    "ننه‌تو کون پدرکونی",
    "پدرتو کون مادرجنده",
    "کس کش پدرسگ",
    "کونی پدرسگ مادرجنده",
    "مادرجنده‌زاده کسکش",
    "کونی بی‌حیا مادرکونی",
    "مادرتو کیر پدرسگ",
    "خواهرتو کیر جنده",
    "کس ننت مادرجنده",
    "کیر ننت پدرکونی",
    "تو کون مادرت پدرسگ",
    "برو گوه بخور مادرجنده",
    "کونشو گاییدن بی‌شرف",
    "مادرتو گاو کسکش",
    "پدرتو سگ کونی",
    "بی‌مغز کونی مادرجنده",
    "کس و کیر تو کونت پدرسگ",
    "بی‌عقل مادرکونی",
    "بی‌شعور پدرکونی",
    "بی‌حیا مادرجنده",
    "بی‌مروت کسکش",
    "بی‌عزت پدرسگ",
    "بی‌آبرو مادرجنده",
    "بی‌هویّت کونی",
    "بی‌اصالت پدرکونی",
    "کثافت مادرجنده",
    "خائن پدرسگ",
    "پست مادرکونی",
    "حقیر بی‌شرف",
    "ابله کسکش",
    "نادان پدرکونی",
    "الاغ مادرجنده",
    "خر پدرسگ",
    "گاو کسکش",
    "سگ مادرجنده",
    "خوک پدرکونی",
    "مار بی‌شرف",
    "عقرب کونی",
    "کرم مادرجنده",
    "انگل پدرسگ",
    "زالو کسکش",
    "رذل مادرکونی",
    "ننگ پدرکونی",
    "عار بی‌شرف",
    "فاحشه مادرجنده",
    "روسیپی کونی",
    "بدکاره پدرسگ",
    "هرزه مادرجنده",
    "بی‌عفّت کسکش",
    "لاابالی پدرکونی",
    "ولنگار مادرجنده",
    "بی‌بندوبار پدرسگ",
    "بی‌سروپا کونی",
    "بی‌ریشه مادرجنده",
    "بی‌اصل پدرکونی",
    "بی‌نسب کسکش",
    "بی‌تبار مادرجنده",
    "بی‌خانواده پدرسگ",
    "بی‌پدر مادرکونی",
    "بی‌مادر پدرکونی",
    "یتیم کونی",
    "طردشده مادرجنده",
    "رانده‌شده پدرسگ",
    "لعنتی کسکش",
    "ملعون مادرجنده",
    "گناهکار پدرکونی",
    "مجرم بی‌شرف",
    "خبیث مادرجنده",
    "پلید کونی",
    "ناپاک پدرسگ",
    "چرکین مادرکونی",
    "کثیف کسکش",
    "متعفن پدرکونی",
    "گندیده مادرجنده",
    "مرده پدرسگ",
    "زامبی کونی",
    "اهریمن مادرجنده",
    "شیطان پدرکونی",
]

# ===== فحش‌های صوتی (بدون حرکات، برای ویس) =====
VOICE_INSULTS = [
    "بی شرف کون طاقار",
    "مادرجنده کثافت",
    "خارکونی پدرسگ",
    "پدرسگ مادرکونی",
    "حرومزاده کسکش",
    "بی غیرت مادرجنده",
    "بی شرف پدرکونی",
    "کثننت مادرکونی",
    "کسننه پدرسگ",
    "مادرکونی بی شرف",
    "کیر و کس دالگت مادرجنده",
    "مادرت زیرمه پدرسگ",
    "مادرتو از کس دار زدم کونی",
    "گاوصفت مادرجنده",
    "ننه جنده پدرکونی",
    "کیرتو تو کونت پدرسگ",
    "مادرت تو سگ خونه کسکش",
    "پدرت خایه مال مادرجنده",
    "خواهرت جنده ست کونی",
    "کونی حرومزاده پدرسگ",
    "اهل کون و کس مادرجنده",
    "مادرتو گاییدن بی شرف",
    "ننه تو کون پدرکونی",
    "پدرتو کون مادرجنده",
    "کس کش پدرسگ",
    "کونی پدرسگ مادرجنده",
    "مادرجنده زاده کسکش",
    "کونی بی حیا مادرکونی",
    "مادرتو کیر پدرسگ",
    "خواهرتو کیر جنده",
    "کس ننت مادرجنده",
    "کیر ننت پدرکونی",
    "تو کون مادرت پدرسگ",
    "برو گوه بخور مادرجنده",
    "کونشو گاییدن بی شرف",
    "مادرتو گاو کسکش",
    "پدرتو سگ کونی",
    "بی مغز کونی مادرجنده",
    "کس و کیر تو کونت پدرسگ",
    "بی عقل مادرکونی",
    "بی شعور پدرکونی",
    "بی حیا مادرجنده",
    "بی مروت کسکش",
    "بی عزت پدرسگ",
    "بی آبرو مادرجنده",
    "بی هویت کونی",
    "بی اصالت پدرکونی",
    "کثافت مادرجنده",
    "خائن پدرسگ",
    "پست مادرکونی",
    "حقیر بی شرف",
    "ابله کسکش",
    "نادان پدرکونی",
    "الاغ مادرجنده",
    "خر پدرسگ",
    "گاو کسکش",
    "سگ مادرجنده",
    "خوک پدرکونی",
    "مار بی شرف",
    "عقرب کونی",
    "کرم مادرجنده",
    "انگل پدرسگ",
    "زالو کسکش",
    "رذل مادرکونی",
    "ننگ پدرکونی",
    "عار بی شرف",
    "فاحشه مادرجنده",
    "روسیپی کونی",
    "بدکاره پدرسگ",
    "هرزه مادرجنده",
    "بی عفت کسکش",
    "لاابالی پدرکونی",
    "ولنگار مادرجنده",
    "بی بندوبار پدرسگ",
    "بی سروپا کونی",
    "بی ریشه مادرجنده",
    "بی اصل پدرکونی",
    "بی نسب کسکش",
    "بی تبار مادرجنده",
    "بی خانواده پدرسگ",
    "بی پدر مادرکونی",
    "بی مادر پدرکونی",
    "یتیم کونی",
    "طرد شده مادرجنده",
    "رانه شده پدرسگ",
    "لعنتي کسکش",
    "ملعون مادرجنده",
    "گناهکار پدرکونی",
    "مجرم بی شرف",
    "خبیث مادرجنده",
    "پلید کونی",
    "ناپاک پدرسگ",
    "چرکین مادرکونی",
    "کثیف کسکش",
    "متعفن پدرکونی",
    "گندیده مادرجنده",
    "مرده پدرسگ",
    "زامبی کونی",
    "اهریمن مادرجنده",
    "شیطان پدرکونی",
]

# ===== تابع حذف حرکات (اِعراب) از متن =====
def remove_diacritics(text):
    diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    return re.sub(diacritics, '', text)

# ===== ذخیره و بارگذاری تنظیمات =====
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

# ===== دیکشنری برای ذخیره حالت‌های انتظار =====
waiting_states = {
    "waiting_for_target": False,
    "waiting_for_sudo": False,
    "waiting_for_insult": False
}

def convert_persian_to_english(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    return text

# ===== تبدیل متن به ویس =====
async def send_voice_insult(reply_to_message, insult_text):
    try:
        # حذف حرکات از متن
        clean_text = remove_diacritics(insult_text)
        
        tts = gTTS(text=clean_text, lang="ar", slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        await reply_to_message.reply_voice(
            voice=BufferedInputFile(
                audio_bytes.read(), 
                filename="insult.ogg"
            )
        )
    except Exception as e:
        await reply_to_message.reply(f"❌ خطا در ساخت ویس: {e}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== کیبورد شیشه‌ای پنل =====
def panel_keyboard():
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

# ===== دستور /panel =====
@dp.message(Command("panel"))
async def panel_command(message: Message):
    user_id = message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await message.reply("⛔ شما دسترسی به این پنل ندارید!")
        return
    await message.reply(
        f"🔧 **تنظیمات ربات فاکر**\n\n"
        f"👤 تارگت فعلی: {config['target']}\n"
        f"🎙️ حالت خروجی: {'ویس' if config.get('output_mode') == 'voice' else 'متن'}\n"
        f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}\n"
        f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
        f"یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=panel_keyboard()
    )

# ===== پردازش دکمه‌ها =====
@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await callback.answer("⛔ شما دسترسی ندارید!", show_alert=True)
        return

    if callback.data == "change_target":
        await callback.message.edit_text(
            "🎯 **تغییر تارگت**\n"
            "لطفاً نام شخص جدید را وارد کنید.\n"
            "مثال: `هینا`\n\n"
            f"تارگت فعلی: {config['target']}"
        )
        waiting_states["waiting_for_target"] = True
        await callback.answer()

    elif callback.data == "add_sudo":
        await callback.message.edit_text(
            "➕ **اضافه کردن سودو جدید**\n"
            "لطفاً آیدی عددی سودو جدید را وارد کنید.\n"
            "مثال: `123456789`\n\n"
            "برای پیدا کردن آیدی عددی، به @userinfobot بروید."
        )
        waiting_states["waiting_for_sudo"] = True
        await callback.answer()

    elif callback.data == "add_insult":
        await callback.message.edit_text(
            "➕ **اضافه کردن فحش جدید**\n"
            "لطفاً فحش جدید را وارد کنید:\n"
            "مثال: `مادرکونی`\n\n"
            f"تعداد فحش‌ها: {len(TEXT_INSULTS)}"
        )
        waiting_states["waiting_for_insult"] = True
        await callback.answer()

    elif callback.data == "output_mode":
        # تغییر حالت خروجی
        if config.get("output_mode") == "text":
            config["output_mode"] = "voice"
        else:
            config["output_mode"] = "text"
        save_config(config)
        
        # به‌روزرسانی پیام پنل
        await callback.message.edit_text(
            f"🔧 **تنظیمات ربات فاکر**\n\n"
            f"👤 تارگت فعلی: {config['target']}\n"
            f"🎙️ حالت خروجی: {'ویس' if config.get('output_mode') == 'voice' else 'متن'}\n"
            f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}\n"
            f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
            f"✅ حالت خروجی به **{'ویس' if config.get('output_mode') == 'voice' else 'متن'}** تغییر کرد!",
            reply_markup=panel_keyboard()
        )
        await callback.answer(f"حالت به {'ویس' if config.get('output_mode') == 'voice' else 'متن'} تغییر کرد!")

    elif callback.data == "help":
        help_text = (
            "📖 **راهنمای ربات**\n\n"
            "🔹 **دستورات اصلی:**\n"
            "`/panel` - باز کردن پنل مدیریت\n\n"
            "🔹 **دستور فحش دادن:**\n"
            f"`{config['target']} رو بگا {{عدد}}`\n"
            f"مثال: `{config['target']} رو بگا 5`\n\n"
            "🔹 **نحوه کار:**\n"
            "1️⃣ روی پیام یک کاربر ریپلای بزنید\n"
            "2️⃣ دستور فحش دادن را بنویسید\n"
            "3️⃣ ربات به آن کاربر فحش می‌دهد\n\n"
            "🔹 **حالت خروجی:**\n"
            "• **متن**: فحش‌ها به صورت پیام متنی ارسال می‌شوند\n"
            "• **ویس**: فحش‌ها به صورت ویس (صوت) ارسال می‌شوند\n\n"
            "🔹 **مدیریت:**\n"
            "• تغییر تارگت: نام شخص مورد نظر را تغییر دهید\n"
            "• اضافه کردن سودو: کاربران جدید را اضافه کنید\n"
            "• اضافه کردن فحش: فحش‌های جدید به لیست اضافه می‌شوند\n\n"
            "🔹 **تعداد فحش‌ها:** ۱ تا ۱۰۰"
        )
        await callback.message.edit_text(help_text)
        await callback.answer()

# ===== هندلر پیام‌های متنی (با اولویت درست) =====
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    # ===== اول: تغییر تارگت =====
    if waiting_states.get("waiting_for_target") and user_id in AUTHORIZED_USERS:
        if text:
            old_target = config['target']
            config['target'] = text
            save_config(config)
            waiting_states["waiting_for_target"] = False
            await message.reply(
                f"✅ تارگت با موفقیت تغییر کرد!\n"
                f"🔄 از `{old_target}` به `{text}`\n\n"
                f"دستور جدید: `{text} رو بگا {{عدد}}`"
            )
            return
        else:
            await message.reply("❌ لطفاً یک نام معتبر وارد کنید.")
            return

    # ===== دوم: اضافه کردن فحش (قبل از سودو) =====
    if waiting_states.get("waiting_for_insult") and user_id in AUTHORIZED_USERS:
        if text:
            TEXT_INSULTS.append(text)
            VOICE_INSULTS.append(text)
            waiting_states["waiting_for_insult"] = False
            await message.reply(
                f"✅ فحش `{text}` با موفقیت به لیست اضافه شد!\n"
                f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}"
            )
            return
        else:
            await message.reply("❌ لطفاً یک فحش معتبر وارد کنید.")
            return

    # ===== سوم: اضافه کردن سودو =====
    if waiting_states.get("waiting_for_sudo") and user_id in AUTHORIZED_USERS:
        if text.isdigit():
            new_sudo = int(text)
            if new_sudo not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.append(new_sudo)
                await message.reply(f"✅ سودو با آیدی `{new_sudo}` با موفقیت اضافه شد!")
            else:
                await message.reply(f"❌ این کاربر قبلاً در لیست سودوها است!")
            waiting_states["waiting_for_sudo"] = False
            return
        else:
            await message.reply("❌ لطفاً یک آیدی عددی معتبر وارد کنید (فقط اعداد).")
            return

    # ===== چهارم: دستور فحش دادن =====
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
    number = int(number_text_english)

    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    # ===== ارسال فحش‌ها =====
    CHUNK_SIZE = 4
    insult_list = VOICE_INSULTS if config.get("output_mode") == "voice" else TEXT_INSULTS
    
    for i in range(number):
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(insult_list)
            chunk.append(f"{config['target']} {insult_list[index]}")
        
        insult_text = " ".join(chunk)
        
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
