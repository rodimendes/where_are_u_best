import getting_data

# # Getting source code
# url_bia = 'https://www.wtatennis.com/players/318176/beatriz-haddad-maia#matches'
# url_rybakina = "https://www.wtatennis.com/players/324166/elena-rybakina#matches"
# codigoFonte = getting_data.get_source_code(url_rybakina)

source_code = "bia_data.html"

print("# Getting main tennis player name")
print(getting_data.get_player_name(source_code))

# print("# Getting opponents list")
# print(len(getting_data.get_last_opponents(source_code)))
# print(getting_data.get_last_opponents(source_code))

print("# Tournaments")
print(len(getting_data.get_tournament_info(source_code)))
print(getting_data.get_tournament_info(source_code))

# print("# Scores")
# print(len(getting_data.get_score(source_code)))
# print(getting_data.get_score(source_code))

# print("# Win-Loss")
# print(len(getting_data.win_loss(source_code)))
# print(getting_data.win_loss(source_code))

# print("# Getting event date")
# print(len(getting_data.get_month(source_code)))
# print(getting_data.get_month(source_code))
# print(len(getting_data.get_year(source_code)))
# print(getting_data.get_year(source_code))

print("# Getting location")
print(len(getting_data.get_tournament_city(source_code)))
print(getting_data.get_tournament_city(source_code))

print("# Getting surface")
print(len(getting_data.get_surface(source_code)))
print(getting_data.get_surface(source_code))
