import streamlit as st
import pandas as pd
import template as t

st.set_page_config(layout="wide")

# load the dataset with the books
df_books = pd.read_csv('../data/BX-Books.csv', sep=';', encoding='latin-1')

# select a book to kickstart the interface
if 'ISBN' not in st.session_state:
  st.session_state['ISBN'] = '0385504209'

df_book = df_books[df_books['ISBN'] == st.session_state['ISBN']]

# create a cover and info column to display the selected book
cover, info = st.columns([2, 3])

with cover:
  # display the image
  st.image(df_book['Image-URL-L'].iloc[0])

with info:
  # display the book information
  st.title(df_book['Book-Title'].iloc[0])
  st.markdown(df_book['Book-Author'].iloc[0])
  st.caption(str(df_book['Year-Of-Publication'].iloc[0]) + ' | ' + df_book['Publisher'].iloc[0])

st.subheader('Recommendations based most reviewed')
df = pd.read_csv('recommendations/recommendations-most-reviewed.csv', sep=';', encoding='latin-1', dtype=object)
df = df.merge(df_books, on='ISBN')
t.recommendations(df)

st.subheader('Recommendations based on average rating')
df = pd.read_csv('recommendations/recommendations-ratings-avg.csv', sep=';', encoding='latin-1', dtype=object)
df = df.merge(df_books, on='ISBN')
t.recommendations(df)

st.subheader('Recommendations based on weighted rating')
df = pd.read_csv('recommendations/recommendations-ratings-weight.csv', sep=';', encoding='latin-1', dtype=object)
df = df.merge(df_books, on='ISBN')
t.recommendations(df)