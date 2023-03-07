from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import mysql.connector
import pandas as pd
import pickle
import datetime as dt
import os


def get_source_code(url, player_name: str):
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.get(url)
    with open(f"html_player_source_code/{player_name}-{dt.date.today()}.html", "w") as file:
        file.write(driver.page_source)


def get_matches_info(source_code):
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
            tournament_name = tournament.find("a", class_="player-matches__tournament-title-link").text.strip()

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
    matches_df = pd.DataFrame(player_matches, columns=[column for column in player_matches.keys()])
    with open(f"dataframes/{player_name}-{dt.date.today()}.pkl", "wb") as file:
        pickle.dump(matches_df, file)
    return matches_df


def create_table(table_name):

    statement = 'CREATE TABLE IF NOT EXISTS {} (id int primary key auto_increment not null, main_player varchar(30), opponent varchar(30), tournament varchar(100), city varchar(50), score varchar(50), result varchar(5), surface varchar(10));'

    # connection = mysql.connector.connect(
    #     user = os.environ.get("AWSUSER"),
    #     password = os.environ.get("AWSPASSWORD"),
    #     host = os.environ.get("AWSHOST"),
    #     port = 3306,
    #     database = os.environ.get("DATABASE")
    # )

    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    cursor = connection.cursor()

    cursor.execute(statement.format(table_name))


def load_data(dataframe):

    # connection = mysql.connector.connect(
    #     user = os.environ.get("AWSUSER"),
    #     password = os.environ.get("AWSPASSWORD"),
    #     host = os.environ.get("AWSHOST"),
    #     port = 3306,
    #     database = os.environ.get("DATABASE")
    # )

    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    # Checking if the variable dataframe is, in fact, a dataframe object to load into the database
    if isinstance(dataframe, pd.DataFrame):
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

    else:
        print("Please, insert a dataframe object to load it into the database.")

    return


def get_player_name(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
        player_name = soup.title.string
        player_name = player_name.split("|")[0].strip()
    return player_name


def get_last_opponents(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_opponents_fname = soup.find_all("span", class_="player-matches__match-opponent-first u-hide-tablet")
    raw_opponents_lname = soup.find_all("span", class_="player-matches__match-opponent-last")
    cleaned_opponents_fname = [fname.text for fname in raw_opponents_fname]
    cleaned_opponents_lname = [lname.text for lname in raw_opponents_lname]
    opp_names_zip = zip(cleaned_opponents_fname, cleaned_opponents_lname)
    opp_separated_names = list(opp_names_zip)
    opp_names = [f"{opp[0]} {opp[1]}" for opp in opp_separated_names]
    return opp_names


def get_score(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    results = []
    tournaments = soup.find_all("div", class_="player-matches__tournament")
    for pos, tournament in enumerate(tournaments):
        matches = tournament.find_all("tr", class_="player-matches__match")
        for round, match in enumerate(matches):
            traco = match.find("div", class_="player-matches__match-opponent").text.strip()
            if traco != "-":
                raw_scores = match.find_all("span", class_="set-score-string")
                placar = ""
                for scores in raw_scores:
                    if len(placar) == 0:
                       placar = f"{scores.text[0]} - {scores.text[-1]}"
                    else:
                        placar = f"{placar} / {scores.text[0]} - {scores.text[-1]}"
                results.append(placar)
    return results


def win_loss(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_results = soup.find_all("td", class_="player-matches__match-cell player-matches__match-cell--winloss")
    cleaned_results = [result.text.strip() for result in raw_results if result.text.strip() != "-"]
    return cleaned_results


def get_month(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    tournaments = soup.find_all("div", class_="player-matches__tournament")
    raw_event_date = [tournament.find("span", class_="player-matches__tournament-date").text.split() for tournament in tournaments]
    month = [date[1] for date in raw_event_date]
    return month


def get_year(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    tournaments = soup.find_all("div", class_="player-matches__tournament")
    raw_event_date = [tournament.find("span", class_="player-matches__tournament-date").text.split() for tournament in tournaments]
    year = [date[-1] for date in raw_event_date]
    return year


def get_tournament_city(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_cities = soup.find_all("span", class_="player-matches__tournament-location")
    cities = [city.text.split(",")[0] for city in raw_cities]
    return cities


def get_surface(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    filtered_data = soup.find_all("div", class_="player-matches__tournament-meta-item")
    surfaces = []
    for surface in filtered_data:
        surface_type = surface.text
        if "Surface" in surface_type:
            surfaces.append(surface_type.split()[1])
    return surfaces


def get_tournament_info(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
        all_tournaments = soup.find_all("a", class_="player-matches__tournament-title-link")
        tournament = [tournament.text.strip() for tournament in all_tournaments]
        return tournament
