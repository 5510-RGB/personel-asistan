# backend/services/weather_service.py
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_weather(self, city, country_code="TR"):
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city},{country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}