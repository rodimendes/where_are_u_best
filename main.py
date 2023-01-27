import requests
from bs4 import BeautifulSoup

endpoint = "https://en.wikipedia.org/wiki/Beatriz_Haddad_Maia#Singles:_25_(17_titles,_8_runner%E2%80%93ups)"
# local_endpoint = "Beatriz Haddad Maia _ Player Stats & More – WTA Official.html"

response = requests.get(endpoint).text

soup = BeautifulSoup(response, "html.parser")

print(soup.text)
