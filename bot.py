import os
from aiohttp import web

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ======================================================
# Token
# ======================================================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ TOKEN not set")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================
# Webhook settings
# ======================================================
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://trevelbot-2.onrender.com{WEBHOOK_PATH}"
PORT = 10000

# ======================================================
# Images
# ======================================================
def img(name: str):
    return os.path.join(BASE_DIR, "images", name)

local_images = {
    "Россия": {
        "Красная площадь": img("RedSquare.jpg"),
        "Эрмитаж": img("Hermitage.jpg"),
        "Байкал": img("Baikal.jpg"),
        "Борщ": img("Borsh.jpg"),
        "Пельмени": img("Pelmeni.jpg"),
        "Блины": img("Blini.jpg"),
    },
    "Франция": {
        "Эйфелева башня": img("EiffelTower.jpg"),
        "Лувр": img("Louvre.jpg"),
        "Версаль": img("Versailles.jpg"),
        "Круассаны": img("Croissant.jpg"),
        "Багеты": img("Baguette.jpg"),
        "Сыр": img("Cheese.jpg"),
    },
    "Япония": {
        "Токийская башня": img("TokyoTower.jpg"),
        "Киото": img("Kyoto.jpg"),
        "Фудзи": img("Fuji.jpg"),
        "Суши": img("Sushi.jpg"),
        "Рамен": img("Ramen.jpg"),
        "Тэмпура": img("Tempura.jpg"),
    },
    "Сербия": {
        "cevapcici": img("Cevapcici.jpg"),
        "pljeskavica": img("Pljeskavica.jpg"),
        "burek": img("Burek.jpg"),
        "default": img("Cevapcici.jpg"),
    }
}

serbia_food_captions = {
    "cevapcici": "🍢 Ćevapčići — мясные колбаски с лепёшкой и айваром",
    "pljeskavica": "🍔 Pljeskavica — балканский бургер",
    "burek": "🥐 Burek — слоёный пирог с начинкой",
}

# ======================================================
# Data
# ======================================================
countries_info = {
    "Россия": {
        "Важные правила и особенности": "🇷🇺 Соблюдайте визовые и таможенные правила.",
        "Требуемые документы": "🛂 Паспорт, билеты, страховка.",
        "Список вещей, которые стоит взять": "🧥 Тёплая одежда, документы.",
        "Популярные места для посещения": ["Красная площадь", "Эрмитаж", "Байкал"],
        "Национальная кухня": ["Борщ", "Пельмени", "Блины"],
    },
    "Франция": {
        "Важные правила и особенности": "🇫🇷 Соблюдайте ПДД.",
        "Требуемые документы": "🛂 Паспорт.",
        "Список вещей, которые стоит взять": "📷 Камера, адаптер.",
        "Популярные места для посещения": ["Эйфелева башня", "Лувр", "Версаль"],
        "Национальная кухня": ["Круассаны", "Багеты", "Сыр"],
    },
    "Япония": {
        "Важные правила и особенности": "🇯🇵 Уважайте традиции.",
        "Требуемые документы": "🛂 Паспорт, виза.",
        "Список вещей, которые стоит взять": "👟 Удобная обувь.",
        "Популярные места для посещения": ["Токийская башня", "Киото", "Фудзи"],
        "Национальная кухня": ["Суши", "Рамен", "Тэмпура"],
    },
    "Сербия": {
        "Важные правила и особенности": "🇷🇸 Сербия безопасна и гостеприимна.",
        "Требуемые документы": "🛂 Паспорт, страховка.",
        "Список вещей, которые стоит взять": "🎒 Удобная одежда.",
        "Популярные места для посещения": [
            "Калемегданская крепость",
            "Скадарлия",
            "Златибор",
        ],
        "Национальная кухня": ["cevapcici", "pljeskavica", "burek"],
    },
}

# ======================================================
# FSM
# ======================================================
class Form(StatesGroup):
    country = State()
    section = State()
    food_index = State()
    place_index = State()

# ======================================================
# Keyboards
# ======================================================
def country_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in countries_info],
        resize_keyboard=True,
    )

def section_keyboard():
    sections = [
        "Важные правила и особенности",
        "Требуемые документы",
        "Список вещей, которые стоит взять",
        "Популярные места для посещения",
        "Национальная кухня",
        "Назад",
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s)] for s in sections],
        resize_keyboard=True,
    )

def nav_keyboard(prefix, index, max_i):
    buttons = []
    if index > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"{prefix}_{index - 1}",
            )
        )
    if index < max_i:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"{prefix}_{index + 1}",
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# ======================================================
# Handlers
# ======================================================
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.country)
    await message.answer("🌍 Выберите страну:", reply_markup=country_keyboard())

@dp.message(Form.country)
async def choose_country(message: Message, state: FSMContext):
    if message.text not in countries_info:
        return await message.answer("Выберите страну кнопкой 👇")
    await state.update_data(country=message.text)
    await state.set_state(Form.section)
    await message.answer(
        f"📌 {message.text}. Выберите раздел:",
        reply_markup=section_keyboard(),
    )

@dp.message(Form.section)
async def choose_section(message: Message, state: FSMContext):
    data = await state.get_data()
    country = data["country"]
    section = message.text

    if section == "Назад":
        await state.set_state(Form.country)
        return await message.answer("🌍 Выберите страну:", reply_markup=country_keyboard())

    if section in [
        "Важные правила и особенности",
        "Требуемые документы",
        "Список вещей, которые стоит взять",
    ]:
        return await message.answer(countries_info[country][section])

    if section == "Популярные места для посещения":
        places = countries_info[country][section]
        name = places[0]
        image = local_images.get(country, {}).get(name) or local_images["Сербия"]["default"]
        await message.answer_photo(
            FSInputFile(image),
            caption=name,
            reply_markup=nav_keyboard("place", 0, len(places) - 1),
        )

    if section == "Национальная кухня":
        foods = countries_info[country][section]
        key = foods[0]
        caption = serbia_food_captions.get(key, key)
        image = local_images[country].get(key, local_images["Сербия"]["default"])
        await message.answer_photo(
            FSInputFile(image),
            caption=caption,
            reply_markup=nav_keyboard("food", 0, len(foods) - 1),
        )

@dp.callback_query(lambda c: c.data.startswith("food_"))
async def food_nav(call: types.CallbackQuery, state: FSMContext):
    i = int(call.data.split("_")[1])
    data = await state.get_data()
    country = data["country"]
    foods = countries_info[country]["Национальная кухня"]
    key = foods[i]
    caption = serbia_food_captions.get(key, key)
    image = local_images[country].get(key, local_images["Сербия"]["default"])
    await call.message.edit_media(
        types.InputMediaPhoto(media=FSInputFile(image), caption=caption),
        reply_markup=nav_keyboard("food", i, len(foods) - 1),
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("place_"))
async def place_nav(call: types.CallbackQuery, state: FSMContext):
    i = int(call.data.split("_")[1])
    data = await state.get_data()
    country = data["country"]
    places = countries_info[country]["Популярные места для посещения"]
    name = places[i]
    image = local_images.get(country, {}).get(name) or local_images["Сербия"]["default"]
    await call.message.edit_media(
        types.InputMediaPhoto(media=FSInputFile(image), caption=name),
        reply_markup=nav_keyboard("place", i, len(places) - 1),
    )
    await call.answer()

# ======================================================
# Webhook lifecycle
# ======================================================
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

# ======================================================
# Run app
# ======================================================
def main():
    app = web.Application()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    print("🚀 Bot started with WEBHOOK")
    main()
