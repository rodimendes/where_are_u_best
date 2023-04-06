import streamlit as st
import pickle


st.title("Where are U best")

table_name = st.radio("Choose the table name below:", ("matches", "tournaments"))

with open("matches/daily.pkl", "rb") as database:
    matches = pickle.load(database)

st.dataframe(matches, height=300)
