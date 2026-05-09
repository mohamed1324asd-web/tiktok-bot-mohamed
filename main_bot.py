import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# 1. إعداد السيرفر الوهمي عشان Render ميفصلش
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# 2. إعدادات البوت
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! البوت شغال دلوقتي وما بيفصلش ✅")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"وصلني: {message.text}")

if __name__ == '__main__':
    # تشغيل السيرفر الوهمي في الخلفية
    Thread(target=run).start()
    # تشغيل البوت مع مسح أي رسايل قديمة معلقة
    executor.start_polling(dp, skip_updates=True)
