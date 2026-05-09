import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import yt_dlp
from flask import Flask
from threading import Thread

# --- الإعدادات الأساسية ---
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"
ADMIN_ID = 8416486845 
CHANNEL_USER = "@i_wi_w" # يوزر قناتك هنا (تأكد إن البوت أدمن في القناة)
CHANNEL_LINK = "https://t.me/i_wi_w" # رابط قناتك

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

users_file = "users.txt"
if not os.path.exists(users_file): open(users_file, "w").close()

def add_user(user_id):
    with open(users_file, "r") as f:
        existing_users = f.read().splitlines()
    if str(user_id) not in existing_users:
        with open(users_file, "a") as f:
            f.write(f"{user_id}\n")

@app.route('/')
def home(): return "✅ Bot is Online!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- دالة فحص الاشتراك الإجباري ---
async def check_subscribe(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USER, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        # لو البوت مش أدمن في القناة أو اليوزر غلط هيسمح بالتحميل عشان البوت ميتعطلش
        return True

def subscribe_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 اشترك في القناة أولاً", url=CHANNEL_LINK))
    markup.add(InlineKeyboardButton("✅ تم الاشتراك (تفعيل)", callback_data="check_sub"))
    return markup

# --- لوحة مفاتيح الأدمن ---
def admin_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📊 الإحصائيات"), KeyboardButton("📢 إذاعة (Broadcast)"))
    return markup

# --- رسالة الترحيب ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    add_user(message.from_user.id)
    
    if not await check_subscribe(message.from_user.id) and message.from_user.id != ADMIN_ID:
        await message.reply(f"⚠️ عذراً! يجب عليك الاشتراك في قناة البوت أولاً لاستخدامه.\n\nاشترك هنا: {CHANNEL_USER}", reply_markup=subscribe_markup())
        return

    if message.from_user.id == ADMIN_ID:
        await message.reply("أهلاً بك يا مطورنا! تم تفعيل لوحة التحكم.", reply_markup=admin_keyboard())
    
    await message.reply("<b>مرحباً بك في بوت التحميل العالمي! 💎</b>\n\nأرسل رابط الفيديو الآن..", parse_mode='HTML')

# --- معالجة التحقق من الاشتراك ---
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def verify_sub(callback_query: types.CallbackQuery):
    if await check_subscribe(callback_query.from_user.id):
        await callback_query.message.edit_text("✅ شكراً لثقتك! تم تفعيل البوت بنجاح. أرسل الرابط الآن.")
    else:
        await callback_query.answer("❌ أنت لم تشترك في القناة بعد!", show_alert=True)

# --- وظائف الأدمن (إحصائيات وإذاعة) ---
@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text == "📊 الإحصائيات")
async def show_stats(message: types.Message):
    with open(users_file, "r") as f:
        count = len(f.readlines())
    await message.reply(f"📊 عدد المستخدمين: {count}")

@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text == "📢 إذاعة (Broadcast)")
async def ask_broadcast(message: types.Message):
    await message.reply("أرسل رسالة الإذاعة الآن.")

@dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and not message.text.startswith("/") and not message.text.startswith("http"))
async def do_broadcast(message: types.Message):
    if message.text in ["📊 الإحصائيات", "📢 إذاعة (Broadcast)"]: return
    with open(users_file, "r") as f:
        users = f.read().splitlines()
    count = 0
    for user in users:
        try: await bot.send_message(user, message.text); count += 1
        except: pass
    await message.reply(f"✅ تم الإرسال لـ {count} مستخدم.")

# --- نظام التحميل (مع فحص الاشتراك) ---
user_data = {}

@dp.message_handler(lambda message: message.text.startswith("http"))
async def handle_link(message: types.Message):
    add_user(message.from_user.id)
    
    # فحص الاشتراك قبل البدء
    if not await check_subscribe(message.from_user.id) and message.from_user.id != ADMIN_ID:
        await message.reply("⚠️ اشترك في القناة أولاً لتتمكن من التحميل!", reply_markup=subscribe_markup())
        return

    user_data[message.from_user.id] = message.text
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 فيديو", callback_data="opt_video"), InlineKeyboardButton("🎵 صوت", callback_data="opt_audio"))
    await message.reply("⚡️ اختر النوع:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('opt_'))
async def process_options(callback_query: types.CallbackQuery):
    url = user_data.get(callback_query.from_user.id)
    if callback_query.data == "opt_audio":
        await callback_query.message.edit_text("⏳ جاري التحميل كصوت...")
        await download_and_send(callback_query.message, url, is_audio=True)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🌟 عالية", callback_data="res_best"), InlineKeyboardButton("📱 متوسطة", callback_data="res_medium"))
        await callback_query.message.edit_text("اختر الجودة:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('res_'))
async def process_video_res(callback_query: types.CallbackQuery):
    url = user_data.get(callback_query.from_user.id)
    q = "best" if callback_query.data == "res_best" else "worst"
    await callback_query.message.edit_text("⏳ جاري التحميل...")
    await download_and_send(callback_query.message, url, is_audio=False, quality=q)

async def download_and_send(message, url, is_audio=False, quality="best"):
    filename = "file" + (".mp3" if is_audio else ".mp4")
    opts = {'quiet': True, 'outtmpl': filename, 'format': 'bestaudio/best' if is_audio else f'{quality}video+bestaudio/best'}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            with open(filename, 'rb') as f:
                caption = "المطور: @i_wi_w"
                if is_audio: await message.answer_audio(f, caption=caption)
                else: await message.answer_video(f, caption=caption)
            os.remove(filename)
            await message.delete()
    except: await message.answer("❌ حدث خطأ في الرابط!")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
    
