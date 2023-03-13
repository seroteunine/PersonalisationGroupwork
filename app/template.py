import streamlit as st
from random import random

def tile_item(column, item):
  with column:
    st.image(item['image'])
    title = item['title'].split('-')[0]
    st.subheader(title)
    st.caption(item['first_broadcast'].date())
    st.caption(item['description'])

def recommendations(df):

  # check the number of items
  nbr_items = df.shape[0]

  if nbr_items != 0:    

    # create columns with the corresponding number of items
    columns = st.columns(nbr_items)

    # convert df rows to dict lists
    items = df.to_dict(orient='records')

    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1]) for x in zip(columns, items))