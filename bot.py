import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State

# ---------------------------
# Загружаем токен из .env
# ---------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------------------------
# Локальные изображения
# ---------------------------
local_images = {
    "Россия": {
        "Красная площадь": "images/RedSquare.jpg",
        "Борщ": "images/Borsh.jpg",
        "Пельмени": "images/Pelmeni.jpg",
        "Блины": "images/Blini.jpg"
    },
    "Франция": {
        "Эйфелева башня": "images/EiffelTower.jpg",
        "Круассаны": "images/Croissant.jpg",
        "Багеты": "images/Baguette.jpg",
        "Сыр": "images/Cheese.jpg"
    },
    "Япония": {
        "Токийская башня": "images/TokyoTower.jpg",
        "Суши": "images/Sushi.jpg",
        "Рамен": "images/Ramen.jpg",
        "Тэмпура": "images/Tempura.jpg"
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
    keyboard = [[KeyboardButton(text=country)] for country in countries_info.keys()]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

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
    keyboard = [sections[i:i+3] for i in range(0, len(sections), 3)]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s) for s in row] for row in keyboard],
        resize_keyboard=True
    )

def food_carousel_keyboard(index, max_index):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"food_nav_{index-1}"))
    if index < max_index:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"food_nav_{index+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def places_carousel_keyboard(index, max_index):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"places_nav_{index-1}"))
    if index < max_index:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"places_nav_{index+1}"))
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
    country = message.text
    if country in countries_info:
        await state.update_data(country=country)
        await state.set_state(Form.section)
        await message.answer(f"Вы выбрали {country}. Выберите раздел:", reply_markup=country_sections_keyboard())
    else:
        await message.answer("Пожалуйста, выберите страну из списка.")

@dp.message(Form.section)
async def section_selected(message: Message, state: FSMContext):
    data = await state.get_data()
    country = data.get("country")
    section = message.text

    if section == "Назад":
        await state.set_state(Form.country)
        await message.answer("Выберите страну:", reply_markup=country_keyboard())
        return

    if section in countries_info[country]:
        if section == "Популярные места для посещения":
            await state.update_data(place_index=0)
            places = countries_info[country]["Популярные места для посещения"]
            first_place = places[0]
            photo_path = local_images[country][first_place]
            await message.answer_photo(
                FSInputFile(photo_path),
                caption=first_place,
                reply_markup=places_carousel_keyboard(0, len(places)-1)
            )
            return
        elif section == "Национальная кухня":
            await state.update_data(food_index=0)
            foods = countries_info[country]["Национальная кухня"]
            first_food = foods[0]
            photo_path = local_images[country][first_food]
            await message.answer_photo(
                FSInputFile(photo_path),
                caption=first_food,
                reply_markup=food_carousel_keyboard(0, len(foods)-1)
            )
            return
        else:
            await message.answer(countries_info[country][section])
    elif section == "Чек-лист для путешественника":
        checklist = ["Паспорт", "Билеты", "Страховка", "Удобная обувь", "Фотоаппарат"]
        checked = [False] * len(checklist)
        await state.update_data(checklist_items=checklist, checklist_checked=checked)
        await state.set_state(Form.checklist)
        await message.answer("Ваш чек-лист:", reply_markup=checklist_keyboard(checklist, checked))
    else:
        await message.answer("Раздел пока не реализован.")

# ---------------------------
# Карусели
# ---------------------------
@dp.callback_query(lambda c: c.data.startswith("food_nav_"))
async def food_nav(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    country = data.get("country")
    foods = countries_info[country]["Национальная кухня"]
    if 0 <= index < len(foods):
        await state.update_data(food_index=index)
        food_name = foods[index]
        photo_path = local_images[country][food_name]
        await callback.message.edit_media(
            media=types.InputMediaPhoto(media=FSInputFile(photo_path), caption=food_name),
            reply_markup=food_carousel_keyboard(index, len(foods)-1)
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("places_nav_"))
async def places_nav(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    country = data.get("country")
    places = countries_info[country]["Популярные места для посещения"]
    if 0 <= index < len(places):
        await state.update_data(place_index=index)
        place_name = places[index]
        photo_path = local_images[country][place_name]
        await callback.message.edit_media(
            media=types.InputMediaPhoto(media=FSInputFile(photo_path), caption=place_name),
            reply_markup=places_carousel_keyboard(index, len(places)-1)
        )
    await callback.answer()

# ---------------------------
# Чек-лист
# ---------------------------
@dp.callback_query(lambda c: c.data.startswith("check_"))
async def checklist_toggle(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    data = await state.get_data()
    items = data.get("checklist_items", [])
    checked = data.get("checklist_checked", [])
    if 0 <= index < len(items):
        checked[index] = not checked[index]
        await state.update_data(checklist_checked=checked)
        await callback.message.edit_reply_markup(reply_markup=checklist_keyboard(items, checked))
    await callback.answer()

# ---------------------------
# Запуск бота
# ---------------------------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

