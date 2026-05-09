import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# التوكن بتاعك
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

# إعداد اللوج
logging.basicConfig(level=logging.INFO)

# تشغيل البوت
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! البوت شغال دلوقتي 100%. ابعتلي أي رابط وهرد عليك.")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"وصلني الرابط: {message.text}\nالبوت متصل بالسيرفر ✅")

if __name__ == '__main__':
    # الكود ده متوافق مع الإصدار اللي على Render
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
    
