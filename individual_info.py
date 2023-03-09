from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import datetime as dt

def get_source_code(url):
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.get(url)
    with open(f"tournaments/tournaments_list.html", "w") as file:
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
