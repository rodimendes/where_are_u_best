import getting_data

# # Getting source code
# url = 'https://www.wtatennis.com/players/318176/beatriz-haddad-maia#matches'
# codigoFonte = get_source_code(url)

# # Getting main tennis player
# print(get_player_name("bia_data.html"))

# # Getting opponents list
# print(getting_data.get_last_opponents("bia_data.html"))

# data = get_tournament_info("bia_data.html")
# for place in data[:3]:
#     opponent = place.find("span", class_="player-matches__match-opponent-last")
#     print(opponent.text)

getting_data.get_score("bia_data.html")
