# Windy API docs
# https://api.windy.com/point-forecast/docs

# TenDay
# https://tenday.pagasa.dost.gov.ph/docs

# Open-meteo
# https://open-meteo.com/

import requests
import os
from dotenv import load_dotenv
from web_scaper.PanahonScraper import PanahonScraper

load_dotenv()

WEATHER_API = os.getenv("WEATHER_API")
WINDY_API = os.getenv("WINDY_API")

class WeatherHandler:
    def __init__(self):
        # self.open_meteo_base = 'https://api.open-meteo.com/v1/forecast'
        self.weatherapi_base_alert =  'http://api.weatherapi.com/v1/alerts.json'
        self.weatherapi_base_forecast = 'http://api.weatherapi.com/v1/forecast.json'
        self.weatherapi_base_current_forecast = 'http://api.weatherapi.com/v1/current.json'
        self.weatherapi_base_search = 'http://api.weatherapi.com/v1/search.json'

        self.windy_api_base = "https://api.windy.com/api/point-forecast/v2"

    def get_panahon_advisory(self, location):
        panahon = PanahonScraper()
        panahon.start_scraping(location=location)
        return panahon.get_data()

    #
    #
    # def get_marine_forecast(self):
    #     pass

    """
    For weather api
    """

    def get_current_forecast(self, lat=13.147298, lng= 123.731476):
        params = {
            'key': WEATHER_API,
            'q': f"{lat},{lng}"
        }
        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
            response.raise_for_status()
            data = response.json()

            # Check if 'current' key exists
            if 'current' not in data:
                print(f"Warning: 'current' key not found in response: {data}")
                return None

            return data['current']

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
        except KeyError as e:
            print(f"Data parsing error: {e}")
            return None

    def get_coordinates_info(self, lat=13.147298, long= 123.731476):
        params = {
            'key': WEATHER_API,
            'q': f"{lat},{long}"
        }

        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
            response.raise_for_status()  # ✅ Add this to catch HTTP errors
            data = response.json()

            # Check if location exists
            if 'location' not in data:
                print(f"Warning: 'location' key not found in response")
                return None

            location = data['location']
            return {
                'name': location.get('name', 'Unknown'),
                'region': location.get('region', 'Unknown'),
                'country': location.get('country', 'Unknown'),
                'state_province': location.get('region', 'Unknown'),
                'timezone': location.get('tz_id', 'Unknown'),
                'lat': location.get('lat', lat),
                'lon': location.get('lon', long)
            }
        except Exception as e:
            print(f"Error: {e}")
            return None

