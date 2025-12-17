import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State


# ---------------------------
# Dummy HTTP сервер для Render Free Plan
# ---------------------------
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server = HTTPServer(("0.0.0.0", 10000), DummyHandler)
    server.serve_forever()

# Запуск HTTP сервера в отдельном потоке
threading.Thread(target=run_dummy_server, daemon=True).start()

# ---------------------------
# Токен из переменной окружения
# ---------------------------
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ Переменная окружения TOKEN не задана")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------------------------
# Базовая директория проекта
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------
# Локальные изображения
# ---------------------------
local_images = {
    "Россия": {
        "Красная площадь": os.path.join(BASE_DIR, "images", "RedSquare.jpg"),
        "Борщ": os.path.join(BASE_DIR, "images", "Borsh.jpg"),
        "Пельмени": os.path.join(BASE_DIR, "images", "Pelmeni.jpg"),
        "Блины": os.path.join(BASE_DIR, "images", "Blini.jpg")
    },
    "Франция": {
        "Эйфелева башня": os.path.join(BASE_DIR, "images", "EiffelTower.jpg"),
        "Круассаны": os.path.join(BASE_DIR, "images", "Croissant.jpg"),
        "Багеты": os.path.join(BASE_DIR, "images", "Baguette.jpg"),
        "Сыр": os.path.join(BASE_DIR, "images", "Cheese.jpg")
    },
    "Япония": {
        "Токийская башня": os.path.join(BASE_DIR, "images", "TokyoTower.jpg"),
        "Суши": os.path.join(BASE_DIR, "images", "Sushi.jpg"),
        "Рамен": os.path.join(BASE_DIR, "images", "Ramen.jpg"),
        "Тэмпура": os.path.join(BASE_DIR, "images", "Tempura.jpg")
    }
}

# ---------------------------
# Данные по странам
# ---------------------------
countries_info = {
    "Россия": {
        "Важные правила и особенности": "Не забывайте о визе и правилах таможни.",
        "Требуемые документы": "Паспорт, страховка, билеты.",
        "Список вещей, которые стоит взять": "Тёплая одежда, удобная обувь, документы.",
        "Популярные места для посещения": ["Красная площадь", "Эрмитаж", "Байкал"],
        "Национальная кухня": ["Борщ", "Пельмени", "Блины"]
    },
    "Франция": {
        "Важные правила и особенности": "Соблюдайте местные правила дорожного движения.",
        "Требуемые документы": "Паспорт, страховка, билеты.",
        "Список вещей, которые стоит взять": "Лёгкая одежда, адаптер для розеток, фотоаппарат.",
        "Популярные места для посещения": ["Эйфелева башня", "Лувр", "Версаль"],
        "Национальная кухня": ["Круассаны", "Багеты", "Сыр"]
    },
    "Япония": {
        "Важные правила и особенности": "Уважайте местные традиции и правила.",
        "Требуемые документы": "Паспорт, виза, страховка.",
        "Список вещей, которые стоит взять": "Удобная обувь, зонтик, карта города.",
        "Популярные места для посещения": ["Токийская башня", "Киото", "Фудзи"],
        "Национальная кухня": ["Суши", "Рамен", "Тэмпура"]
    },
    "Сербия": {
        "Важные правила и особенности": (
        "Язык официальный — сербский (кириллица и латиница). "
        "В туристических местах часто говорят по‑английски. Небольшой набор фраз на сербском поможет.\n"
        "Валюта сербский динар (RSD). Кредитные карты принимают в городах, но в маленьких поселениях и на рынках чаще берут только наличные.\n"
        "Религия православие широко представлено — уважайте монастыри и церкви: закрытая одежда, обувь тихая, при входе держать руки и не шуметь.\n"
        "В целом безопасно, но в туристических зонах возможны карманные кражи — следите за вещами.\n"
        "Спрашивайте разрешение перед фотографированием людей; не фотографируйте объекты с охраной/военные инсталляции.\n"
        "Курение в закрытых общественных местах часто запрещено/ограничено — смотрите предупреждения.\n"
        "Алкоголь: молодежные развлечения развиты (особенно в Белграде), но публичное опьянение/провокации не приветствуются.\n"
        "Что нельзя: наркотики — строгие наказания; провоз некоторых товаров через границу ограничен (алкоголь, табак свыше норм, крупные суммы наличных — декларируйте).\n"
        "Движение правостороннее. При остановке полицией вежливо сотрудничать; права международные не обязательны для EU, но рекомендуется иметь IDP.\n"
        "Интересные факты: столетние монастыри, традиционная кухня с сильным влиянием Балкан/Османской/Центральной Европы. Белград — оживлённый культурный и ночной центр."
    ),
        "Требуемые документы": (
        "Паспорт: действительный по крайней мере на период поездки; рекомендуют иметь запас минимум 3 месяца до окончания срока действия (проверяйте требования вашей страны).\n"
        "Виза: для граждан многих стран (ЕС, США, Канада, UK и др.) разрешено безвизовое пребывание (обычно до 30–90 дней). Обязательно проверить актуальные визовые правила по гражданству на сайте посольства/консульства.\n"
        "Билеты туда/обратно или подтверждение дальнейшей поездки (иногда спрашивают на границе).\n"
        "Подтверждение брони жилья (иногда требуют при въезде).\n"
        "Медицинская страховка туристическая (рекомендуется покрытие репатриации и госпитализации).\n"
        "Водительские права: национальные права обычно действуют; для спокойствия возьмите международное водительское удостоверение (IDP).\n"
        "При транзите/особых обстоятельствах: прививочный сертификат (возможно требование по эпидемиологической ситуации — уточняйте перед поездкой).\n"
        "Копии документов: сохраняйте сканы паспорта/виз/страховки в облаке и бумажные копии отдельно от оригинала."
    ),
    "Список вещей, которые стоит взять":(
        "Теплая и многослойная одежда (особенно если поездка вне лета) — в горах быстро меняется погода.\n"
        "Удобная обувь для прогулок и возможных каменистых троп (если планируете национальные парки).\n" 
        "Лёгкая куртка/ветровка и дождевик.\n"
        "Зарядные устройства, power bank и переходник для розеток (тип F, 230V; адаптеры типа C/F работают).\n"
        "Маленькая аптечка: индивидуальные лекарства, обезболивающие, пластыри, средство от укачивания, антигистаминные.\n"
        "Документы и копии (паспорт, страховка, билеты, бронь отеля).\n"
        "Наличные в динарах и банковские карты (сообщите банку о поездке).\n"
        "Солнцезащитные очки и солнцезащитный крем (летом).\n"
        "Рюкзак на день, емкость для воды.\n"
        "Универсальный замок для багажа и небольшая сумка на ремне для ценных вещей.\n"
        "При планах на горы/зиму — специализированная одежда (горные ботинки, термобелье).\n"
        "Фотокамера/смартфон с картами офлайн (или карта)."
    ),
    "Популярные места для посещения": ["Белград", "Нови-Сад", "Ниш"],
    "Национальная кухня": ["Ćevapi", "Sarma", "Pljeskavica"]
    }
}

# ---------------------------
# FSM
# ---------------------------
class Form(StatesGroup):
    country = State()
    section = State()
    food_index = State()
    place_index = State()
    checklist = State()

# ---------------------------
# Клавиатуры
# ---------------------------
def country_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=country)] for country in countries_info],
        resize_keyboard=True
    )

def country_sections_keyboard():
    sections = [
        "Важные правила и особенности",
        "Требуемые документы",
        "Список вещей, которые стоит взять",
        "Популярные места для посещения",
        "Национальная кухня",
        "Чек-лист для путешественника",
        "Назад"
    ]
    keyboard = [sections[i:i + 3] for i in range(0, len(sections), 3)]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s) for s in row] for row in keyboard],
        resize_keyboard=True
    )

def food_carousel_keyboard(index, max_index):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"food_nav_{index - 1}"))
    if index < max_index:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"food_nav_{index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def places_carousel_keyboard(index, max_index):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"places_nav_{index - 1}"))
    if index < max_index:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"places_nav_{index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def checklist_keyboard(items, checked):
    buttons = []
    for i, item in enumerate(items):
        text = f"✅ {item}" if checked[i] else item
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"check_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ---------------------------
# Хендлеры
# ---------------------------
@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.country)
    await message.answer("Выберите страну:", reply_markup=country_keyboard())

@dp.message(Form.country)
async def country_selected(message: Message, state: FSMContext):
    if message.text in countries_info:
        await state.update_data(country=message.text)
        await state.set_state(Form.section)
        await message.answer(
            f"Вы выбрали {message.text}. Выберите раздел:",
            reply_markup=country_sections_keyboard()
        )
    else:
        await message.answer("Пожалуйста, выберите страну из списка.")

@dp.message(Form.section)
async def section_selected(message: Message, state: FSMContext):
    data = await state.get_data()
    country = data["country"]
    section = message.text

    if section == "Назад":
        await state.set_state(Form.country)
        await message.answer("Выберите страну:", reply_markup=country_keyboard())
        return

    if section == "Популярные места для посещения":
        places = countries_info[country][section]
        await state.update_data(place_index=0)
        name = places[0]
        await message.answer_photo(
            FSInputFile(local_images[country][name]),
            caption=name,
            reply_markup=places_carousel_keyboard(0, len(places) - 1)
        )
        return

    if section == "Национальная кухня":
        foods = countries_info[country][section]
        await state.update_data(food_index=0)
        name = foods[0]
        await message.answer_photo(
            FSInputFile(local_images[country][name]),
            caption=name,
            reply_markup=food_carousel_keyboard(0, len(foods) - 1)
        )
        return

    if section == "Чек-лист для путешественника":
        checklist = ["Паспорт", "Билеты", "Страховка", "Удобная обувь", "Фотоаппарат"]
        checked = [False] * len(checklist)
        await state.update_data(checklist_items=checklist, checklist_checked=checked)
        await message.answer("Ваш чек-лист:", reply_markup=checklist_keyboard(checklist, checked))
        return

    await message.answer(countries_info[country].get(section, "Раздел не найден"))

# ---------------------------
# Карусели
# ---------------------------
@dp.callback_query(lambda c: c.data.startswith("food_nav_"))
async def food_nav(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    country = data["country"]
    foods = countries_info[country]["Национальная кухня"]
    name = foods[index]
    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=FSInputFile(local_images[country][name]),
            caption=name
        ),
        reply_markup=food_carousel_keyboard(index, len(foods) - 1)
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("places_nav_"))
async def places_nav(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    country = data["country"]
    places = countries_info[country]["Популярные места для посещения"]
    name = places[index]
    await callback.message.edit_media(
        media=types.InputMediaPhoto(
            media=FSInputFile(local_images[country][name]),
            caption=name
        ),
        reply_markup=places_carousel_keyboard(index, len(places) - 1)
    )
    await callback.answer()

# ---------------------------
# Чек-лист
# ---------------------------
@dp.callback_query(lambda c: c.data.startswith("check_"))
async def checklist_toggle(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    items = data["checklist_items"]
    checked = data["checklist_checked"]
    checked[index] = not checked[index]
    await state.update_data(checklist_checked=checked)
    await callback.message.edit_reply_markup(
        reply_markup=checklist_keyboard(items, checked)
    )
    await callback.answer()

# ---------------------------
# Запуск
# ---------------------------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))