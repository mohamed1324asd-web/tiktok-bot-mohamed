import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import yt_dlp
from flask import Flask
from threading import Thread

# --- الإعدادات الأساسية ---
API_TOKEN = "8753125623:AAEYcN_dc8KwdJS7NQrph63arhQulSZSRTk"
ADMIN_ID = 8416486845 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

# --- إدارة البيانات ---
USERS_FILE = "users.txt"
CONFIG_FILE = "channels_config.json"

if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"channels": ["@i_wi_w"], "status": "on"}, f)

def get_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def set_config(data):
    with open(CONFIG_FILE, "w") as f: json.dump(data, f)

def add_user(user_id):
    with open(USERS_FILE, "r") as f:
        if str(user_id) not in f.read():
            with open(USERS_FILE, "a") as fa: fa.write(f"{user_id}\n")

@app.route('/')
def home(): return "✅ Bot is Online!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- فحص الاشتراك الإجباري ---
async def check_all_subs(user_id):
    config = get_config()
    if config["status"] == "off" or user_id == ADMIN_ID: return True, []
    not_subbed = []
    for channel in config["channels"]:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_subbed.append(channel)
        except: continue
    return (len(not_subbed) == 0), not_subbed

# --- لوحات المفاتيح ---
def admin_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📊 الإحصائيات"), KeyboardButton("📢 إذاعة (Broadcast)"))
    markup.add(KeyboardButton("⚙️ إدارة القنوات"))
    return markup

def channels_manage_keyboard():
    config = get_config()
    markup = InlineKeyboardMarkup(row_width=1)
    status_icon = "✅ مشغل" if config["status"] == "on" else "❌ معطل"
    markup.add(InlineKeyboardButton(f"نظام الاشتراك الإجباري: {status_icon}", callback_data="toggle_all_status"))
    for ch in config["channels"]:
        markup.add(InlineKeyboardButton(f"❌ حذف قناة {ch}", callback_data=f"del_ch_{ch}"))
    markup.add(InlineKeyboardButton("➕ إضافة قناة جديدة", callback_data="add_new_channel"))
    return markup

# --- رسالة الترحيب الأصلية (المميزات) ---
WELCOME_TEXT = (
    "<b>أهلاً بك في بوت تحميل ميديا تيك توك ⚡️</b>\n\n"
    "<b>المميزات المتوفرة حالياً:</b>\n"
    "• تحميل الفيديوهات بدون علامة مائية 🎬\n"
    "• تحويل الفيديو إلى ملف صوتي MP3 🎵\n"
    "• اختيار الجودة (عالية / متوسطة) 🌟\n"
    "• سرعة فائقة في المعالجة والرفع 🚀\n"
    "• دعم كامل لروابط تيك توك وكواى 📱\n\n"
    "<i>بواسطة: @i_wi_w</i>"
)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    is_sub, channels = await check_all_subs(message.from_user.id)
    
    if message.from_user.id == ADMIN_ID:
        await message.reply(f"أهلاً بك يا مطورنا! تم تفعيل لوحة التحكم.\n\n{WELCOME_TEXT}", reply_markup=admin_main_keyboard(), parse_mode='HTML')
    elif not is_sub:
        markup = InlineKeyboardMarkup(row_width=1)
        for ch in channels:
            markup.add(InlineKeyboardButton(f"📢 اشترك هنا {ch}", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(InlineKeyboardButton("✅ تم الاشتراك (تحقق)", callback_data="check_sub"))
        await message.reply("⚠️ عذراً! يجب الاشتراك في القنوات التالية أولاً لاستخدام هذه المميزات:", reply_markup=markup)
    else:
        await message.reply(WELCOME_TEXT, parse_mode='HTML')

# --- إدارة القنوات ---
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "⚙️ إدارة القنوات")
async def settings_panel(message: types.Message):
    await message.reply("⚙️ **إدارة قنوات الاشتراك:**", reply_markup=channels_manage_keyboard(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.from_user.id == ADMIN_ID and (c.data == "toggle_all_status" or c.data.startswith("del_ch_") or c.data == "add_new_channel"))
async def admin_callbacks(c: types.CallbackQuery):
    config = get_config()
    if c.data == "toggle_all_status":
        config["status"] = "off" if config["status"] == "on" else "on"
        set_config(config)
        await c.message.edit_reply_markup(reply_markup=channels_manage_keyboard())
    elif c.data.startswith("del_ch_"):
        ch = c.data.replace("del_ch_", "")
        if ch in config["channels"]: config["channels"].remove(ch); set_config(config)
        await c.message.edit_reply_markup(reply_markup=channels_manage_keyboard())
    elif c.data == "add_new_channel":
        await c.message.answer("أرسل يوزر القناة الجديد مع @ (مثال: @my_channel)")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text.startswith("@"))
async def add_channel_confirm(m: types.Message):
    config = get_config()
    if m.text not in config["channels"]:
        config["channels"].append(m.text); set_config(config)
        await m.reply(f"✅ تم إضافة {m.text} بنجاح.", reply_markup=admin_main_keyboard())

# --- الإحصائيات والإذاعة ---
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 الإحصائيات")
async def show_stats(m: types.Message):
    with open(USERS_FILE, "r") as f: count = len(f.readlines())
    await m.reply(f"📊 عدد مستخدمي البوت الحاليين: {count}")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📢 إذاعة (Broadcast)")
async def ask_br(m: types.Message): await m.reply("أرسل رسالة الإذاعة الآن:")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and not m.text.startswith("/") and not m.text.startswith("http") and not m.text.startswith("@"))
async def do_br(m: types.Message):
    if m.text in ["📊 الإحصائيات", "📢 إذاعة (Broadcast)", "⚙️ إدارة القنوات"]: return
    with open(USERS_FILE, "r") as f: users = f.read().splitlines()
    count = 0
    for u in users:
        try: await bot.send_message(u, m.text); count += 1
        except: pass
    await m.reply(f"✅ تم إرسال الإذاعة لـ {count} مستخدم.")

# --- نظام التحميل الرئيسي ---
user_data = {}
@dp.message_handler(lambda m: m.text.startswith("http"))
async def handle_download(m: types.Message):
    is_sub, _ = await check_all_subs(m.from_user.id)
    if not is_sub: await m.reply("⚠️ اشترك أولاً!"); return
    user_data[m.from_user.id] = m.text
    mk = InlineKeyboardMarkup().add(InlineKeyboardButton("🎬 فيديو", callback_data="opt_video"), InlineKeyboardButton("🎵 صوت", callback_data="opt_audio"))
    await m.reply("⚡️ اختر النوع المطلوب:", reply_markup=mk)

@dp.callback_query_handler(lambda c: c.data.startswith('opt_'))
async def opt_proc(c: types.CallbackQuery):
    url = user_data.get(c.from_user.id)
    if c.data == "opt_audio":
        await c.message.edit_text("⏳ جاري التحميل كصوت..."); await download_send(c.message, url, True)
    else:
        mk = InlineKeyboardMarkup().add(InlineKeyboardButton("🌟 عالية", callback_data="res_best"), InlineKeyboardButton("📱 متوسطة", callback_data="res_medium"))
        await c.message.edit_text("اختر الجودة:", reply_markup=mk)

@dp.callback_query_handler(lambda c: c.data.startswith('res_'))
async def res_proc(c: types.CallbackQuery):
    url = user_data.get(c.from_user.id)
    q = "best" if c.data == "res_best" else "worst"
    await c.message.edit_text("⏳ جاري التحميل..."); await download_send(c.message, url, False, q)

async def download_send(msg, url, is_audio, q="best"):
    ext = ".mp3" if is_audio else ".mp4"
    fn = f"file{ext}"
    opts = {'quiet': True, 'outtmpl': fn, 'format': 'bestaudio/best' if is_audio else f'{q}video+bestaudio/best'}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            with open(fn, 'rb') as f:
                cap = "بواسطة: @i_wi_w"
                if is_audio: await msg.answer_audio(f, caption=cap)
                else: await msg.answer_video(f, caption=cap)
            os.remove(fn); await msg.delete()
    except: await msg.answer("❌ خطأ في معالجة الرابط!")

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_btn(c: types.CallbackQuery):
    is_sub, _ = await check_all_subs(c.from_user.id)
    if is_sub: await c.message.edit_text("✅ تم التحقق! يمكنك الآن إرسال الروابط.")
    else: await c.answer("❌ لم تشترك في كل القنوات بعد!", show_alert=True)

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
