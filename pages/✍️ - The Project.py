import streamlit as st
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

DEPARTURE_MAIL = os.environ["DEPARTURE_MAIL"]
PASS_DEPART_MAIL = os.environ["PASS_DEPART_MAIL"]
ARRIVAL_MAIL = os.environ["ARRIVAL_MAIL"]

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

st.warning("**This project is non-commercial, that is, it is not primarily intended or directed for commercial advantage or monetary compensation by an individual or organization.**")
st.markdown("---")
st.markdown("# 🏗 Under construction 🦺")
st.markdown("""### New features to implement:""")
st.markdown("- H2H, with graph based on temperature and humidity;")
st.markdown("- Prediction of results based on temperature and humidity;")

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
