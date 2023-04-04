import requests
import pickle
import os
from dotenv import load_dotenv
import mysql.connector
import datetime as dt
import pandas as pd

load_dotenv()
api_key = os.environ.get("OPENWEATHER_KEY")


def weather_data():
    """
    It checks the city hosting a current tournament, locates its latitude and longitude, and then collects the temperature and humidity for the next seven days. Returns a dictionary with the name of the city, forecast date, temperature and humidity.
    """
    with open("tournaments_files/tournaments.pkl", 'rb') as file:
        lista = pickle.load(file)

    full_start_dt = lista.start_date + ' ' + lista.year
    full_end_dt = lista.end_date + ' ' + lista.year
    today = dt.datetime.today()
    city = []
    week_dates = []
    week_temperature = []
    week_humidity = []
    for pos, start in enumerate(full_start_dt):
        start_date = dt.datetime.strptime(start, '%b %d %Y')
        end_date = dt.datetime.strptime(full_end_dt[pos], '%b %d %Y')
        if (start_date - today).days >= 0 and (today < end_date):
            city_name = lista['city'][pos]
            print(f'Getting data from {city_name} tournament.')

            coord_params = {
            "appid": api_key,
            "q": city_name,
            "limit": 1,
            }
            # Get latitude and longitude
            coord_url = f"http://api.openweathermap.org/geo/1.0/direct"
            coord_response = requests.get(coord_url, params=coord_params)
            coord_response.raise_for_status() # returns an HTTPError object if an error has occurred during the process. It is used for debugging the requests module.
            lat = coord_response.json()[0]['lat']
            long = coord_response.json()[0]['lon']

            # Get next days temperature and humidity
            parameters = {
                    "appid": api_key,
                    "units": "metric",
                    "lat": lat,
                    "lon": long,
                    "exclude": "current,minutely,hourly,alerts"
                }

            endpoint = f"https://api.openweathermap.org/data/2.5/onecall"

            response = requests.get(endpoint, params=parameters)
            response.raise_for_status
            weather_data = response.json()
            remaining_days = (end_date - today).days
            if remaining_days < 7:
                next_days = weather_data['daily'][:remaining_days + 2]
                for day in next_days:
                    week_temperature.append(day['temp']['eve'])
                    week_humidity.append(day['humidity'])
                    week_dates.append(str(dt.date.fromtimestamp(day['dt'])))
                    city.append(city_name)
            else:
                next_days = weather_data['daily'][:7]
                for day in next_days:
                    week_temperature.append(day['temp']['eve'])
                    week_humidity.append(day['humidity'])
                    week_dates.append(str(dt.date.fromtimestamp(day['dt'])))
                    city.append(city_name)

    weather_forecast = {
        'name': city,
        "dates": week_dates,
        "temperature": week_temperature,
        "humidity": week_humidity
        }

    return weather_forecast


def to_dataframe(weather_dict: dict):
    """
    Saves the dictionary as dataframe.
    """
    weather_df = pd.DataFrame(weather_dict, columns=[column for column in weather_dict.keys()])
    try:
        last_weather_forecast = "weather_files/climate_forecast.pkl"
        with open(last_weather_forecast, "rb") as file:
            last_forecast = pickle.load(file)
        full_forecast = pd.concat([last_forecast, weather_df], ignore_index=True)
        uptodate_forecast = full_forecast.drop_duplicates(subset=['name', 'dates'], keep="first", ignore_index=True)
        cleaned_forecast = full_forecast.drop_duplicates(subset=['name', 'dates'], keep=False, ignore_index=True)
        with open("weather_files/climate_forecast.pkl", "wb") as file:
            pickle.dump(uptodate_forecast, file)
        return cleaned_forecast
    except:
        with open("weather_files/climate_forecast.pkl", 'wb') as file:
            pickle.dump(weather_df, file)
        return weather_df


def to_database(weather: pd.DataFrame):
    """
    Loads the data into database for further analysis.
    """
    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    if weather.shape[0] == 0:
        print("Database up to date. No data to load.")
    else:
        with connection.cursor() as cursor:
            for index, row in weather.iterrows():
                city = row["name"]
                date = row["dates"]
                temperature = row["temperature"]
                humidity = row["humidity"]
                command = f"INSERT INTO weather_forecast (city, date, temperature, humidity) VALUES (%s, %s, %s, %s);"
                cursor.execute(command, (city, date, temperature, humidity))
                connection.commit()
        print("Weather data uploaded successfully")
    return

weather_dict = weather_data()
weather_df = to_dataframe(weather_dict)
to_database(weather_df)
