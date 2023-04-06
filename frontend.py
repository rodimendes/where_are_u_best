import streamlit as st
import pickle
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

st.title("Where are U best")

table_name = st.radio("Choose the table name below:", ("matches", "tournaments"))

# with open("matches/daily.pkl", "rb") as database:
#     matches = pickle.load(database)

new_matches = pd.read_pickle("matches/daily.pkl")

st.dataframe(new_matches, height=300)
