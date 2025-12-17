class RouteService:
    def __init__(self):
        self.routes = {
            "france": ["Эйфелева башня", "Лувр", "Версаль"],
            "italy": ["Колизей", "Ватикан", "Пиза"],
            "spain": ["Саграда Фамилия", "Парк Гуэль", "Альгамбра"]
        }

    def get_places_for_country(self, country_key: str):
        return self.routes.get(country_key.lower(), [])
