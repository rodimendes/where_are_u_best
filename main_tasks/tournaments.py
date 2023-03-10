from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import mysql.connector
import pandas as pd
import pickle
import datetime as dt
import os


def get_data_source(url):
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    driver.get(url)
    with open(f"tournaments/tournaments_list.html", "w") as file:
        file.write(driver.page_source)


def get_tournaments_info_to_dict(html_file):
    with open(html_file, 'r') as raw_file:
        soup = BeautifulSoup(raw_file, 'html.parser')
    active_tournaments = soup.find_all('div', class_='is-active-month')
    for tournament in active_tournaments:
        raw_names = tournament.find_all('h3', class_='tournament-thumbnail__title')
        names = [name.text.strip() for name in raw_names]
        raw_dates = tournament.find_all('time')
        start_date = [date.text.strip() for pos, date in enumerate(raw_dates) if pos % 2 == 0]
        end_date = [date.text.split(',')[0].strip() for pos, date in enumerate(raw_dates) if pos % 2 == 1]
        year = [date.text.split(',')[1].strip() for pos, date in enumerate(raw_dates) if pos % 2 == 1]
        raw_location = tournament.find_all('span', class_='tournament-thumbnail__location')
        cities = [city.text.split(',')[0].strip().title() for city in raw_location]
        countries = [country.text.split(',')[1].strip().title() for country in raw_location]
        raw_surface = tournament.find_all('span', class_='tournament-tag')
        surfaces = [surface.text.strip() for surface in raw_surface]

    tournaments_dict = {
        'name': names,
        'city': cities,
        'country': countries,
        'surface': surfaces,
        'start_date': start_date,
        'end_date': end_date,
        'year': year
    }

    return tournaments_dict


def to_dataframe(tournaments: dict):
    tournaments_df = pd.DataFrame(tournaments, columns=[column for column in tournaments.keys()])
    month = dt.date.today()
    with open(f"tournaments/{month:%B}.pkl", "wb") as file:
        pickle.dump(tournaments_df, file)
    return tournaments_df


def to_database(tournaments: pd.DataFrame):

    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    with connection.cursor() as cursor:
        for index, row in tournaments.iterrows():
            name = row["name"]
            city = row["city"]
            country = row["country"]
            surface = row["surface"]
            start_date = row["start_date"]
            end_date = row["end_date"]
            year = row["year"]
            command = f"INSERT INTO tournaments (name, city, country, surface, start_date, end_date, year) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(command, (name, city, country, surface, start_date, end_date, year))
            connection.commit()
    print("Data uploaded successfully")

    return


def get_data_from_db():

    connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )

    with connection.cursor() as cursor:
        query = "SELECT * FROM tournaments"
        cursor.execute(query)
        content = cursor.fetchall()

    return content
