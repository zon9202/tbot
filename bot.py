import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F

from dotenv import load_dotenv

# 🔹 Загружаем токен из .env
load_dotenv(override=True)
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Берём токен из .env

if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env")

# 🔹 Подключаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔹 Подключаем базу данных (если нет — создаст)
try:
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0)""")
    conn.commit()
except Exception as e:
    print(f"⚠️ Ошибка подключения к базе данных: {e}")

# 🔹 Функция кнопки "Тап"
def get_tap_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔥 Тап!", callback_data="tap"))
    return keyboard

# 🔹 Команда /start
@dp.message(Command("start"))
async def start_game(message: types.Message):
    user_id = message.from_user.id

    # Добавляем игрока, если его нет
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    await message.answer("Добро пожаловать в Тап-игру! Нажимай кнопку и набирай очки!", reply_markup=get_tap_button())

# 🔹 Обработка клика (тапа)
@dp.callback_query(F.data == "tap")
async def tap_button(call: types.CallbackQuery):
    user_id = call.from_user.id

    # Увеличиваем счет игрока
    cursor.execute("UPDATE users SET score = score + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

    # Получаем обновленный счет
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()[0]

    await call.message.edit_text(f"Ты тапнул! 🎉 Очки: {score}", reply_markup=get_tap_button())
    await call.answer()

# 🔹 Функция запуска бота
async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

# 🔹 Запуск асинхронного кода
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Бот остановлен.")
