# TODO Ajustar para atualizar base dos torneios

import pickle
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.environ.get("OPENWEATHER_KEY")

with open("tournaments_files/tournaments.pkl", "rb") as file:
    old_data = pickle.load(file)

tournaments_coord = old_data.drop(["surface", "start_date", "end_date", "year"], axis=1)
tournaments_coord["lat"] = 0
tournaments_coord["lon"] = 0

for pos, city in tournaments_coord.iterrows():
    coord_params = {
                "appid": api_key,
                "q": city.city,
                "limit": 1,
                }
                # Getting latitude and longitude
    coord_url = f"http://api.openweathermap.org/geo/1.0/direct"
    coord_response = requests.get(coord_url, params=coord_params)
    coord_response.raise_for_status() # returns an HTTPError object if an error has occurred during the process. It is used for debugging the requests module.
    lat = coord_response.json()[0]['lat']
    long = coord_response.json()[0]['lon']
    tournaments_coord.at[pos, "lat"] = lat
    tournaments_coord.at[pos, "lon"] = long

print(tournaments_coord)

with open(f"tournaments_files/tournaments_coord.pkl", "wb") as file:
    pickle.dump(tournaments_coord, file)

with open("tournaments_files/tournaments_coord.pkl", "rb") as file:
    coord_file = pickle.load(file)

print(coord_file)
