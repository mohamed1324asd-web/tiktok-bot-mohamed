import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
from flask import Flask
from threading import Thread

# إعدادات البوت
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home(): return "✅ Bot is Online!"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# تخزين مؤقت للروابط عشان نعرف المستخدم اختار إيه لأي رابط
user_data = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "<b>مرحباً بك في بوت الـ VIP العالمي! 💎</b>\n\n"
        "أرسل رابط الفيديو الآن واختر الصيغة المناسبة لك.\n\n"
        "<i>المطور: @i_wi_w</i>"
    )
    await message.reply(welcome_text, parse_mode='HTML')

# استقبال الرابط وعرض خيارات (فيديو أو صوت)
@dp.message_handler(lambda message: message.text.startswith("http"))
async def ask_format(message: types.Message):
    url = message.text
    user_data[message.from_user.id] = url # حفظ الرابط مؤقتاً
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 فيديو (Video)", callback_data="opt_video"))
    markup.add(InlineKeyboardButton("🎵 صوت (MP3)", callback_data="opt_audio"))
    
    await message.reply("⚡️ وصل الرابط! اختر ماذا تريد استخراجه:", reply_markup=markup)

# معالجة الضغط على الأزرار
@dp.callback_query_handler(lambda c: c.data.startswith('opt_'))
async def process_options(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    url = user_data.get(user_id)
    
    if not url:
        await callback_query.answer("⚠️ حدث خطأ، أرسل الرابط مرة أخرى.")
        return

    if callback_query.data == "opt_audio":
        await callback_query.message.edit_text("⏳ جاري تحويل الفيديو إلى ملف صوتي...")
        await download_and_send(callback_query.message, url, is_audio=True)
    
    elif callback_query.data == "opt_video":
        # عرض خيارات الجودة
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🌟 جودة عالية (High)", callback_data="res_best"))
        markup.add(InlineKeyboardButton("📱 جودة متوسطة (Medium)", callback_data="res_medium"))
        await callback_query.message.edit_text("اختر جودة الفيديو المطلوبة:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('res_'))
async def process_video_res(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    url = user_data.get(user_id)
    quality = "best" if callback_query.data == "res_best" else "worst"
    
    await callback_query.message.edit_text(f"⏳ جاري تحميل الفيديو بجودة {'عالية' if quality=='best' else 'متوسطة'}...")
    await download_and_send(callback_query.message, url, is_audio=False, quality=quality)

async def download_and_send(message, url, is_audio=False, quality="best"):
    filename = "downloaded_file"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'outtmpl': filename,
    }

    if is_audio:
        ydl_opts['format'] = 'bestaudio/best'
        extension = ".mp3"
    else:
        ydl_opts['format'] = f'{quality}video+bestaudio/best'
        extension = ".mp4"

    ydl_opts['outtmpl'] = filename + extension

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            final_file = filename + extension
            
            with open(final_file, 'rb') as file:
                if is_audio:
                    await message.answer_audio(file, caption="🎵 تم استخراج الصوت بنجاح\nالمطور: @i_wi_w")
                else:
                    await message.answer_video(file, caption="✅ تم استخراج الفيديو بنجاح\nالمطور: @i_wi_w")
            
            os.remove(final_file)
            await message.delete() # حذف رسالة الانتظار

    except Exception as e:
        await message.answer("❌ عذراً، هذا الرابط غير مدعوم حالياً أو حدث خطأ.")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
    
