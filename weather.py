import requests
import pickle
import os


# TODO Get city name
# TODO Get latitude and longitude
# TODO Get next 7 days temperature and humidity

# # Indian Wells. Current weather and forecast for 8 days
lat = 33.721550
long = -116.326797
api_key = os.environ.get("OPENWEATHER_KEY")

parameters = {
        "appid": api_key,
        "units": "metric",
        "lat": lat,
        "lon": long,
        "exclude": "minutely,hourly,alerts"
    }

endpoint = f"https://api.openweathermap.org/data/2.5/onecall"

response = requests.get(endpoint, params=parameters)
response.raise_for_status
weather_data = response.json()
print(weather_data)

with open("tournaments/March.pkl", 'rb') as file:
    lista = pickle.load(file)

print(lista.city)
