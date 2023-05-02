from main_tasks import cities_coord, match_by_match, tournaments, weather
import datetime as dt


today = dt.datetime.today()

if today.weekday() == 6:
    try:
        tournaments_url = "https://www.wtatennis.com/tournaments"
        tournament_source_file = tournaments.get_data_source(tournaments_url)
        tournament_dict = tournaments.get_tournaments_info_to_dict(tournament_source_file)
        tournament_df = tournaments.to_dataframe(tournament_dict)
        tournaments.to_database(tournament_df)
        print("\033[92mtournaments module works well\033[0m")
    except:
        print("\033[91mtournaments not working.\033[0m")
    try:
        weather_dict = weather.weather_data()
        weather_df = weather.to_dataframe(weather_dict)
        weather.to_database(weather_df)
        print("\033[92mweather module works well\033[0m")
    except:
            print("\033[91mweather not working.\033[0m")
    try:
        cities_coord
        print("\033[92mcities_coord module works well\033[0m")
    except:
        print("\033[91mcities_coord not working.\033[0m")

try:
    source_code_to_test = match_by_match.get_source_code("https://www.wtatennis.com/scores")
    matches_dict = match_by_match.get_matches_info_to_dict(source_code_to_test)
    matches_df = match_by_match.to_dataframe(matches_dict)
    match_by_match.to_database(matches_df)
    weather.current_weather()
    print("\033[92mMatches have been updated\033[0m")
except Exception as e:
    print("\033[91mUpdate did not work properly.\033[0m")
    print(e)
