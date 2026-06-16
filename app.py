import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ---------- تنظیمات از محیط Render ----------
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ---------- لیست سودوها ----------
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ---------- لیست فحش‌های به‌روز شده (با فحش‌های جدید شما) ----------
INSULTS = [
    # 🔥 فحش‌های جدید شما:
    "🤬 بی‌ناموس!",
    "🤬 مادرجنده!",
    "🤬 یه روز داشتیم میرفتیم تقمون خورد به مادر اوا!",
    "🤬 کثننت!",
    "🤬 کسننه!",
    "🤬 مادرکونی!",
    "🤬 خارکونی!",
    "🤬 کیر و کس دالگت!",
    "🤬 پدرسگ!",
    "🤬 مادرت زیرمه!",
    "🤬 مادرتو از کس دار زدم!",
    "🤬 حرومزاده!",
    
    # 💀 فحش‌های خیلی بد (اضافی):
    "💀 کونی بی‌شرف!",
    "💀 گاوصفت بی‌غیرت!",
    "💀 ننه‌جنده!",
    "💀 کیرتو تو کونت!",
    "💀 مادرت تو سگ‌خونه!",
    "💀 پدرت خایه‌مال!",
    "💀 خواهرت جنده‌ست!",
    "💀 بی‌شرف بی‌ناموس!",
    "💀 کونی حرومزاده!",
    "💀 اهل کون و کس!",
    "💀 مادرتو گاییدن!",
    "💀 ننه‌تو کون!",
    "💀 پدرتو کون!",
    "💀 کس کش!",
    "💀 کونی پدرسگ!",
    "💀 مادرجنده‌زاده!",
    "💀 بی‌غیرت بی‌شرف!",
    "💀 کونی بی‌حیا!",
    "💀 مادرتو کیر!",
    "💀 خواهرتو کیر!",
    "💀 کس ننت!",
    "💀 کیر ننت!",
    "💀 تو کون مادرت!",
    "💀 برو گوه بخور!",
    "💀 کونشو گاییدن!",
    "💀 مادرتو گاو!",
    "💀 پدرتو سگ!",
    "💀 بی‌مغز کونی!",
    "💀 کس و کیر تو کونت!",
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handler(message: types.Message):
    user_id = message.from_user.id

    # بررسی دسترسی (فقط سودوها)
    if user_id not in AUTHORIZED_USERS:
        await message.reply("⛔ شما دسترسی به این ربات ندارید!")
        return

    # بررسی ریپلای
    if not message.reply_to_message:
        await message.reply("⚠️ روی یک پیام ریپلای بزنید و عدد مورد نظر را بفرستید.")
        return

    # بررسی عدد بودن پیام
    if not message.text or not message.text.isdigit():
        await message.reply("❌ لطفاً یک عدد وارد کنید.")
        return

    number = int(message.text)
    
    # محدودیت ۱ تا ۱۰۰
    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    # ارسال فحش‌ها به صورت ریپلای
    for i in range(number):
        insult = INSULTS[i % len(INSULTS)]
        await message.reply_to_message.reply(f"{i+1}️⃣ {insult}")
        await asyncio.sleep(0.3)  # تاخیر برای جلوگیری از محدودیت

async def main():
    print("🤖 ربات با Aiogram روشن شد!")
    print(f"✅ تعداد کاربران مجاز: {len(AUTHORIZED_USERS)}")
    print(f"✅ تعداد فحش‌ها: {len(INSULTS)}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
