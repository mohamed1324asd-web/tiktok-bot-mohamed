import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# التوكن الجديد بتاعك (متصلح وجاهز)
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"

# إعدادات اللوج عشان نعرف لو في مشاكل
logging.basicConfig(level=logging.INFO)

# تشغيل البوت
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("أهلاً يا محمد! أنا بوت تحميل فيديوهات تيك توك. ابعتلي الرابط وهجربهولك.")

@dp.message_handler()
async def echo(message: types.Message):
    # هنا هنضيف كود التحميل لاحقاً، دلوقتي بنجرب الاتصال
    await message.answer(f"وصلني الرابط: {message.text}\nالبوت شغال والتوكن سليم ✅")

if __name__ == '__main__':
    # تشغيل البوت مع تخطي مشكلة الـ Port في Render
    executor.start_polling(dp, skip_updates=True)
    
