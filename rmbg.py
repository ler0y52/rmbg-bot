import asyncio 
import logging
import random
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# === Токены ===
TOKEN = "7833950557:AAFMS4xlHWxzqO11i_T9eTgnzaNS_5XqKKM"
TMDB_API_KEY = "52ab5ae3a04c37bb469a16db320f1011"

# === Настройки бота ===
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Главное меню ===
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рекомендовать фильм")]
    ],
    resize_keyboard=True
)

# === Меню жанров ===
genre_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Комедия"), KeyboardButton(text="Драма")],
        [KeyboardButton(text="Триллер"), KeyboardButton(text="Ужасы")],
        [KeyboardButton(text="Фантастика"), KeyboardButton(text="Экшен")]
    ],
    resize_keyboard=True
)

# === Словарь жанров TMDb ===
GENRES = {
    "Комедия": 35,
    "Драма": 18,
    "Триллер": 53,
    "Ужасы": 27,
    "Фантастика": 878,
    "Экшен": 28
}

# === Кеш для фильмов ===
seen_movies = set()

# === Обработчик команды /start ===
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я AI-кинокритик. Нажми 'Рекомендовать фильм' и выбери жанр!", reply_markup=menu)

# === Обработчик кнопки "Рекомендовать фильм" ===
@dp.message(F.text == "Рекомендовать фильм")
async def recommend_film(message: types.Message):
    await message.answer("Выбери жанр:", reply_markup=genre_menu)

# === Обработчик выбора жанра ===
@dp.message(F.text.in_(GENRES.keys()))
async def recommend_by_genre(message: types.Message):
    genre_id = GENRES[message.text]
    url = (f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ru-RU"
           f"&sort_by=popularity.desc&vote_average.gte=5&vote_count.gte=500"
           f"&with_genres={genre_id}&without_genres=16,12,10751,14"  # Исключаем анимацию, семейные, фэнтези
           f"&page=1")
    
    response = requests.get(url).json()
    
    if "results" in response and response["results"]:
        movies = [m for m in response["results"] if m["id"] not in seen_movies]
        
        if not movies:
            await message.answer("Фильмы закончились! Попробуйте другой жанр.")
            return
        
        movie = random.choice(movies)
        seen_movies.add(movie["id"])
        
        title = movie.get("title", "Без названия")
        rating = movie.get("vote_average", "Нет рейтинга")
        overview = movie.get("overview", "Описание отсутствует.")
        poster_path = movie.get("poster_path")

        # Проверяем, есть ли постер
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url = None  # Если постера нет, ставим None
        
        logging.info(f"Выбран фильм: {title}, постер: {poster_url}")

        text = f"🎬 <b>{title}</b>\n⭐ Рейтинг: {rating}/10\n📖 {overview}"

        if poster_url:
            try:
                await message.answer_photo(photo=poster_url, caption=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logging.error(f"Ошибка при отправке постера: {e}")
                await message.answer(text, parse_mode=ParseMode.HTML)
        else:
            await message.answer(text, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Не удалось найти фильм. Попробуйте другой жанр.")

# === Функция запуска бота ===
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

# === Запуск бота ===
if __name__ == "__main__":
    asyncio.run(main())
