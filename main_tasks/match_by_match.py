from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import datetime as dt
from datetime import timedelta
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import pickle
import mysql.connector
from glob import glob


load_dotenv()
api_key = os.environ.get("OPENWEATHER_KEY")


def get_source_code(url):
    """
    ?????????????????????
    Returns a tuple
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
    for pos, item in enumerate(tournaments):
        time.sleep(3)
        item.click()
        time.sleep(3)
        with open(f"../matches_source_code/{dt.date.today()}-{pos}.html", "w") as file:
            file.write(driver.page_source)

    driver.quit()

    return


def get_matches_info_to_dict(source_code):
    """
    ????????????????????????
    """
    today = dt.date.today()
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    # print(soup)
    raw_tournament_name = soup.find_all("div", class_="sidebar-item__content")
    # print("RAW TOURNAMENT")
    # print(raw_tournament_name)
    raw_surface = soup.find_all("span", class_="tournament-tag")
    # print("RAW SURFACE")
    # print(raw_surface)
    completed_matches = soup.find_all(attrs={"data-status": "COMPLETE"})
    # print("COMPLETE")
    # print(completed_matches)
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
        tournament_name.append(raw_tournament_name[1].find('h3').text.strip())
        city_splitted = raw_tournament_name[1].find('p').text.split(',')
        city.append(city_splitted[0].strip())
        country.append(city_splitted[1].strip())
        for surface in raw_surface:
            surfaces.append(surface.text.strip())

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
    current_time = dt.datetime.today().time()
    try:
        if str(current_time) < "18:00":
            yesterday = dt.date.today() - timedelta(days=-1)
            old_file = glob(f"../matches/{yesterday}-B")
            with open(old_file[0], "rb") as file:
                old_data = pickle.load(file)
            full_data = pd.concat([old_data, matches_df])
            cleaned_data = full_data.drop_duplicates(subset=['player1', 'player2', 'city', 'date'], keep=False)
            print("Dropped duplicated data")
            folder_name = "matches"
            try:
                os.mkdir(f"../{folder_name}")
            finally:
                with open(f"../matches/{dt.date.today()}-A.pkl", "wb") as file:
                    pickle.dump(matches_df, file)
            return cleaned_data
        else:
            old_file = glob(f"../matches/{dt.date.today()}-A")
            with open(old_file[0], "rb") as file:
                old_data = pickle.load(file)
            full_data = pd.concat([old_data, matches_df])
            cleaned_data = full_data.drop_duplicates(subset=['player1', 'player2', 'city', 'date'], keep=False)
            print("Dropped duplicated data")
            folder_name = "matches"
            try:
                os.mkdir(f"../{folder_name}")
            finally:
                with open(f"../matches/{dt.date.today()}-B.pkl", "wb") as file:
                    pickle.dump(matches_df, file)
            return cleaned_data
    except:
        with open(f"../matches/{dt.date.today()}-A.pkl", "wb") as file:
                pickle.dump(matches_df, file)
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


# source_code_to_test = get_source_code("https://www.wtatennis.com/scores")
# folder = "../matches_source_code/"
# for file in os.listdir(folder):
#     print(file)
source_code_to_test = "../matches_source_code/2023-03-28-1.html"
matches_dict = get_matches_info_to_dict(source_code_to_test)
print(matches_dict)
# matches_df = to_dataframe(matches_dict)
# to_database(matches_df)
