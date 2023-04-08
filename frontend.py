# TODO Filtrar por jogadora e resultado.
# TODO Quando filtrar, aparecer sumário: n° vitórias, n° derrotas, percentual das vitórias e derrotas, percentual de vitórias por temperatura e humidade.

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd


st.set_page_config(
    page_title="Where are U best",
    page_icon="🎾",
    layout="centered",
)

def all_matches(matches_data):
    st.dataframe(matches_data[:5], height=212)
    choice = st.radio("Filter data by:", options=["Players", "Tournament", "Country", "Winner"], horizontal=True)
    if choice == "Players":
        players1 = matches_data["Player 1"].unique()
        players2 = matches_data["Player 2"].unique()
        full_players_list = sorted(list(set(players1) | set(players2)))
        player_select = st.selectbox("Pick a player:", full_players_list)
        st.write(f"You choose **{player_select}**")
        player_df = matches_data[(matches_data['Player 1'] == player_select) | (matches_data['Player 2'] == player_select)]
        st.dataframe(player_df)

        # Wins and defeats
        wins = 0
        defeat = 0
        for winner in player_df["Winner"]:
            if player_select[-4:] in winner:
                wins += 1
            else:
                defeat += 1

        # Temperature
        mean_temp = (player_df["Temperature"]).mean()
        std_dev_temp = pd.DataFrame(player_df["Temperature"]).std()

        #Humidity
        mean_humidity = (player_df["Humidity"]).mean()
        std_dev_hum = pd.DataFrame(player_df["Humidity"]).std()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(label="Recorded matches", value=player_df.shape[0])
        col2.metric(label="Wins", value=wins, delta=f"{(wins/player_df.shape[0])*100:.1f}%")
        col3.metric(label="Defeats", value=defeat, delta=f"{(defeat/player_df.shape[0])*100:.1f}%")
        col4.metric(label="Mean temperature", value=f"{mean_temp:.2f}", delta=f"{std_dev_temp.max():.2f}", help="The green value represents the standard deviation for collected values so far.")
        col5.metric(label="Mean humidity", value=f"{mean_humidity:.2f}", delta=f"{std_dev_hum.max():.2f}", help="The green value represents the standard deviation for collected values so far.")
        st.write("---")
        desired_temp = st.slider(label='Temperature', min_value=5, max_value=50, value=(10, 20))
        my_choice_temp = (player_df[(player_df['Temperature'] >= desired_temp[0]) & (player_df['Temperature'] <= desired_temp[1])])
        st.write(my_choice_temp)
    elif choice == "Tournament":
        tournaments = matches_data["Tournament"].unique()
        tournament_select = st.selectbox("Pick a tournament:", tournaments)
        st.dataframe(matches_data[matches_data["Tournament"] == tournament_select])
    elif choice == "Country":
        countries = matches_data["Country"].unique()
        country_select = st.selectbox("Pick a country:", countries)
        st.dataframe(matches_data[matches_data["Country"] == country_select])
    elif choice == "Winner":
        winners = matches_data["Winner"].unique()
        winner_select = st.selectbox("Pick a winner:", winners)
        st.dataframe(matches_data[matches_data["Winner"] == winner_select])

def all_tournaments(tournament_data):
    st.dataframe(tournament_data[:5], height=212)


### Page Start ###
st.title("🎾 Where are U best 🥇")

### Adding sidebar ###
add_sidebar = st.sidebar.radio("Select one of the options below:", ("Matches", "Tournaments"))

### Loading and configuring data from pickle files ###
matches = pd.read_pickle("matches/daily.pkl")
matches.columns = ["Player 1", "Player 2", "Tournament", "City", "Country", "Winner", "Score", "Date", "Temperature", "Humidity"]
matches.index += 1
tournaments = pd.read_pickle("tournaments_files/tournaments.pkl")
tournaments.columns = ["Name", "City", "Country", "Surface", "Start", "End", "Year"]
tournaments.index += 1

st.write(f"See the first 5 rows on **{add_sidebar}** dataset.")

### Showing data according to selection ###
if add_sidebar == "Matches":
    all_matches(matches_data=matches)


if add_sidebar == "Tournaments":
    all_tournaments(tournament_data=tournaments)
