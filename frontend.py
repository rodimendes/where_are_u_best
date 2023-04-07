# TODO Filtrar por jogadora. Já iniciei a ideia
# TODO Filtrar por jogadora e resultado.
# TODO Quando filtrar, aparecer sumário: n° vitórias, n° derrotas, percentual das vitórias e derrotas, percentual de vitórias por temperatura e humidade.

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd


add_sidebar = st.sidebar.selectbox("Match Data or Tournaments Information", ("Matches", "Tournaments"), )

st.title("Where are U best")

matches = pd.read_pickle("matches/daily.pkl")
matches.columns = ["Player 1", "Player 2", "Tournament", "City", "Country", "Winner", "Score", "Date", "Temperature", "Humidity"]
tournaments = pd.read_pickle("tournaments_files/tournaments.pkl")
tournaments.columns = ["Name", "City", "Country", "Surface", "Start", "End", "Year"]

st.write(f"See the first 5 rows on **{add_sidebar}** dataset.")

if add_sidebar == "Matches":
    st.dataframe(matches, height=248)
    players1 = matches["Player 1"].unique()
    players2 = matches["Player 2"].unique()
    full_players_list = sorted(list(set(players1) | set(players2)))
    player_select = st.selectbox("Pick a player:", full_players_list)
    st.write(f"You choose **{player_select}**")
if add_sidebar == "Tournaments":
    st.dataframe(tournaments, height=248)

###
