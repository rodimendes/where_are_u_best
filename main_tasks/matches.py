from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import mysql.connector
import pandas as pd
import pickle
import datetime as dt
import os
from glob import glob
import time


def get_source_code(url):
    """
    Gets the source code and saves it for further verifications.
    The function returns the path to 'html' file and the player name.
    """
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.get(url)
    player_name = url.split("/")[-1].split("#")[0]
    with open(f"html_player_source_code/{player_name}-{dt.date.today()}.html", "w") as file:
        file.write(driver.page_source)
    return f"html_player_source_code/{player_name}-{dt.date.today()}.html", player_name


def get_matches_info_to_dict(source_code):
    """
    Receives the source code as html file and gets 'main player', 'opponent', 'tournament', 'city', 'scores', 'result' and 'surface' from last matches, returning a dictionary.
    """
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
        tournaments = soup.find_all("div", class_="player-matches__tournament")

        main_player = []
        opponents = []
        tournaments_name = []
        cities = []
        matches_scores = []
        surfaces = []


        for tournament in tournaments:

            # Tournament Name
            tournament_name = tournament.find("h2", class_="player-matches__tournament-title").text.strip()

            # City
            city = tournament.find("span", class_="player-matches__tournament-location").text.split(",")[0]

            # Tournament Information
            matches_info = tournament.find_all("tr", class_="player-matches__match")

            # Surfaces
            raw_opps = tournament.find_all("div", class_="player-matches__match-opponent")

            for item in raw_opps:
                if item.text.strip() != "-":

                    searching_surface = tournament.find_all("div", class_="player-matches__tournament-meta-item")
                    for surface in searching_surface:
                        # surfaces = []
                        surface_type = surface.text
                        if "Surface" in surface_type:
                            # print(surface_type.split()[1])
                            surfaces.append(surface_type.split()[1])

            for match in matches_info:

                # Main player
                player_name = soup.title.string
                player_name = player_name.split("|")[0].strip()

                # Opponent
                raw_opponents_fname = match.find_all("span", class_="player-matches__match-opponent-first u-hide-tablet")
                raw_opponents_lname = match.find_all("span", class_="player-matches__match-opponent-last")
                cleaned_opponents_fname = [fname.text for fname in raw_opponents_fname]
                cleaned_opponents_lname = [lname.text for lname in raw_opponents_lname]
                opp_names_zip = zip(cleaned_opponents_fname, cleaned_opponents_lname)
                opp_separated_names = list(opp_names_zip)
                opp_names = [f"{opp[0]} {opp[1]}" for opp in opp_separated_names]

                # Score
                raw_opps = match.find_all("div", class_="player-matches__match-opponent")
                results = []
                for item in raw_opps:
                    if item.text.strip() != "-":
                        raw_scores = match.find_all("span", class_="set-score-string")
                        match_score = ""
                        for scores in raw_scores:
                            if len(match_score) == 0:
                                match_score = f"{scores.text[0]} - {scores.text[-1]}"
                            else:
                                match_score = f"{match_score} / {scores.text[0]} - {scores.text[-1]}"
                        results.append(match_score)

                # Results
                raw_results = soup.find_all("td", class_="player-matches__match-cell player-matches__match-cell--winloss")
                final_results = [result.text.strip() for result in raw_results if result.text.strip() != "-"]

                for opp_name in opp_names:
                    main_player.append(player_name)
                    opponents.append(opp_name)
                    tournaments_name.append(tournament_name)
                    cities.append(city)
                    matches_scores.append(match_score)

    # Creating a dictionary
    matches = {
        "main_player": main_player,
        "opponent": opponents,
        "tournament": tournaments_name,
        "city": cities,
        "scores": matches_scores,
        "result": final_results,
        "surface": surfaces,
    }

    return matches


def to_dataframe(player_name: str, player_matches: dict):
    """
    Receives a dictionary and player name, saving for dataframe format.
    If there is an older file for the same player, checks for duplicate data e returns only the new data.
    """
    matches_df = pd.DataFrame(player_matches, columns=[column for column in player_matches.keys()])
    old_file = glob(f"dataframes/{player_name}*")
    if len(old_file) == 0:
        with open(f"dataframes/{player_name}-{dt.date.today()}.pkl", "wb") as file:
            pickle.dump(matches_df, file)
        print("Saving full file.")
        return matches_df
    else:
        with open(old_file[0], "rb") as file:
            old_data = pickle.load(file)
        full_data = pd.concat([old_data, matches_df])
        time.sleep(1)
        cleaned_data = full_data.drop_duplicates(keep=False)
        time.sleep(1)
        with open(f"dataframes/{player_name}-{dt.date.today()}.pkl", "wb") as file:
            pickle.dump(cleaned_data, file)
        print("Dropped duplicated data and saved just new data")
        return cleaned_data


def to_database(dataframe: pd.DataFrame):
    """
    Checks the dataframe for new data and, if so, loads it into database for further analysis.
    """
    # connection = mysql.connector.connect(
    #     user = os.environ.get("AWSUSER"), # nome usuário principal
    #     password = os.environ.get("AWSPASSWORD"),
    #     host = os.environ.get("AWSHOST"), # endpoint
    #     port = 3306,
    #     database = os.environ.get("DATABASE") # nome do db
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
                player = row["main_player"]
                opp = row["opponent"]
                tournament = row["tournament"]
                city = row["city"]
                score = row['scores']
                result = row["result"]
                surface = row["surface"]
                command = f"INSERT INTO matches (main_player, opponent, tournament, city, score, result, surface) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(command, (player, opp, tournament, city, score, result, surface))
                connection.commit()
        print("Data uploaded successfully")

    return


def get_data_from_db():
    """
    Runs a query for all records in the table.
    """
    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    with connection.cursor() as cursor:
        query = "SELECT * FROM matches"
        cursor.execute(query)
        content = cursor.fetchall()

    return content
