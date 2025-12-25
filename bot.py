import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    InputMediaPhoto
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ==============================
# TOKEN
# ==============================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ TOKEN not set")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==============================
# Webhook
# ==============================
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://trevelbot-2.onrender.com{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 10000))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def img(name: str):
    return os.path.join(BASE_DIR, "images", name)

# ==============================
# Local images
# ==============================
local_images = {
    "Россия": {
        "Красная площадь": img("RedSquare.jpg"),
        "Эрмитаж": img("Эрмитаж.jpg"),
        "Байкал": img("Байкал.jpg"),
        "Борщ": img("Borsh.jpg"),
        "Пельмени": img("Pelmeni.jpg"),
        "Блины": img("Blini.jpg"),
    },
    "Франция": {
        "Эйфелева башня": img("EiffelTower.jpg"),
        "Лувр": img("Лувр.jpg"),
        "Версаль": img("Версаль.jpg"),
        "Круассаны": img("Круассаны.jpg"),
        "Багеты": img("Багеты.jpg"),
        "Сыр": img("Сыр.jpg"),
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
    },
    "Казахстан": {
        "Монумент Байтерек": img("монумент Байтерек.jpg"),
        "ТЦ «Хан-Шатыр»": img("ТЦ «Хан-Шатыр».jpg"),
        "Дворец мира": img("Дворец мира.jpg"),
        "Бешбармак": img("Бешбармак.jpg"),
        "Казы": img("Казы.jpg"),
        "Кумыс и шубат": img("Кумыс и шубат.jpeg"),
    },
    "Южная Корея": {
        "Дворец Кёнбоккун": img("Дворец Кёнбоккун.jpg"),
        "Улицы Мёндон и Хондэ": img("Улицы Мёндон и Хондэ.jpg"),
        "Остров Чеджу": img("Остров Чеджу.jpg"),
        "Бибимбап": img("Бибимбап.jpg"),
        "Ттокпокки": img("Ттокпокки.jpg"),
        "Сочжу": img("Сочжу.jpg"),
    },
    "США": {
        "Статуя Свободы": img("Статуя Свободы.jpg"),
        "Голливуд": img("Голливуд.jpg"),
        "Белый дом": img("Белый дом.jpg"),
        "Бургер": img("Бургер.jpg"),
        "Стейк": img("Стейк.jpg"),
        "Пицца": img("Пицца.jpg"),
    },
}

serbia_food_captions = {
    "cevapcici": "🍢 Ćevapčići — мясные колбаски",
    "pljeskavica": "🍔 Pljeskavica — балканский бургер",
    "burek": "🥐 Burek — слоёный пирог",
}

# ==============================
# FSM
# ==============================
class Form(StatesGroup):
    country = State()
    section = State()

# ==============================
# Keyboards
# ==============================
def country_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in local_images.keys()],
        resize_keyboard=True
    )

def section_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[ [KeyboardButton(text=s)] for s in [
            "Важные правила и особенности",
            "Требуемые документы",
            "Список вещей, которые стоит взять",
            "Популярные места для посещения",
            "Национальная кухня"
        ]] + [[KeyboardButton(text="⬅ Назад")]],
        resize_keyboard=True
    )

def nav_keyboard(index: int, max_i: int):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"nav:{index-1}"))
    if index < max_i - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"nav:{index+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# ==============================
# DATA
# ==============================
countries_info = {
    "Россия": {
        "Важные правила и особенности": "🇷🇺 Соблюдайте визовые и таможенные правила.",
        "Требуемые документы": "🛂 Паспорт, билеты, страховка.",
        "Список вещей, которые стоит взять": "🧥 Тёплая одежда, документы.",
        "Популярные места для посещения": "Красная площадь, Эрмитаж, Байкал",
        "Национальная кухня": "Борщ, Пельмени, Блины",
    },
    "Франция": {
        "Важные правила и особенности": "🇫🇷 Соблюдайте ПДД.",
        "Требуемые документы": "🛂 Паспорт.",
        "Список вещей, которые стоит взять": "📷 Камера, адаптер.",
        "Популярные места для посещения": "Эйфелева башня, Лувр, Версаль",
        "Национальная кухня": "Круассаны, Багеты, Сыр",
    },
    "Япония": {
        "Важные правила и особенности": "🇯🇵 Уважайте традиции.",
        "Требуемые документы": "🛂 Паспорт, виза.",
        "Список вещей, которые стоит взять": "👟 Удобная обувь.",
        "Популярные места для посещения": "Токийская башня, Киото, Фудзи",
        "Национальная кухня": "Суши, Рамен, Тэмпура",
    },
    "Сербия": {
        "Важные правила и особенности": "🇷🇸 Сербия безопасна и гостеприимна.",
        "Требуемые документы": "🛂 Паспорт, страховка.",
        "Список вещей, которые стоит взять": "🎒 Удобная одежда.",
        "Популярные места для посещения": "Калемегдан, Скадарлия, Златибор",
        "Национальная кухня": "cevapcici, pljeskavica, burek",
    },
    "Казахстан": {
        "Важные правила и особенности": "🇰🇿 Большая страна с разным климатом.",
        "Требуемые документы": "🛂 Загранпаспорт.",
        "Список вещей, которые стоит взять": "🧥 Одежда по сезону.",
        "Популярные места для посещения": "Байтерек, Хан-Шатыр, Дворец мира",
        "Национальная кухня": "Бешбармак, Казы, Кумыс",
    },
    "Южная Корея": {
        "Важные правила и особенности": "🇰🇷 Чистота, уважение, порядок.",
        "Требуемые документы": "🛂 Паспорт, K-ETA.",
        "Список вещей, которые стоит взять": "👟 Удобная обувь.",
        "Популярные места для посещения": "Кёнбоккун, Мёндон, Чеджу",
        "Национальная кухня": "Бибимбап, Ттокпокки, Сочжу",
    },
    "США": {
        "Важные правила и особенности": "🇺🇸 Законы отличаются по штатам.",
        "Требуемые документы": "🛂 Паспорт, виза или ESTA.",
        "Список вещей, которые стоит взять": "👟 Удобная обувь, адаптер.",
        "Популярные места для посещения": "Статуя Свободы, Голливуд, Белый дом",
        "Национальная кухня": "Бургер, Стейк, Пицца",
    },
}

text_sections = [
    "Важные правила и особенности",
    "Требуемые документы",
    "Список вещей, которые стоит взять"
]

# ==============================
# Handlers
# ==============================
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.country)
    await message.answer("🌍 Выберите страну:", reply_markup=country_keyboard())


@dp.message(Form.country)
async def choose_country(message: Message, state: FSMContext):
    if message.text not in countries_info:
        await message.answer("❌ Выберите страну кнопкой")
        return
    await state.update_data(country=message.text)
    await state.set_state(Form.section)
    await message.answer("📂 Выберите раздел:", reply_markup=section_keyboard())


@dp.message(Form.section)
async def choose_section(message: Message, state: FSMContext):
    if message.text == "⬅ Назад":
        await state.set_state(Form.country)
        await message.answer("🌍 Выберите страну:", reply_markup=country_keyboard())
        return

    data = await state.get_data()
    country = data["country"]
    section = message.text

    if section not in countries_info[country]:
        await message.answer("❌ Раздел недоступен")
        return

    # ----------------------------
    # Текстовые разделы
    # ----------------------------
    if section in text_sections:
        await message.answer(countries_info[country][section], reply_markup=section_keyboard())
        return

    # ----------------------------
    # Фото-карусель
    # ----------------------------
    items = [i.strip() for i in countries_info[country][section].split(",")]
    await state.update_data(carousel_items=items, carousel_country=country)

    index = 0
    item = items[index]
    path = local_images.get(country, {}).get(item) or img("default.png")
    caption = serbia_food_captions.get(item, f"{item} ({index+1}/{len(items)})")

    await message.answer_photo(
        photo=FSInputFile(path),
        caption=caption,
        reply_markup=nav_keyboard(index, len(items))
    )


@dp.callback_query(lambda c: c.data.startswith("nav:"))
async def carousel_callback(call: CallbackQuery, state: FSMContext):
    index = int(call.data.split(":")[1])
    data = await state.get_data()
    items = data["carousel_items"]
    country = data["carousel_country"]

    item = items[index]
    path = local_images.get(country, {}).get(item) or img("default.png")
    caption = serbia_food_captions.get(item, f"{item} ({index+1}/{len(items)})")
    media = InputMediaPhoto(media=FSInputFile(path), caption=caption)

    await call.message.edit_media(media=media, reply_markup=nav_keyboard(index, len(items)))
    await call.answer()


# ==============================
# Webhook lifecycle
# ==============================
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


# ==============================
# Run
# ==============================
def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()