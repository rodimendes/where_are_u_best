import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

DEPARTURE_MAIL = os.environ["DEPARTURE_MAIL"]
PASS_DEPART_MAIL = os.environ["PASS_DEPART_MAIL"]
ARRIVAL_MAIL = os.environ["ARRIVAL_MAIL"]
DATAFRAME_HEIGHT_LARGE = 320
DATAFRAME_HEIGHT_SMALL = 100
PX_HEIGHT = 400

st.set_page_config(
    page_title="Where are U best",
    page_icon="🎾",
    layout="centered",
)

def all_matches(matches_data, data_type):
    choice = st.sidebar.radio("Filter data by:", options=["General", "Players", "Winners", "Country"], horizontal=True)
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
        st.dataframe(matches_data, height=DATAFRAME_HEIGHT_LARGE)

    if choice == "Players":
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
        # TODO Fix legend for second graph
        # TODO H2H para previsão de resultados de confrontos em outra "radio"

        winners = matches_data["Winner"].unique()
        winner_select = st.sidebar.selectbox("Pick a winner:", winners)
        wins = matches_data[matches_data["Winner"] == winner_select]
        st.dataframe(wins, height=DATAFRAME_HEIGHT_SMALL)

        all_wins_rounded = matches_data.round()
        wins_rounded = wins.round()

        fig = px.histogram(wins_rounded, x="Temperature", title="Wins and Temperature - Individual", text_auto=True, range_x=(5, 40), range_y=(0, 30), width=700, height=PX_HEIGHT)
        fig.update_layout(yaxis_title="Wins")
        fig.update_traces(xbins=dict(
            start=5,
            end=40,
            size=2
            ))
        st.plotly_chart(fig)

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=all_wins_rounded["Temperature"], nbinsx=15))
        fig2.add_trace(go.Histogram(x=wins_rounded["Temperature"], nbinsx=15))

        fig2.update_traces(
            opacity=0.75,
            xbins=dict(
                start=5,
                end=40,
                size=2),
            )
        fig2.update_layout(title_text="Wins and Temperature - Total vs. Individual player",
                           yaxis_title="Wins",
                           xaxis_title="Temperature",
                           barmode="overlay",
                           width=700,
                           height=PX_HEIGHT,
                           legend_title="Legend",
                           )
        fig2.update_xaxes(range=[5, 40])
        fig2.update_yaxes(range=[0, 30])
        st.plotly_chart(fig2)

        fig3 = px.histogram(wins_rounded, x="Humidity", title="Wins and Humidity - Individual", text_auto=True, range_x=(0, 100), range_y=(0, 30), width=700, height=PX_HEIGHT)
        fig3.update_layout(yaxis_title="Wins")
        fig3.update_traces(xbins=dict(
            start=0,
            end=100,
            size=2
            ))
        st.plotly_chart(fig3)

        fig4 = go.Figure()
        fig4.add_trace(go.Histogram(x=all_wins_rounded["Humidity"], nbinsx=15))
        fig4.add_trace(go.Histogram(x=wins_rounded["Humidity"], nbinsx=15))

        fig4.update_traces(
            opacity=0.75,
            xbins=dict(
                start=0,
                end=100,
                size=2),
            )
        fig4.update_layout(title_text="Wins and Humidity - Total vs. Individual player",
                           yaxis_title="Wins",
                           xaxis_title="Humidity",
                           barmode="overlay",
                           width=700,
                           height=PX_HEIGHT,
                           legend_title="Legend"
                           )
        fig4.update_xaxes(range=[0, 100])
        fig4.update_yaxes(range=[0, 30])
        st.plotly_chart(fig4)

    elif choice == "Country":
        countries = matches_data["Country"].unique()
        country_select = st.sidebar.selectbox("Pick a country:", countries)
        st.dataframe(matches_data[matches_data["Country"] == country_select], height=DATAFRAME_HEIGHT_LARGE)


def all_tournaments(tournament_data):
    """
    Shows all recorded tournaments and its data.
    """
    # Showing recorded tournaments
    st.dataframe(tournament_data, height=DATAFRAME_HEIGHT_LARGE)

    # World map with tournaments
    st.markdown("##### Hover over points for more information.")
    tournaments_coord = pd.read_pickle("tournaments_files/tournaments_coord.pkl")
    fig = px.scatter_mapbox(data_frame=tournaments_coord, lat="lat", lon="lon", zoom=0.5, hover_name="name", hover_data=["city", "country", "surface"], labels={"city": "City", "surface": "Surface", "country": "Country", "lat": "Latitude", "lon": "Longitude"})
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)



### Page Start ###
st.title("🎾 Where are U best")

### Adding sidebar ###
add_sidebar = st.sidebar.radio("Select one of the options below:", ("Matches", "Tournaments"), horizontal=True)

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

st.sidebar.write("---")
st.sidebar.markdown("#### 📬 Contacts")
st.sidebar.info('👨🏻‍💻 **Rodrigo Mendes** - [LinkedIn](https://www.linkedin.com/in/rodrigo-mendes-pinto/) - [Github](https://github.com/rodimendes/where_are_u_best)')

with st.sidebar.form(key="form", clear_on_submit=True):
    text = st.text_area("Feel free to give me some impressions or suggestions")
    name = st.text_input(label="Name")
    email = st.text_input(label="E-mail for response")
    submit = st.form_submit_button()
    if submit:
        st.success("Message sent successfully")
        email_message = f"Subject:Where are U best calling... 📬\n\nMessage: {text}\nName: {name}\nEmail: {email}"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(DEPARTURE_MAIL, PASS_DEPART_MAIL)
            connection.sendmail(from_addr=DEPARTURE_MAIL, to_addrs=ARRIVAL_MAIL, msg=email_message.encode('utf-8'))
