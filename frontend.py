import streamlit as st
import tournaments
from main_tasks import matches
import pandas as pd
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
connection = mysql.connector.connect(
        user = 'root',
        password = os.environ.get("LOCALPASSWORD"),
        host = 'localhost',
        database = os.environ.get("LOCAL_DATABASE")
    )


st.title("Where are U best")

table_name = st.radio("Choose the table name below:", ("matches", "tournaments"))

with connection.cursor() as cursor:
    cursor.execute(f"SHOW columns FROM {table_name}")
    data = cursor.fetchall()

columns = [column[0] for column in data]
table = table_name
content = pd.DataFrame(locals()[table].get_data_from_db(), columns=columns)

print(content)

st.dataframe(content)
