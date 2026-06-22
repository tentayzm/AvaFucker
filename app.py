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

# ===== لیست سودوها (فقط اینا میتونن استفاده کنن) =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== تنظیمات =====
CONFIG = {
    "target": "مسعود",
    "output_mode": "text",  # "text" یا "voice"
}

# ===== فحش‌های متنی (بدون اعراب) =====
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

# ===== فحش‌های صوتی (با اعراب برای تلفظ درست فارسی) =====
VOICE_INSULTS = [
    "مادَرجِنده",
    "بی‌ناموس",
    "کُسمادَر",
    "کونی",
    "پِدَر سَگ",
    "حَرام‌زادِه",
    "خار کُنی",
    "بی‌شَرَف",
    "بی‌غیرَت",
    "کَثافَت",
    "هَرزِه",
    "لااَبالی",
    "وَلَنگار",
    "بی‌بَندوبار",
    "بی‌سَروپا",
    "بی‌ریشِه",
    "بی‌اَصل",
    "بی‌نِسب",
    "بی‌تَبار",
    "بی‌خانوادِه",
    "بی‌پِدَر",
    "بی‌مادَر",
    "یَتیم",
    "طَرد شُدِه",
    "رانِه شُدِه",
    "لَعَنتی",
    "مَلعون",
    "گُناهکار",
    "مُجرِم",
    "خَبیث",
    "پَلید",
    "ناپاک",
    "چِرکین",
    "کَثیف",
    "مُتَعَفِن",
    "گَندیدِه",
    "مُردِه",
    "زامبی",
    "اَهریمَن",
    "شیطان",
    "کیر و کُس",
    "دالگَت",
    "زیرِمِه",
    "گاو صِفَت",
    "نَنِه جِنده",
    "خایِه‌مال",
    "جِنده",
    "کون",
    "کُس",
]

# ===== تابع حذف اعراب (فقط برای متن) =====
def remove_diacritics(text):
    diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    return re.sub(diacritics, '', text)

# ===== تابع چسباندن فحش‌ها با ترتیب خاص =====
def join_insults(target, insult_list):
    """
    چسباندن فحش‌ها با ترتیب:
    - اول: {تارگت} + ِ (یا ی اگه به آ ختم بشه)
    - دوم: {فحش}ی (با ی ربطی)
    - سوم به بعد: {فحش}ِ (با ِ)
    - آخر: {فحش} (بدون چیزی)
    """
    if not insult_list:
        return target
    
    # تشخیص آخرین حرف تارگت
    if target and target[-1] in "اآ":
        result = target + "ی "
    else:
        result = target + "ِ "
    
    for i, insult in enumerate(insult_list):
        if i == 0:
            # فحش اول: با ی ربطی
            result += insult + "ی "
        elif i == len(insult_list) - 1:
            # آخرین فحش: بدون چیزی
            result += insult
        else:
            # فحش‌های وسط: با ِ
            result += insult + "ِ "
    
    return result.strip()

# ===== تبدیل متن به ویس با gTTS (فارسی) =====
async def send_voice_insult(reply_to_message, insult_text):
    try:
        # حذف اعراب از متن برای gTTS (چون خودش تلفظ میکنه)
        clean_text = remove_diacritics(insult_text)
        
        tts = gTTS(text=clean_text, lang="fa", slow=False)
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

# ===== دیکشنری برای ذخیره حالت‌های انتظار =====
waiting_states = {
    "waiting_for_target": False,
    "waiting_for_sudo": False,
    "waiting_for_insult": False
}

# ===== کیبورد شیشه‌ای پنل =====
def panel_keyboard():
    mode_text = "🔊 ویس" if CONFIG.get("output_mode") == "voice" else "📝 متن"
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
            InlineKeyboardButton(text="📖 راهنما", callback_data="help")
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
        f"🔧 **تنظیمات ربات**\n\n"
        f"👤 تارگت فعلی: {CONFIG['target']}\n"
        f"🎙️ حالت خروجی: {'ویس' if CONFIG.get('output_mode') == 'voice' else 'متن'}\n"
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
            f"تارگت فعلی: {CONFIG['target']}"
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
        if CONFIG.get("output_mode") == "text":
            CONFIG["output_mode"] = "voice"
        else:
            CONFIG["output_mode"] = "text"
        
        await callback.message.edit_text(
            f"🔧 **تنظیمات ربات**\n\n"
            f"👤 تارگت فعلی: {CONFIG['target']}\n"
            f"🎙️ حالت خروجی: {'ویس' if CONFIG.get('output_mode') == 'voice' else 'متن'}\n"
            f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}\n"
            f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
            f"✅ حالت خروجی به **{'ویس' if CONFIG.get('output_mode') == 'voice' else 'متن'}** تغییر کرد!",
            reply_markup=panel_keyboard()
        )
        await callback.answer(f"حالت به {'ویس' if CONFIG.get('output_mode') == 'voice' else 'متن'} تغییر کرد!")

    elif callback.data == "help":
        help_text = (
            "📖 **راهنمای ربات**\n\n"
            "🔹 **دستورات اصلی:**\n"
            "`/panel` - باز کردن پنل مدیریت\n\n"
            "🔹 **دستور فحش دادن:**\n"
            f"`{CONFIG['target']} رو بگا {{عدد}}`\n"
            f"مثال: `{CONFIG['target']} رو بگا 5`\n\n"
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

# ===== هندلر پیام‌های متنی =====
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    # ===== فقط به سودوها پاسخ بده =====
    if user_id not in AUTHORIZED_USERS:
        return

    # ===== ۱. تغییر تارگت =====
    if waiting_states.get("waiting_for_target"):
        if text:
            old_target = CONFIG['target']
            CONFIG['target'] = text
            waiting_states["waiting_for_target"] = False
            await message.reply(
                f"✅ تارگت با موفقیت تغییر کرد!\n"
                f"🔄 از `{old_target}` به `{text}`\n\n"
                f"دستور جدید: `{text} رو بگا {{عدد}}`"
            )
        else:
            await message.reply("❌ لطفاً یک نام معتبر وارد کنید.")
        return

    # ===== ۲. اضافه کردن سودو =====
    if waiting_states.get("waiting_for_sudo"):
        if text.isdigit():
            new_sudo = int(text)
            if new_sudo not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.append(new_sudo)
                await message.reply(f"✅ سودو با آیدی `{new_sudo}` با موفقیت اضافه شد!")
            else:
                await message.reply(f"❌ این کاربر قبلاً در لیست سودوها است!")
        else:
            await message.reply("❌ لطفاً یک آیدی عددی معتبر وارد کنید (فقط اعداد).")
        waiting_states["waiting_for_sudo"] = False
        return

    # ===== ۳. اضافه کردن فحش =====
    if waiting_states.get("waiting_for_insult"):
        if text:
            TEXT_INSULTS.append(text)
            VOICE_INSULTS.append(text)
            waiting_states["waiting_for_insult"] = False
            await message.reply(
                f"✅ فحش `{text}` با موفقیت به لیست اضافه شد!\n"
                f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}"
            )
        else:
            await message.reply("❌ لطفاً یک فحش معتبر وارد کنید.")
        return

    # ===== ۴. دستور فحش دادن (فقط با ریپلای) =====
    if not message.reply_to_message:
        return

    # بررسی دستور "تارگت رو بگا {عدد}"
    pattern = rf'^{CONFIG["target"]} رو بگا\s+(\d+)$'
    match = re.match(pattern, text)
    
    if not match:
        return

    number_text = match.group(1)
    # تبدیل اعداد فارسی به انگلیسی
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for persian, english in persian_to_english.items():
        number_text = number_text.replace(persian, english)
    
    number = int(number_text)

    if not (1 <= number <= 100):
        await message.reply("❌ عدد بین ۱ تا ۱۰۰ وارد کنید.")
        return

    # ===== انتخاب لیست مناسب =====
    insult_list = VOICE_INSULTS if CONFIG.get("output_mode") == "voice" else TEXT_INSULTS
    CHUNK_SIZE = 4
    
    for i in range(number):
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(insult_list)
            chunk.append(insult_list[index])
        
        # چسباندن فحش‌ها با ترتیب خاص
        insult_text = join_insults(CONFIG['target'], chunk)
        
        if CONFIG.get("output_mode") == "voice":
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
