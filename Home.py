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


def all_matches(matches_data, data_type):
    choice = st.sidebar.radio("Filter data by:", options=["General", "Players", "Winners", "Tournament", "Country"], horizontal=True)
    players1 = matches_data["Player 1"].unique()
    players2 = matches_data["Player 2"].unique()
    full_players_list = sorted(list(set(players1) | set(players2)))

    if choice == "General":
        st.write(f"See the whole **{data_type}** dataset.")
        col01, col02, col03, col04, col05 = st.columns(5)
        col01.metric(label="Saved matches", value=len(matches_data))
        col02.metric(label="Total players", value=len(full_players_list))
        col03.metric(label="Total tournaments", value=len(matches_data["Tournament"].unique()))
        col04.metric(label="Total cities", value=len(matches_data["City"].unique()))
        col05.metric(label="Total countries", value=len(matches_data["Country"].unique()))
        st.dataframe(matches_data, height=320)

    if choice == "Players":
        # TODO Insert graph that represents the results and applied filters
        # TODO Graficos com vitorias e derrotas relacionadas com temperatura e humidade, em imagens separadas

        player_select = st.sidebar.selectbox("Pick a player:", full_players_list)
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
        col1.metric(label="Matches", value=player_df.shape[0])
        col2.metric(label="Wins", value=wins, delta=f"{(wins/player_df.shape[0])*100:.1f}%")
        col3.metric(label="Defeats", value=defeat, delta=f"{(defeat/player_df.shape[0])*100:.1f}%")
        col4.metric(label="Mean temperature", value=f"{mean_temp:.2f}", delta=f"{std_dev_temp.max():.2f}", help="The green value represents the standard deviation for collected values so far.")
        col5.metric(label="Mean humidity", value=f"{mean_humidity:.2f}", delta=f"{std_dev_hum.max():.2f}", help="The green value represents the standard deviation for collected values so far.")

        i_will_try = st.sidebar.checkbox("Do you want to try?")
        if i_will_try:
            desired_temp = st.sidebar.slider(label='Temperature', min_value=5, max_value=50, value=(10, 40))
            desired_humid = st.sidebar.slider(label='Humidity', min_value=0, max_value=100, value=(50, 70))
            my_choice_temp = (player_df[(player_df['Temperature'] >= desired_temp[0]) & (player_df['Temperature'] <= desired_temp[1])])
            my_choice_hum = (my_choice_temp[(my_choice_temp['Humidity'] >= desired_humid[0]) & (my_choice_temp['Humidity'] <= desired_humid[1])])
            st.dataframe(my_choice_hum)

    elif choice == "Winners":
        # TODO Applies temperature and humidity filter to try the best players given the weather condition
        # TODO H2H para previsão de resultados de confrontos

        winners = matches_data["Winner"].unique()
        winner_select = st.sidebar.selectbox("Pick a winner:", winners)
        wins = matches_data[matches_data["Winner"] == winner_select]
        st.dataframe(wins, height=110)
        all_wins_rounded_temp = matches_data.round()
        wins_rounded_temp = wins.round()
        fig = px.histogram(wins_rounded_temp, x="Temperature", title="Wins and temperature", text_auto=True, range_x=(5, 40), range_y=(0, 30), width=700, height=400)
        fig.update_layout(yaxis_title="Wins")
        fig.update_traces(xbins=dict(
            start=5,
            end=40,
            size=2
            ))
        st.plotly_chart(fig)

        # fig2 = go.Figure()
        # fig2.add_trace(go.Histogram(x=all_wins_rounded_temp["Temperature"], nbinsx=15))
        # fig2.add_trace(go.Histogram(x=wins_rounded_temp["Temperature"], nbinsx=15))

        # fig2.update_traces(opacity=0.75)
        # fig2.update_layout(yaxis_title="Wins", xaxis_title="Temperature", barmode="overlay")
        # st.plotly_chart(fig2)

    elif choice == "Tournament":
        # TODO Insert map with tournaments around the world as a point

        tournaments = matches_data["Tournament"].unique()
        tournament_select = st.sidebar.selectbox("Pick a tournament:", tournaments)
        st.dataframe(matches_data[matches_data["Tournament"] == tournament_select], height=320)

    elif choice == "Country":
        # TODO Insert map with countries

        countries = matches_data["Country"].unique()
        country_select = st.sidebar.selectbox("Pick a country:", countries)
        st.dataframe(matches_data[matches_data["Country"] == country_select], height=320)


def all_tournaments(tournament_data):
    st.dataframe(tournament_data, height=320)


### Page Start ###
st.title("🎾 Where are U best")

### Adding sidebar ###
add_sidebar = st.sidebar.radio("Select one of the options below:", ("Matches", "Tournaments"))

### Loading and configuring data from pickle files ###
matches = pd.read_pickle("matches/daily.pkl")
matches.columns = ["Player 1", "Player 2", "Tournament", "City", "Country", "Winner", "Score", "Date", "Temperature", "Humidity"]
matches.index += 1
tournaments = pd.read_pickle("tournaments_files/tournaments.pkl")
tournaments.columns = ["Name", "City", "Country", "Surface", "Start", "End", "Year"]
tournaments.index += 1

### Showing data according to selection ###
if add_sidebar == "Matches":
    all_matches(matches_data=matches, data_type=add_sidebar)


if add_sidebar == "Tournaments":
    all_tournaments(tournament_data=tournaments)
