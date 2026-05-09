import logging
import asyncio
from aiogram import Bot, Dispatcher, types

# التوكن بتاعك
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

# إعداد اللوج
logging.basicConfig(level=logging.INFO)

# تشغيل البوت والديسباتشر بالإصدار الجديد
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! البوت شغال دلوقتي على السيرفر 100% ✅")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"وصلني الرابط: {message.text}\nالبوت متصل وشغال أهو!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
