import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! البوت شغال دلوقتي بإصدار 2 ومستقر ✅")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"وصلني: {message.text}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
