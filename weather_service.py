from abc import ABC, abstractmethod
import requests

API_KEY = "a33cc9d38f4eef11bdc16ecd15a9b897"

class WeatherService(ABC):
    API_URL = "https://api.openweathermap.org/data/2.5/forecast"

    @abstractmethod
    def get_weather_data(self, city):
        pass

class OpenWeatherService(WeatherService):
    def get_weather_data(self, city):
        if not city or not city.strip():
            return {"error": "City name cannot be empty."}, 400  # Returning HTTP 400 for bad request

        try:
            params = {"q": city, "appid": API_KEY, "units": "metric"}
            response = requests.get(self.API_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # ✅ Handle invalid city names
            if "city" not in data or "list" not in data:
                return {"error": "Invalid city name. Please enter a valid city."}, 400

            return data

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                return {"error": "Invalid city name. Please enter a valid city."}, 400
            return {"error": f"HTTP error occurred: {http_err}"}, response.status_code

        except requests.exceptions.ConnectionError:
            return {"error": "Network error occurred. Please check your connection."}, 503

        except requests.exceptions.Timeout:
            return {"error": "The request timed out. Try again later."}, 504

        except requests.exceptions.RequestException as req_err:
            return {"error": f"An unexpected error occurred: {req_err}"}, 500


