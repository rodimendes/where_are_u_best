from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import mysql.connector


create_statement = """
        INSERT INTO matches
            (player, opponent, score, W-L, date, city, surface, time, temperature, umidity, hand_player, hand_opp)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

db_config = {
    'user': 'root',
    'password': 'mcmlxxxiv',
    'host': 'localhost',
    'database': 'player_analysis_db',
}

mydb_conn = mysql.connector.connect(**db_config)


def get_source_code(url):
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.get(url)
    with open("rybakina_data.html", "w") as file:
        file.write(driver.page_source)


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
                matches_scores = []
                # print(f"Tournament {pos + 1}")
                # print(f"Match {round}")
                for scores in raw_scores:
                    splitted_score = scores.text.split("-")
                    cleaned_score = []
                    for games in splitted_score:
                        cleaned_score.append(games[0])
                    matches_scores.append(cleaned_score)
                results.append(matches_scores)
    return results


def win_loss(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    raw_results = soup.find_all("td", class_="player-matches__match-cell player-matches__match-cell--winloss")
    cleaned_results = [result.text.strip() for result in raw_results if result.text.strip() != "-"]
    return cleaned_results


def get_data():
    pass


def get_tournament_info(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
        all_tournaments = soup.find_all("a", class_="player-matches__tournament-title-link")
        tournament = [tournament.text.strip() for tournament in all_tournaments]
        return tournament


def build_database(source_code):
    cursor = mydb_conn.cursor()
    cursor.execute(create_statement, (
        get_player_name(source_code),
        get_last_opponents(source_code),
        get_score(source_code),
        win_loss(source_code),
        date,
        city,
        surface,
        time,
        temperature,
        umidity,
        hand_player,
        hand_opp
    ))
    cursor.close()
    mydb_conn.close()
