import logging
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# سيرفر Render الوهمي
app = Flask('')
@app.route('/')
def home(): return "Multi-Downloader Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! ابعتلي أي رابط فيديو (TikTok, Instagram, YouTube) وهحملهولك فوراً 🚀")

@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return await message.reply("من فضلك ابعت رابط صحيح")

    msg = await message.reply("جاري التحميل... انتظر ثواني ⏳")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            await bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة بوت محمد ✅")
        
        os.remove('video.mp4') # مسح الفيديو بعد الإرسال لتوفير مساحة
        await msg.delete()

    except Exception as e:
        await msg.edit(f"حدث خطأ: تأكد من أن الرابط عام وليس لحساب خاص.")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
    
