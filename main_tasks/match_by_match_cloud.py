from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import datetime as dt
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import pickle
import mysql.connector


load_dotenv()
api_key = os.environ.get("OPENWEATHER_KEY")


def get_source_code(url):
    """
    ?????????????????????
    Returns a tuple
    """
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    try:
        os.mkdir("matches_source_code")
    finally:
        with open(f"matches_source_code/{dt.date.today()}.html", "w") as file:
            file.write(driver.page_source)
        return f"matches_source_code/{dt.date.today()}.html"


def get_matches_info_to_dict(source_code):
    """
    ????????????????????????
    """
    today = dt.date.today()
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_tournament_name = soup.find_all("div", class_="sidebar-item__content")
    raw_surface = soup.find_all("span", class_="tournament-tag")
    completed_matches = soup.find_all(attrs={"data-status": "COMPLETE"})
    scores_list = []
    winner = []
    players1 = []
    players2 = []
    temperature = []
    humidity = []
    for match in completed_matches:
        # PLAYERS
        raw_players = match.find_all("a", class_="match-table__player match-table__player--link")
        for pos, player in enumerate(raw_players):
            if pos % 2 == 0:
                players1.append(player['aria-label'])
        for pos, player in enumerate(raw_players):
            if pos % 2 == 1:
                players2.append(player['aria-label'])

    # SCORES
        raw_score = match.find_all("a", class_="tennis-match__match-link")
        scores = [score['title'] for score in raw_score]
        for score in scores:
            scores_list.append(score.split(" ")[-1])
            winner.append(score.split("d")[0].strip())

    # REPEATING ITEMS FOR THE SAME LENGTH OF MATCHES
    surfaces = []
    tournament_name = []
    city = []
    country = []
    for match in range(len(players1)):
        for surface in raw_surface:
            surfaces.append(surface.text.strip())
        for tournament in raw_tournament_name:
            tournament_name.append(tournament.find('h3').text.strip())
            city_splitted = tournament.find('p').text.split(',')
            city.append(city_splitted[0].strip())
            country.append(city_splitted[1].strip())

    if len(players1) != 0:
        city_name = city[0]
        coord_params = {
            "appid": api_key,
            "q": city_name,
            "limit": 1,
            }
            # Getting latitude and longitude
        coord_url = f"http://api.openweathermap.org/geo/1.0/direct"
        coord_response = requests.get(coord_url, params=coord_params)
        coord_response.raise_for_status() # returns an HTTPError object if an error has occurred during the process. It is used for debugging the requests module.
        lat = coord_response.json()[0]['lat']
        long = coord_response.json()[0]['lon']

        # Getting current temperature and humidity
        parameters = {
                "appid": api_key,
                "units": "metric",
                "lat": lat,
                "lon": long,
                "exclude": "minutely,hourly, alerts,daily"
                }

        endpoint = f"https://api.openweathermap.org/data/2.5/onecall"

        response = requests.get(endpoint, params=parameters)
        response.raise_for_status
        weather_data = response.json()

        for match in range(len(players1)):
            temperature.append(weather_data['current']['feels_like'])
            humidity.append(weather_data['current']['humidity'])

    match_dict = {
        "player1": players1,
        "player2": players2,
        "tournament": tournament_name,
        "city": city,
        "country": country,
        "surface": surfaces,
        "winner": winner,
        "score": scores_list,
        "date": today,
        "temperature": temperature,
        "humidity": humidity,
    }

    return match_dict


def to_dataframe(player_matches: dict):
    """
    Saves the dictionary as dataframe.
    """
    matches_df = pd.DataFrame(player_matches, columns=[column for column in player_matches.keys()])
    folder_name = "matches"
    try:
        os.mkdir(folder_name)
    finally:
        with open(f"matches/{dt.date.today()}.pkl", "wb") as file:
            pickle.dump(matches_df, file)
        return matches_df


def to_database(dataframe: pd.DataFrame):
    """
    Checks the dataframe for new data and, if so, loads it into database for further analysis.
    """

    connection = mysql.connector.connect(
        url = `${{MYSQL_URL}}`,
        user = "MYSQLUSER",
        password = "MYSQLPASSWORD",
        host = "MYSQLHOST",
        database = "MYSQLDATABASE",
        port = "MYSQLPORT"
    )

    if dataframe.shape[0] == 0:
        print("Database up to date. No data to load.")
        return
    else:
        with connection.cursor() as cursor:
            for index, row in dataframe.iterrows():
                player1 = row["player1"]
                player2 = row["player2"]
                tournament = row["tournament"]
                city = row["city"]
                country = row["country"]
                surface = row["surface"]
                winner = row["winner"]
                score = row['score']
                date = row["date"]
                temperature = row["temperature"]
                humidity = row["humidity"]

                command = f"INSERT INTO matches (player1, player2, tournament, city, country, surface, winner, score, date, temperature, humidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(command, (player1, player2, tournament, city, country, surface, winner,  score, date, temperature, humidity))
                connection.commit()
        print("Data uploaded successfully")
        return


source_code_to_test = get_source_code("https://www.wtatennis.com/scores")

# source_code_to_test = "matches_source_code/2023-03-16.html"

matches_dict = get_matches_info_to_dict(source_code_to_test)
matches_df = to_dataframe(matches_dict)
to_database(matches_df)
