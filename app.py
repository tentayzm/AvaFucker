import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from flask import Flask

BOT_TOKEN = os.environ.get('BOT_TOKEN')

AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

INSULTS = [
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
async def handler(message: Message):
    user_id = message.from_user.id

    if user_id not in AUTHORIZED_USERS:
        await message.reply("⛔ شما دسترسی به این ربات ندارید!")
        return

    if not message.reply_to_message:
        await message.reply("⚠️ روی یک پیام ریپلای بزنید و عدد مورد نظر را بفرستید.")
        return

    if not message.text or not message.text.isdigit():
        await message.reply("❌ لطفاً یک عدد وارد کنید.")
        return

    number = int(message.text)

    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    for i in range(number):
        insult = INSULTS[i % len(INSULTS)]
        await message.reply_to_message.reply(f"{i+1}️⃣ {insult}")
        await asyncio.sleep(0.3)

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
