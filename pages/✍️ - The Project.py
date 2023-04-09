import streamlit as st


st.set_page_config(
    page_title="The Project",
    page_icon="✍️",
    layout="centered",
)

st.markdown("# The Project")

st.markdown("**Where are U best** is a project that seeks to identify the degree of influence of the :green[temperature] and :green[humidity] on female tennis players.")
st.markdown("For this the python script gets data from the official webpage of female tennis players, that is, [Women's Tennis Association - WTA](https://www.wtatennis.com/) and gathers weather forecast data as temperature and humidity, collected by using API from [OpenWeather](https://openweathermap.org/).")
st.markdown("On this first approach we've collected the following information:")
col01, col02, col03, col04 = st.columns(4)
with col01:
    st.markdown("""
            - players,
            - score,
            - tournament,
            - city,
            - country,
            """)
with col02:
    st.markdown("""
            - winner,
            - score,
            - date,
            - temperature, and
            - humidity.""")

st.markdown("# 🏗 Under construction 🦺")
