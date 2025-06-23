import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

WEBHOOK_HOST = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === MAIN MENU ===
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("\ud83c\udf24 Harflar"),
    KeyboardButton("\ud83d\udcd6 서울대 한국어 1A/1B"),
    KeyboardButton("\ud83d\udcda TOPIK 1"),
    KeyboardButton("\ud83d\udc8e Premium darslar")
)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Assalomu alaykum!\nKoreys tili botiga xush kelibsiz. Menyudan tanlang:", reply_markup=main_menu)

@dp.message_handler(lambda message: message.text == "\ud83c\udf24 Harflar")
async def show_letter_menu(message: types.Message):
    from data.hangeul import hangeul_letters_data
    markup = InlineKeyboardMarkup(row_width=4)
    for harf in hangeul_letters_data.keys():
        markup.insert(InlineKeyboardButton(harf, callback_data=f"harf_{harf}"))
    markup.add(InlineKeyboardButton("\u2b05\ufe0f Orqaga", callback_data="back_to_main"))
    await message.answer("Quyidagi harflardan birini tanlang:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("harf_"))
async def show_letter_info(callback: types.CallbackQuery):
    from data.hangeul import hangeul_letters_data
    harf = callback.data.replace("harf_", "")
    matn = hangeul_letters_data.get(harf, "Ma'lumot topilmadi")
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("\u2b05\ufe0f Orqaga", callback_data="back_to_letters"))
    await callback.message.edit_text(f"\ud83c\udf24 {harf}\n{matn}", reply_markup=markup)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back_to_letters")
async def back_to_letters(callback: types.CallbackQuery):
    from data.hangeul import hangeul_letters_data
    markup = InlineKeyboardMarkup(row_width=4)
    for harf in hangeul_letters_data.keys():
        markup.insert(InlineKeyboardButton(harf, callback_data=f"harf_{harf}"))
    markup.add(InlineKeyboardButton("\u2b05\ufe0f Orqaga", callback_data="back_to_main"))
    await callback.message.edit_text("Quyidagi harflardan birini tanlang:", reply_markup=markup)
    await callback.answer()

@dp.message_handler(lambda message: message.text == "\ud83d\udcd6 서울대 한국어 1A/1B")
async def show_books(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("1A \ud83d\udcda", callback_data="book_1A"),
        InlineKeyboardButton("1B \ud83d\udcd6", callback_data="book_1B"),
        InlineKeyboardButton("\u2b05\ufe0f Orqaga", callback_data="back_to_main")
    )
    await message.answer("Sizga qaysi kitob kerak:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, "Asosiy menyu:", reply_markup=main_menu)
    await callback.answer()

# WEBHOOK
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("\u2705 Webhook o‘rnatildi: %s", WEBHOOK_URL)

async def on_shutdown(dp):
#    await bot.delete_webhook()
    logging.info("\u274c Webhook o‘chirildi")

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
