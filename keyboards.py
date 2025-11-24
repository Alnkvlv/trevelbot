from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура с выбором стран
def country_keyboard():
    countries = ["Россия", "Франция", "Япония"]  # список стран на русском
    keyboard = [[KeyboardButton(text=country)] for country in countries]
    kb = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
    return kb

# Клавиатура с выбором разделов внутри страны
def country_sections_keyboard():
    sections = [
        "Важные правила и особенности",
        "Требуемые документы",
        "Список вещей, которые стоит взять",
        "Популярные места для посещения"
    ]
    keyboard = [[KeyboardButton(text=section)] for section in sections]
    kb = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
    return kb

# Пример inline-клавиатуры для мест (если нужны отдельные места)
def inline_places_keyboard(places: list):
    buttons = [InlineKeyboardButton(text=place, callback_data=place) for place in places]
    keyboard = [[button] for button in buttons]
    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return kb
