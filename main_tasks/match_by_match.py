from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import datetime as dt
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import pickle
import mysql.connector
from weather import current_weather


load_dotenv()
api_key = os.environ.get("OPENWEATHER_KEY")


def get_source_code(url):
    """
    Gets the source code and saves it for further verifications.
    The function returns the path to 'html' file and the player name.
    """
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless') #### Without window
    # chrome_options.add_argument('--start-maximized') #####
    # chrome_options.add_experimental_option('detach', True) #### Keep the window opened
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    driver.find_element(By.XPATH, '//*[@id="js-cookie-notice"]/div/div/div/div/button[2]').click()
    tournaments = driver.find_elements(By.CLASS_NAME, "sidebar-item")
    for item in tournaments:
        time.sleep(3)
        item.click()
        time.sleep(3)
        with open(f"matches_source_code/{dt.date.today()}.html", "w") as file:
            file.write(driver.page_source)
    driver.quit()
    return f"matches_source_code/{dt.date.today()}.html"


def get_matches_info_to_dict(source_code):
    """
    It takes source code as html file and gets 'player1', 'player2', 'tournament', 'city', 'country', 'winner', 'score', 'date', 'temperature', 'humidity' from last completed matches, returning a dictionary.
    """
    today = dt.date.today()
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_data = soup.find("article")
    raw_tournament_data = raw_data.find_all("div", class_="tournament-wrapper") # Prints a list with all matches info per tournament
    tournament_name_list = []
    city_list = []
    country_list = []
    player1 = []
    player2 = []
    score = []
    winner = []
    temperature = []
    humidity = []
    for tournament in raw_tournament_data:
        tournament_matches = tournament.find(attrs={"data-status":"COMPLETE"})
        name = tournament["data-ui-title"]
        raw_city = tournament["data-ui-subtitle"]
        city_and_country = raw_city.split(",")
        city = city_and_country[0].strip().title()
        country = city_and_country[1].strip().title()
        players = tournament_matches.find_all("a", class_="match-table__player match-table__player--link")
        for pos, player in enumerate(players):
            if pos % 2 == 0:
                player1.append(player['aria-label'])
                tournament_name_list.append(name)
                city_list.append(city)
                country_list.append(country)
            else:
                player2.append(player['aria-label'])
        raw_score = tournament_matches.find_all("a", class_="tennis-match__match-link")
        score_data = []
        for result in raw_score:
            try:
                score_data.append(result['title'])
            except:
                score_data.append("UNKNOWN")
        for match in score_data:
            raw_winner = match.split(" d ")[0].strip()
            if "]" in raw_winner:
                winner.append(raw_winner.split("]")[1].strip())
            else:
                winner.append(raw_winner.strip())
            try:
                score.append(match.split(" ")[-1])
            except:
                score.append("UNKNOWN")

    if len(player1) != 0:
        for city in city_list:
            coord_params = {
                "appid": api_key,
                "q": city,
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
                    "exclude": "minutely, hourly, alerts, daily"
                    }

            endpoint = f"https://api.openweathermap.org/data/2.5/onecall"

            response = requests.get(endpoint, params=parameters)
            response.raise_for_status
            weather_data = response.json()
            temperature.append(weather_data['current']['feels_like'])
            humidity.append(weather_data['current']['humidity'])
    else:
        print("No one match completed so far.")

    match_dict = {
        "player1": player1,
        "player2": player2,
        "tournament": tournament_name_list,
        "city": city_list,
        "country": country_list,
        "winner": winner,
        "score": score,
        "date": today,
        "temperature": temperature,
        "humidity": humidity,
    }

    # print(match_dict)
    return match_dict


def to_dataframe(player_matches: dict):
    """
    Saves the dictionary as dataframe.
    """
    if len(player_matches["player1"]) == 0:
        matches_df = pd.DataFrame(player_matches, columns=[column for column in player_matches.keys()])
        return matches_df

    else:
        matches_df = pd.DataFrame(player_matches, columns=[column for column in player_matches.keys()])
        try:
            try:
                os.mkdir("matches")
            except:
                with open("matches/daily.pkl", "rb") as file:
                    old_data = pickle.load(file)
                reunited_data = pd.concat([old_data, matches_df], ignore_index=True)
                full_data = pd.concat([reunited_data, old_data], ignore_index=True)
                print("Dropping duplicated data")
                new_data = full_data.drop_duplicates(subset=['player1', 'player2', 'city'], keep=False, ignore_index=True)
                if new_data.shape[0] == 0:
                    print("Nothing to save")
                keep_data = full_data.drop_duplicates(subset=['player1', 'player2', 'city'], keep="first", ignore_index=True)
                with open(f"matches/daily.pkl", "wb") as file:
                    pickle.dump(keep_data, file)
            return new_data

        except:
            with open(f"matches/daily.pkl", "wb") as file:
                    pickle.dump(matches_df, file)
            print("Full dataset saved")
            return matches_df


def to_database(dataframe: pd.DataFrame):
    """
    Checks the dataframe for new data and, if so, loads it into database for further analysis.
    """
    # connection = mysql.connector.connect(
    #     user = os.environ.get("PYANY_USERNAME"), # nome usuário principal
    #     password = os.environ.get("PYANY_PWD"),
    #     host = os.environ.get("PYANY_HOST"), # endpoint
    #     port = 3306,
    #     database = os.environ.get("PYANY_DATABASE") # nome do db
    # )

    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    if dataframe.shape[0] == 0:
        print("No data to load.")
    else:
        with connection.cursor() as cursor:
            for index, row in dataframe.iterrows():
                player1 = row["player1"]
                player2 = row["player2"]
                tournament = row["tournament"]
                city = row["city"]
                country = row["country"]
                winner = row["winner"]
                score = row["score"]
                date = row["date"]
                temperature = row["temperature"]
                humidity = row["humidity"]

                command = f"INSERT INTO matches (player1, player2, tournament, city, country, winner, score, date, temperature, humidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(command, (player1, player2, tournament, city, country, winner,  score, date, temperature, humidity))
                connection.commit()
        print("Data uploaded successfully")


source_code_to_test = get_source_code("https://www.wtatennis.com/scores")
matches_dict = get_matches_info_to_dict(source_code_to_test)
matches_df = to_dataframe(matches_dict)
to_database(matches_df)
