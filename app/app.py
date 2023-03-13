    # Setup
import streamlit as st
import pandas as pd
import template as t
from data_import import data_import
df = data_import()

N_ITEMS = 5
N_CATEGORIES = 3

EMOJIS = {
    'Arts' : ':art:',
    'Comedy' : ':laughing:',
    'Documentary' : ':newspaper:',
    'Drama' : ':drama:',
    'Entertainment' : ':clapper:',
    'CBBC' : ':tv:',
}

    # Streamlit setup
st.set_page_config(layout="wide")
st.title('BBC Video Recommender System - University Utrecht')

    # Iterate over the categories
for category in df.category.unique()[:N_CATEGORIES]:
    # Select the data (our recommendation algorithm)
    df_subset = df[df.category == category]
    df_subset = df_subset.sort_values(by='first_broadcast', ascending=False)
    df_subset = df_subset.head(N_ITEMS)
    # Create streamlit components
    category_title = category + EMOJIS.get(category, 'NO EMOJI SET')
    st.subheader(category_title, anchor=category)
    t.recommendations(df_subset)
