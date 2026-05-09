import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import URLInputFile

# توكن البوت
API_TOKEN = 8753125623:AAEYcN_dc8KwdJS7NQrph63arhQuISZSRTk

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.reply("🚀 البوت شغال الآن من Koyeb!\nابعت رابط تيك توك وهبعتلك الفيديو فوراً.")

    @dp.message()
    async def handle_video(message: types.Message):
        url = message.text
        if "http" not in url: return
        msg = await message.reply("⏳ جاري التحميل...")
        api_url = f"https://www.tikwm.com/api/?url={url}"
        try:
            async with aiohttp.ClientSession() as session_http:
                async with session_http.get(api_url) as resp:
                    data = await resp.json()
                    video_url = data.get('data', {}).get('play')
                    if video_url:
                        await message.answer_video(video=URLInputFile(f"https://www.tikwm.com{video_url}"))
                        await msg.delete()
        except:
            await msg.edit_text("❌ حدث خطأ، جرب تاني.")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
      
