# TODO Filtrar por jogadora. Já iniciei a ideia
# TODO Filtrar por jogadora e resultado.
# TODO Quando filtrar, aparecer sumário: n° vitórias, n° derrotas, percentual das vitórias e derrotas, percentual de vitórias por temperatura e humidade.

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd


def all_matches(matches_data):
    st.dataframe(matches_data, height=248)
    players1 = matches_data["Player 1"].unique()
    players2 = matches_data["Player 2"].unique()
    full_players_list = sorted(list(set(players1) | set(players2)))
    player_select = st.selectbox("Pick a player:", full_players_list)
    st.write(f"You choose **{player_select}**")
    st.dataframe(matches_data[(matches_data['Player 1'] == player_select) | (matches_data['Player 2'] == player_select)])

def all_tournaments(tournament_data):
    st.dataframe(tournament_data, height=248)


st.title("🎾 Where are U best 🥇")

add_sidebar = st.sidebar.radio("Select one of the options below:", ("Matches", "Tournaments"))

matches = pd.read_pickle("matches/daily.pkl")
matches.columns = ["Player 1", "Player 2", "Tournament", "City", "Country", "Winner", "Score", "Date", "Temperature", "Humidity"]
matches.index += 1
tournaments = pd.read_pickle("tournaments_files/tournaments.pkl")
tournaments.columns = ["Name", "City", "Country", "Surface", "Start", "End", "Year"]
tournaments.index += 1

st.write(f"See the first 5 rows on **{add_sidebar}** dataset.")

if add_sidebar == "Matches":
    all_matches(matches_data=matches)

if add_sidebar == "Tournaments":
    all_tournaments(tournament_data=tournaments)

###
