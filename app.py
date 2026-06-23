import asyncio
import os
import re
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from flask import Flask

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ===== لیست سودوها (آیدی عددی) =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== لیست فحش‌های سنگین =====
INSULTS = [
    "مادرجنده کثافت",
    "بی‌ناموس پدرسگ",
    "کسمادر کونی",
    "حرومزاده بی‌غیرت",
    "پدرسگ مادرکونی",
    "خارکونی بی‌شرف",
    "کون طاقار کسکش",
    "بی‌شرف بی‌ناموس",
    "مادرتو گاییدن",
    "کیر تو کونت پدرسگ",
    "ننه‌جنده خایه‌مال",
    "هرزه بی‌عفّت",
    "لاابالی ولنگار",
    "بی‌بندوبار کونی",
    "چرکین کثیف",
    "گندیده متعفن",
    "مرده مرداب",
    "اهریمن شیطان",
    "کونی بی‌حیا",
    "مادرجنده‌زاده",
]

# ===== تابع تبدیل اعداد فارسی به انگلیسی =====
def convert_persian_to_english(text):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    return text

# ===== تابع چسباندن فحش‌ها =====
def join_insults(target, insult_list):
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== دستور /panel (فقط سودوها) =====
@dp.message(Command("panel"))
async def panel_command(message: Message):
    user_id = message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await message.reply("⛔ شما دسترسی به این پنل ندارید!")
        return
    await message.reply(
        f"🔧 **تنظیمات ربات فاکر**\n\n"
        f"👤 تعداد سودوها: {len(AUTHORIZED_USERS)}\n"
        f"📝 تعداد فحش‌ها: {len(INSULTS)}\n\n"
        f"⚡ **دستور فحش دادن:**\n"
        f"`{target} رو بگا {{عدد}}`\n"
        f"مثال: `مسعود رو بگا 5`\n\n"
        f"🔹 روی پیام ریپلای بزنید و عدد بنویسید",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 سازنده", url="https://t.me/TaakaaOrg")]
        ])
    )

# ===== هندلر پیام‌ها =====
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    # ===== چک کردن سودو بودن =====
    if user_id not in AUTHORIZED_USERS:
        return

    # ===== چک کردن ریپلای =====
    if not message.reply_to_message:
        return

    # ===== بررسی دستور فحش دادن =====
    pattern = r'^(.*?) رو بگا\s+(\d+)$'
    match = re.match(pattern, text)
    
    if not match:
        return

    target = match.group(1).strip()
    number_text = match.group(2)
    number_text_english = convert_persian_to_english(number_text)
    
    if not number_text_english.isdigit():
        return
        
    number = int(number_text_english)

    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    # ===== ارسال فحش‌ها =====
    CHUNK_SIZE = 4
    
    for i in range(number):
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(INSULTS)
            chunk.append(INSULTS[index])
        
        insult_text = join_insults(target, chunk)
        await message.reply_to_message.reply(insult_text)
        await asyncio.sleep(1.5)  # تاخیر ۱.۵ ثانیه برای جلوگیری از محدودیت

# ===== Flask (برای نگه‌داشتن ربات روشن) =====
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
    print("🤖 ربات فحاش فعال شد...")
    asyncio.run(main())
