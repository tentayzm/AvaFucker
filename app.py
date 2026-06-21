import asyncio
import os
import re
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from flask import Flask
from gtts import gTTS
import io

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ===== لیست سودوها =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== لیست فحش‌ها =====
INSULTS = [
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

# ===== تابع چسباندن با فرمت خاص =====
def join_insults_custom(target, insult_list):
    """
    چسباندن فحش‌ها با فرمت:
    - اولین فحش: {تارگت}ِ
    - فحش‌های وسط: {فحش}ِ
    - آخرین فحش: {فحش} (بدون چیزی)
    - اگه به "ا" ختم شد: {فحش}ی
    """
    if not insult_list:
        return target
    
    vowels = "اآ"
    
    result = target + "ِ "
    
    for i, insult in enumerate(insult_list):
        if i == len(insult_list) - 1:
            result += insult
        else:
            if insult and insult[-1] in vowels:
                result += insult + "ی "
            else:
                result += insult + "ِ "
    
    return result.strip()

# ===== تبدیل متن به ویس =====
async def send_voice_insult(reply_to_message, insult_text):
    try:
        tts = gTTS(text=insult_text, lang="ar", slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        await reply_to_message.reply_voice(
            voice=types.BufferedInputFile(
                audio_bytes.read(), 
                filename="insult.ogg"
            )
        )
    except Exception as e:
        await reply_to_message.reply(f"❌ خطا در ساخت ویس: {e}")

# ===== تبدیل عدد فارسی به انگلیسی =====
def convert_persian_to_english(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    return text

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== کیبورد شیشه‌ای پنل =====
def panel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 تغییر تارگت", callback_data="change_target"),
            InlineKeyboardButton(text="➕ اضافه کردن فحش", callback_data="add_insult")
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
    
    # بارگذاری تارگت از فایل
    try:
        with open("target.txt", "r") as f:
            target = f.read().strip()
    except:
        target = "مسعود"
    
    await message.reply(
        f"🔧 **تنظیمات ربات فحاش**\n\n"
        f"👤 تارگت فعلی: {target}\n"
        f"📝 تعداد فحش‌ها: {len(INSULTS)}\n"
        f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
        f"یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=panel_keyboard()
    )

# ===== پردازش دکمه‌ها =====
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await callback.answer("⛔ شما دسترسی ندارید!", show_alert=True)
        return

    if callback.data == "change_target":
        await callback.message.edit_text(
            "🎯 **تغییر تارگت**\n"
            "لطفاً نام شخص جدید را وارد کنید.\n"
            "مثال: `هینا`\n\n"
            "تارگت فعلی رو می‌تونی با دستور `/panel` ببینی."
        )
        # تنظیم حالت انتظار برای دریافت نام جدید
        dp["waiting_for_target"] = True
        await callback.answer()

    elif callback.data == "add_insult":
        await callback.message.edit_text(
            "➕ **اضافه کردن فحش جدید**\n"
            "لطفاً فحش جدید را وارد کنید:\n"
            "مثال: `مادرکونی`\n\n"
            f"تعداد فحش‌ها: {len(INSULTS)}"
        )
        dp["waiting_for_insult"] = True
        await callback.answer()

    elif callback.data == "help":
        help_text = (
            "📖 **راهنمای ربات**\n\n"
            "🔹 **دستورات اصلی:**\n"
            "`/panel` - باز کردن پنل مدیریت\n\n"
            "🔹 **دستور فحش دادن:**\n"
            "روی پیام یک کاربر ریپلای بزنید و عدد را بنویسید.\n"
            "مثال: `5`\n\n"
            "🔹 **نحوه کار:**\n"
            "1️⃣ روی پیام یک کاربر ریپلای بزنید\n"
            "2️⃣ عدد مورد نظر را بنویسید (۱ تا ۱۰۰)\n"
            "3️⃣ ربات به آن کاربر فحش می‌دهد\n\n"
            "🔹 **مدیریت:**\n"
            "• تغییر تارگت: نام شخص مورد نظر را تغییر دهید\n"
            "• اضافه کردن فحش: فحش‌های جدید به لیست اضافه می‌شوند\n\n"
            "🔹 **تعداد فحش‌ها:** ۱ تا ۱۰۰"
        )
        await callback.message.edit_text(help_text)
        await callback.answer()

# ===== هندلر پیام‌های متنی =====
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    # ===== پردازش تغییر تارگت =====
    if dp.get("waiting_for_target") and user_id in AUTHORIZED_USERS:
        if text:
            # ذخیره تارگت جدید در فایل
            with open("target.txt", "w") as f:
                f.write(text)
            dp["waiting_for_target"] = False
            await message.reply(
                f"✅ تارگت با موفقیت تغییر کرد!\n"
                f"🔄 به `{text}`\n\n"
                f"از این به بعد فحش‌ها به {text} می‌رسه!"
            )
            return
        else:
            await message.reply("❌ لطفاً یک نام معتبر وارد کنید.")
            return

    # ===== پردازش اضافه کردن فحش =====
    if dp.get("waiting_for_insult") and user_id in AUTHORIZED_USERS:
        if text:
            INSULTS.append(text)
            dp["waiting_for_insult"] = False
            await message.reply(
                f"✅ فحش `{text}` با موفقیت به لیست اضافه شد!\n"
                f"📝 تعداد فحش‌ها: {len(INSULTS)}"
            )
            return
        else:
            await message.reply("❌ لطفاً یک فحش معتبر وارد کنید.")
            return

    # ===== دستور فحش دادن (فقط با ریپلای) =====
    if user_id not in AUTHORIZED_USERS:
        return

    if not message.reply_to_message:
        return

    # چک کردن عدد بودن پیام
    if not text.isdigit():
        return

    number_text = convert_persian_to_english(text)
    number = int(number_text)

    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    # ===== بارگذاری تارگت از فایل =====
    try:
        with open("target.txt", "r") as f:
            target = f.read().strip()
    except:
        target = "مسعود"

    # ===== ارسال فحش‌ها با چسباندن =====
    CHUNK_SIZE = 4
    
    for i in range(number):
        # انتخاب ۴ فحش
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(INSULTS)
            chunk.append(INSULTS[index])
        
        # چسباندن فحش‌ها
        insult_text = join_insults_custom(target, chunk)
        
        # انتخاب خروجی (ویس یا متن)
        await message.reply_to_message.reply(insult_text)
        await asyncio.sleep(0.5)

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
    print("🤖 ربات فحاش روشن شد!")
    asyncio.run(main())
