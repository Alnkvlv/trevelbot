import json
import os

class CountriesService:
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), "countries.json")

    def load(self) -> dict:
        """Загрузить все страны из JSON"""
        if not os.path.exists(self.data_file):
            return {}
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_country_info(self, country_key: str, field: str) -> str:
        """Получить конкретный раздел информации по стране"""
        data = self.load()
        return data.get(country_key, {}).get(field, "Информация отсутствует")
