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
    with open("bia_data.html", "w") as file:
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
    raw_opponents_name = soup.find_all("a", class_="player-matches__match-opponent-link")
    cleaned_opponents_name = [opp.get("title") for opp in raw_opponents_name]
    return cleaned_opponents_name


def get_score(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
    # for table in soup.find_all("table"):
    #     return table.get("class")
    table = soup.find_all("tbody", class_="js-tournament-matches")
    print(len(table))
    # print(table.find_all("tr"))
    # return teste_jogos
    # raw_scores = soup.find_all("span", class_="set-score-string")
    # cleaned_scores = [opp.text for opp in raw_scores]
    # return cleaned_scores


def get_tournament_info(source_code):
    with open(source_code, "r") as file_to_read:
        soup = BeautifulSoup(file_to_read, 'html.parser')
        tournaments_info = soup.find_all('div', class_='player-matches__tournament')
    return tournaments_info


def build_database(source_code):
    cursor = mydb_conn.cursor()
    cursor.execute(create_statement, (
        get_player_name(source_code),
        get_last_opponents(source_code),
        score,
        W-L,
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
