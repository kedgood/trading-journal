import streamlit as st
import gspread

st.title("My Trading Journal")

pair = st.text_input("Pair")
profit = st.number_input("Profit/Loss")

if st.button("Save"):
    st.success("Saved!")
