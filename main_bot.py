import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
from flask import Flask
from threading import Thread

# إعدادات البوت (التوكن الخاص بك)
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

# إعداد اللوجات لمراقبة الأداء
logging.basicConfig(level=logging.INFO)

# تشغيل البوت والديسباتشر
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# سيرفر وهمي (Flask) لضمان استمرارية العمل على Render
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is Online and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 1. رسالة الترحيب (عند الضغط على Start) ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "<b>مرحباً بك في بوت الـ VIP العالمي! 💎</b>\n\n"
        "أنت الآن تستخدم أسرع أداة لتحميل الفيديوهات بجودة عالية ⚡️\n\n"
        "<b>الخدمات المتاحة حالياً:</b>\n"
        "• 📥 تحميل تيك توك (بدون علامة مائية)\n"
        "• 📸 ريلز إنستجرام وفيديوهات فيسبوك\n"
        "• 🎥 شورتس يوتيوب والمنصات العالمية\n"
        "• 🎵 استخراج الصوت من أي فيديو\n\n"
        "<b>كل ما عليك هو إرسال الرابط.. وسأقوم بالسحر! ✨</b>\n\n"
        "<i>المطور: @i_wi_w</i>"
    )
    await message.reply(welcome_text, parse_mode='HTML')

# --- 2. معالجة الروابط وتحميل الفيديوهات ---
@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    status_msg = await message.reply("⚡️ جاري معالجة الرابط.. استعد للإبهار!")

    # إعدادات yt-dlp للتحميل بأفضل جودة ممكنة
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات والتحميل
            info = ydl.extract_info(url, download=True)
            filename = 'video.mp4'
            
            # إرسال الفيديو للمستخدم بالبصمة الجديدة
            with open(filename, 'rb') as video:
                await message.reply_video(
                    video, 
                    caption=f"✅ تم استخراج الفيديو بنجاح\n\nالمطور: @i_wi_w",
                    parse_mode='HTML'
                )
            
            # تنظيف الملفات المؤقتة بعد الإرسال
            if os.path.exists(filename):
                os.remove(filename)
            
            await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ عذراً، حدث خطأ أثناء التحميل. تأكد من الرابط وحاول مجدداً.")
        logging.error(f"Error during download: {e}")

# --- 3. تشغيل البوت ---
if __name__ == '__main__':
    keep_alive() # تشغيل السيرفر الوهمي في الخلفية
    print("Bot is starting...")
    executor.start_polling(dp, skip_updates=True)
    
