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

# ===== اطمینان از وجود پوشه =====
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

# ===== لیست سودوها (آیدی عددی) =====
AUTHORIZED_USERS = [
    8273038319,
    7667099146,
    8811402550,
]

# ===== فحش‌های متنی (بدون حرکات) =====
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

# ===== فحش‌های صوتی (با حرکات درست و تلفظ "کونی") =====
VOICE_INSULTS = [
    "بی‌شَرَف کون طاقار",
    "مادَر جِنده کَثافَت",
    "خار کونی پِدَر سَگ",
    "پِدَر سَگ مادَر کونی",
    "حَرام‌زادِه کُس‌کِش",
    "بی‌غِیرَت مادَر جِنده",
    "بی‌شَرَف پِدَر کونی",
    "کَثنَنَت مادَر کونی",
    "کِس‌نِنِه پِدَر سَگ",
    "مادَر کونی بی‌شَرَف",
    "کیر و کُس دالگَت مادَر جِنده",
    "مادَرَت زیرِمِه پِدَر سَگ",
    "مادَرَت را کُس دار زَدَم کونی",
    "گاو صِفَت مادَر جِنده",
    "نَنِه جِنده پِدَر کونی",
    "کیرَت تو کونَت پِدَر سَگ",
    "مادَرَت تو سَگ‌خونِه کُس‌کِش",
    "پِدَرَت خایِه‌مال مادَر جِنده",
    "خواهَرَت جِنده‌سِت کونی",
    "کونی حَرام‌زادِه پِدَر سَگ",
    "اهل کون و کُس مادَر جِنده",
    "مادَرَت را گاییدِن بی‌شَرَف",
    "نَنِه‌ت را کون پِدَر کونی",
    "پِدَرَت را کون مادَر جِنده",
    "کُس کِش پِدَر سَگ",
    "کونی پِدَر سَگ مادَر جِنده",
    "مادَر جِنده‌زادِه کُس‌کِش",
    "کونی بی‌حَیا مادَر کونی",
    "مادَرَت را کیر پِدَر سَگ",
    "خواهَرَت را کیر جِنده",
    "کُس نَنَت مادَر جِنده",
    "کیر نَنَت پِدَر کونی",
    "تو کون مادَرَت پِدَر سَگ",
    "بِرو گوه بِخُور مادَر جِنده",
    "کونَش گاییدِن بی‌شَرَف",
    "مادَرَت گاو کُس‌کِش",
    "پِدَرَت سَگ کونی",
    "بی‌مَغز کونی مادَر جِنده",
    "کُس و کیر تو کونَت پِدَر سَگ",
    "بی‌عَقل مادَر کونی",
    "بی‌شُعور پِدَر کونی",
    "بی‌حَیا مادَر جِنده",
    "بی‌مُرُوَت کُس‌کِش",
    "بی‌عِزَت پِدَر سَگ",
    "بی‌آبرو مادَر جِنده",
    "بی‌هَویَّت کونی",
    "بی‌اصالَت پِدَر کونی",
    "کَثافَت مادَر جِنده",
    "خائِن پِدَر سَگ",
    "پُست مادَر کونی",
    "حَقیر بی‌شَرَف",
    "اَبلَه کُس‌کِش",
    "نادان پِدَر کونی",
    "اَلاغ مادَر جِنده",
    "خَر پِدَر سَگ",
    "گاو کُس‌کِش",
    "سَگ مادَر جِنده",
    "خوک پِدَر کونی",
    "مار بی‌شَرَف",
    "عَقرَب کونی",
    "کِرْم مادَر جِنده",
    "اَنگَل پِدَر سَگ",
    "زالو کُس‌کِش",
    "رِذل مادَر کونی",
    "نَنگ پِدَر کونی",
    "عار بی‌شَرَف",
    "فاحِشِه مادَر جِنده",
    "روسپی کونی",
    "بَدکارِه پِدَر سَگ",
    "هَرزِه مادَر جِنده",
    "بی‌عِفَّت کُس‌کِش",
    "لااَبالی پِدَر کونی",
    "وَلَنگار مادَر جِنده",
    "بی‌بَندوبار پِدَر سَگ",
    "بی‌سَر و پا کونی",
    "بی‌ریشِه مادَر جِنده",
    "بی‌اَصل پِدَر کونی",
    "بی‌نِسب کُس‌کِش",
    "بی‌تَبار مادَر جِنده",
    "بی‌خانوادِه پِدَر سَگ",
    "بی‌پِدَر مادَر کونی",
    "بی‌مادَر پِدَر کونی",
    "یَتیم کونی",
    "طَرد شُدِه مادَر جِنده",
    "رانِه شُدِه پِدَر سَگ",
    "لَعَنتی کُس‌کِش",
    "مَلعون مادَر جِنده",
    "گُناهکار پِدَر کونی",
    "مُجرِم بی‌شَرَف",
    "خَبیث مادَر جِنده",
    "پَلید کونی",
    "ناپاک پِدَر سَگ",
    "چِرکین مادَر کونی",
    "کَثیف کُس‌کِش",
    "مُتَعَفِن پِدَر کونی",
    "گَندیدِه مادَر جِنده",
    "مُردِه پِدَر سَگ",
    "زامبی کونی",
    "اَهریمَن مادَر جِنده",
    "شیطان پِدَر کونی",
]

# ===== تابع چسباندن هوشمند فحش‌ها =====
def smart_join_insults(target, insult_list):
    """
    چسباندن هوشمند فحش‌ها به تارگت با "ـِ" یا فاصله
    مثال: مسعود + پدرسگ + مادرکونی → مسعودِ پدرسگِ مادرکونی
    """
    # اگه فقط یه فحش باشه، همون رو با تارگت برمی‌گردونیم
    if len(insult_list) == 1:
        return f"{target} {insult_list[0]}"
    
    # چسباندن با "ـِ" برای فحش‌های مرکب
    # کلمات فارسی که به حرف بی‌صدا ختم میشن، "ـِ" میگیرن
    result = target
    for insult in insult_list:
        # اگه کلمه به حرف بی‌صدا ختم بشه، "ـِ" اضافه کن
        if insult and insult[-1] not in "آاآهیوی":
            result += "ِ " + insult
        else:
            result += " " + insult
    return result

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

# ===== ذخیره تنظیمات گروه =====
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

# ===== تبدیل متن به ویس با Edge TTS (صدای مردانه) =====
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

# ===== کیبورد شیشه‌ای پنل =====
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

# ===== دستور /panel =====
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

# ===== پردازش دکمه‌ها =====
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
            "🎯 **تغییر تارگت**\n"
            "لطفاً نام شخص جدید را وارد کنید.\n"
            "مثال: `هینا`\n\n"
            f"تارگت فعلی: {config['target']}"
        )
        waiting_states[f"{chat_id}_waiting_for_target"] = True
        await callback.answer()

    elif callback.data == "add_sudo":
        await callback.message.edit_text(
            "➕ **اضافه کردن سودو جدید**\n"
            "لطفاً آیدی عددی سودو جدید را وارد کنید.\n"
            "مثال: `123456789`\n\n"
            "برای پیدا کردن آیدی عددی، به @userinfobot بروید."
        )
        waiting_states[f"{chat_id}_waiting_for_sudo"] = True
        await callback.answer()

    elif callback.data == "add_insult":
        await callback.message.edit_text(
            "➕ **اضافه کردن فحش جدید**\n"
            "لطفاً فحش جدید را وارد کنید:\n"
            "مثال: `مادرکونی`\n\n"
            f"تعداد فحش‌ها: {len(TEXT_INSULTS)}"
        )
        waiting_states[f"{chat_id}_waiting_for_insult"] = True
        await callback.answer()

    elif callback.data == "output_mode":
        if config.get("output_mode") == "text":
            config["output_mode"] = "voice"
        else:
            config["output_mode"] = "text"
        save_group_config(chat_id, config)
        
        await callback.message.edit_text(
            f"🔧 **تنظیمات ربات فاکر - گروه {chat_id}**\n\n"
            f"👤 تارگت فعلی: {config['target']}\n"
            f"🎙️ حالت خروجی: {'ویس' if config.get('output_mode') == 'voice' else 'متن'}\n"
            f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}\n"
            f"👥 تعداد سودوها: {len(AUTHORIZED_USERS)}\n\n"
            f"✅ حالت خروجی به **{'ویس' if config.get('output_mode') == 'voice' else 'متن'}** تغییر کرد!",
            reply_markup=panel_keyboard(config)
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

# ===== هندلر پیام‌های متنی =====
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""

    config = load_group_config(chat_id)

    # ===== ۱. تغییر تارگت =====
    if waiting_states.get(f"{chat_id}_waiting_for_target") and user_id in AUTHORIZED_USERS:
        if text:
            old_target = config['target']
            config['target'] = text
            save_group_config(chat_id, config)
            waiting_states[f"{chat_id}_waiting_for_target"] = False
            await message.reply(
                f"✅ تارگت این گروه با موفقیت تغییر کرد!\n"
                f"🔄 از `{old_target}` به `{text}`\n\n"
                f"دستور جدید: `{text} رو بگا {{عدد}}`"
            )
        else:
            await message.reply("❌ لطفاً یک نام معتبر وارد کنید.")
        return

    # ===== ۲. اضافه کردن فحش =====
    if waiting_states.get(f"{chat_id}_waiting_for_insult") and user_id in AUTHORIZED_USERS:
        if text:
            TEXT_INSULTS.append(text)
            VOICE_INSULTS.append(text)
            waiting_states[f"{chat_id}_waiting_for_insult"] = False
            await message.reply(
                f"✅ فحش `{text}` با موفقیت به لیست اضافه شد!\n"
                f"📝 تعداد فحش‌ها: {len(TEXT_INSULTS)}"
            )
        else:
            await message.reply("❌ لطفاً یک فحش معتبر وارد کنید.")
        return

    # ===== ۳. اضافه کردن سودو =====
    if waiting_states.get(f"{chat_id}_waiting_for_sudo") and user_id in AUTHORIZED_USERS:
        if text.isdigit():
            new_sudo = int(text)
            if new_sudo not in AUTHORIZED_USERS:
                AUTHORIZED_USERS.append(new_sudo)
                await message.reply(f"✅ سودو با آیدی `{new_sudo}` با موفقیت اضافه شد!")
            else:
                await message.reply(f"❌ این کاربر قبلاً در لیست سودوها است!")
        else:
            await message.reply("❌ لطفاً یک آیدی عددی معتبر وارد کنید (فقط اعداد).")
        waiting_states[f"{chat_id}_waiting_for_sudo"] = False
        return

    # ===== ۴. دستور فحش دادن =====
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

    # ===== ارسال فحش‌ها با چسباندن هوشمند =====
    CHUNK_SIZE = 4
    insult_list = VOICE_INSULTS if config.get("output_mode") == "voice" else TEXT_INSULTS
    
    for i in range(number):
        # انتخاب ۴ فحش
        chunk = []
        for j in range(CHUNK_SIZE):
            index = (i * CHUNK_SIZE + j) % len(insult_list)
            chunk.append(insult_list[index])
        
        # چسباندن هوشمند فحش‌ها
        insult_text = smart_join_insults(config['target'], chunk)
        
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
