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
    with open("tournaments/tournaments.pkl", 'rb') as file:
        lista = pickle.load(file)

    full_start_dt = lista.start_date + ' ' + lista.year
    full_end_dt = lista.end_date + ' ' + lista.year
    today = dt.datetime.today()
    for pos, start in enumerate(full_start_dt):
        start_date = dt.datetime.strptime(start, '%b %d %Y')
        end_date = dt.datetime.strptime(full_end_dt[pos], '%b %d %Y')
        if (start_date - today).days < 1:
            city_name = lista['city'][pos]
            print(f'{city_name} is coming soon...')

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

            # Get next 7 days temperature and humidity
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
            next_seven_days = weather_data['daily'][:7]
            week_temperature = [day['temp']['eve'] for day in next_seven_days]
            week_humidity = [day['humidity'] for day in next_seven_days]
            week_dates = [str(dt.date.fromtimestamp(day['dt'])) for day in next_seven_days]
            city = [city_name for _ in week_dates]

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
    with open(f"weather_files/climate_forecast.pkl", 'ab') as file:
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

# Script to enter first values
# Do not need to be executed again
"""weather = {
    "Dubai":
        {
            "Sorana Cirstea":
                {
                    "temperature": 22,
                    "humidity": 64
                }
        },
    "Doha":
        {
            "Paula Badosa":
                {
                    "temperature": 26,
                    "humidity": 65
                },
            "Daria Kasatkina":
                {
                    "temperature": 26,
                    "humidity": 65
                },
            "Jessica Pegula":
                {
                    "temperature": 23,
                    "humidity": 65
                }
        },
    "Abu Dhabi":
        {
            "Marie Bouzkova":
                {
                    "temperature": 19,
                    "humidity": 64
                },
            "Yulia Putintseva":
                {
                    "temperature": 21,
                    "humidity": 64
                },
            "Elena Rybakina":
                {
                    "temperature": 21,
                    "humidity": 64
                },
            "Belinda Bencic":
                {
                    "temperature": 22,
                    "humidity": 64
                }
        },
    "Melbourne":
        {
            "Nuria Parrizas Diaz":
                {
                    "temperature": 21,
                    "humidity": 73
                }
        },
    "Adelaide":
        {
           "Sorana Cirstea":
               {
                    "temperature": 22,
                    "humidity": 66
               },
            "Amanda Anisimova":
                {
                    "temperature": 23,
                    "humidity": 66
                },
            "Paula Badosa":
                {
                    "temperature": 23,
                    "humidity": 66
                }
        },
    "Australia":
        {
            "Martina Trevisan":
                {
                    "temperature": 26,
                    "humidity": 76
                },
            "Malene Helgø":
                {
                    "temperature": 26,
                    "humidity": 76
                }
        },
    "Guadalajara":
        {
            "Katerina Siniakova":
                {
                    "temperature": 20,
                    "humidity": 89
                }
        },
    "Ostrava":
        {
            "Karolina Muchova":
                {
                    "temperature": 12,
                    "humidity": 87
                }
        },
    "Tallinn":
        {
            "Xinyu Wang":
                {
                    "temperature": 12,
                    "humidity": 85
                },
            "Linda Noskova":
                {
                    "temperature": 11,
                    "humidity": 85
                },
            "Barbora Krejcikova":
                {
                    "temperature": 11,
                    "humidity": 85
                }
        },
    "Tokyo":
        {
            "Yuki Naito":
                {
                    "temperature": 24,
                    "humidity": 80
                },
            "Naomi Osaka":
                {
                    "temperature": 25,
                    "humidity": 80
                },
            "Veronika Kudermetova":
                {
                    "temperature": 23,
                    "humidity": 80
                }
        },
    "Portoroz":
        {
            "Clara Tauson":
                {
                    "temperature": 21,
                    "humidity": 79
                },
            "Cristina Bucsa":
                {
                    "temperature": 21,
                    "humidity": 79
                },
            "Ana Bogdan":
                {
                    "temperature": 21,
                    "humidity": 79
                }
        },
    "New York":
        {
            "Ana Konjuh":
                {
                    "temperature": 24,
                    "humidity": 77
                },
            "Bianca Andreescu":
                {
                    "temperature": 23,
                    "humidity": 79
                }
        },
    "Cincinnati":
        {
            "Jelena Ostapenko":
                {
                    "temperature": 25,
                    "humidity": 80
                }
        },
    "Toronto":
        {
            "Martina Trevisan":
                {
                    "temperature": 23,
                    "humidity": 81
                },
            "Leylah Fernandez":
                {
                    "temperature": 23,
                    "humidity": 81
                },
            "Iga Swiatek":
                {
                    "temperature": 23,
                    "humidity": 81
                },
            "Belinda Bencic":
                {
                    "temperature": 23,
                    "humidity": 81
                },
            "Karolina Pliskova":
                {
                    "temperature": 23,
                    "humidity": 81
                },
            "Simona Halep":
                {
                    "temperature": 22,
                    "humidity": 81
                },
        },
    "San Jose":
        {
            "Claire Liu":
                {
                    "temperature": 21,
                    "humidity": 79
                }
        },
    "Wimbledon":
        {
            "Kaja Juvan":
                {
                    "temperature": 19,
                    "humidity": 85
                }
        },
    "Eastbourne":
        {
            "Kaia Kanepi":
                {
                    "temperature": 16,
                    "humidity": 88
                },
            "Jodie Burrage":
                {
                    "temperature": 15,
                    "humidity": 88
                },
            "Lesia Tsurenko":
                {
                    "temperature": 16,
                    "humidity": 88
                },
            "Petra Kvitova":
                {
                    "temperature": 16,
                    "humidity": 88
                }
        },
    "Birmingham":
        {
            "Petra Kvitova":
                {
                    "temperature": 17,
                    "humidity": 90
                },
            "Magdalena Frech":
                {
                    "temperature": 18,
                    "humidity": 90
                },
            "Camila Giorgi":
                {
                    "temperature": 18,
                    "humidity": 90
                },
            "Simona Halep":
                {
                    "temperature": 13,
                    "humidity": 90
                },
            "Shuai Zhang":
                {
                    "temperature": 13,
                    "humidity": 90
                }
        },
    "Nottingham":
        {
            "Yuriko Miyazaki":
                {
                    "temperature": 14,
                    "humidity": 90
                },
            "Maria Sakkari":
                {
                    "temperature": 14,
                    "humidity": 90
                },
            "Tereza Martincova":
                {
                    "temperature": 14,
                    "humidity": 90
                },
            "Alison Riske-Amritraj":
                {
                    "temperature": 15,
                    "humidity": 90
                }
        }
}

for key, value in weather.items():
    print(len(weather))
    for player, data in weather[key].items():
        print(weather[key])
        print(player)
        print(key.upper(), player, data['temperature'], data['humidity'])


        connection = mysql.connector.connect(
                user = 'root',
                password = os.environ.get("LOCALPASSWORD"),
                host = 'localhost',
                database = os.environ.get("LOCAL_DATABASE")
            )

        with connection.cursor() as cursor:
            query = "UPDATE matches set temperature = %s, humidity = %s WHERE opponent = %s AND main_player = 'Beatriz Haddad Maia' AND city = %s;"
            cursor.execute(query, (data['temperature'], data['humidity'], player, key.upper()))
            connection.commit()
            print(f"{player} - OK")

print("Data loaded successfully.")"""
