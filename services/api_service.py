import aiohttp

class ApiService:
    BASE_COUNTRY_URL = "https://restcountries.com/v3.1/name/"

    async def fetch_country_info(self, country_name: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_COUNTRY_URL}{country_name}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
                return None

    async def search_place(self, place_name: str, country_name: str):
        # Заглушка: здесь можно добавить реальный поиск координат через API геокодера
        return {"lat": 55.751244, "lon": 37.618423}  # Пример: Москва