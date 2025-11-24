def format_country_message(country_key: str, country: dict) -> str:
    name = country.get("name", country_key)
    rules = country.get("rules", "Информация отсутствует.")
    documents = country.get("documents", "Информация отсутствует.")
    things = country.get("things_to_take", "Информация отсутствует.")
    places = "\n".join(country.get("places", [])) or "Информация отсутствует."

    message = (
        f"🌍 <b>{name}</b>\n\n"
        f"📌 <b>Важные правила и особенности:</b>\n{rules}\n\n"
        f"📝 <b>Требуемые документы:</b>\n{documents}\n\n"
        f"🎒 <b>Список вещей, которые стоит взять:</b>\n{things}\n\n"
        f"🗺 <b>Популярные места для посещения:</b>\n{places}"
    )
    return message
