import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
from flask import Flask
from threading import Thread

# إعدادات البوت (التوكن الجديد بتاعك)
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

# إعداد اللوجات
logging.basicConfig(level=logging.INFO)

# تشغيل البوت
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# سيرفر وهمي عشان Render ما يقفلش البوت
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- رسالة الترحيب الفخمة ---
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
        "<i>بواسطة المطور: محمد 👨‍💻</i>"
    )
    await message.reply(welcome_text, parse_mode='HTML')

# --- نظام التحميل الذكي ---
@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    status_msg = await message.reply("⚡️ جاري معالجة الرابط.. استعد للإبهار!")

    # إعدادات yt-dlp لتحميل أفضل جودة
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = 'video.mp4'
            
            with open(filename, 'rb') as video:
                await message.reply_video(
                    video, 
                    caption=f"✅ تم استخراج الفيديو بنجاح عبر بوت محمد\n\n<i>المطور: @M_7_4_M_E_D</i>",
                    parse_mode='HTML'
                )
            
            os.remove(filename) # مسح الفيديو بعد الإرسال لتوفير المساحة
            await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ عذراً، حدث خطأ أثناء التحميل. تأكد من الرابط وحاول مجدداً.")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    keep_alive() # تشغيل السيرفر الوهمي
    executor.start_polling(dp, skip_updates=True)
