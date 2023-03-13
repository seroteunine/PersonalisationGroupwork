import streamlit as st
import pandas as pd
import template as t

st.set_page_config(layout="wide")

# load the dataset with the books
df_comedy = pd.read_pickle('../data/arts.pkl')
df_subset = df_comedy[0:5]

st.subheader('Subset df_comedy')
t.recommendations(df_subset)
