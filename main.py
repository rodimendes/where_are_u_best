import requests
from bs4 import BeautifulSoup

endpoint = "https://www.flashscore.pt/jogador/haddad-maia-beatriz/lSABz6E8/"

response = requests.get(endpoint).text

soup = BeautifulSoup(response, "html.parser")

print(soup.title.string)
