# Setup
import streamlit as st
import pandas as pd
import user_interface as ui
import authenticate as a
from tqdm import tqdm
# Custom modules
from data_import import data_import, FILE_POLITICAL, FILE_POLARIZING

# Streamlit setup
st.set_page_config(layout="wide")

# Title
st.title('BBC Video Recommender System :tv:')
st.markdown('This is a demo of a video recommender system for the BBC  - University Utrecht.')

with st.sidebar:
  # Search bar functions
  DEBUG = st.checkbox('Debug mode', True) # Show debug messages for Development

# Import data
overwrite_text=False # always off because it takes a long time
overwrite_activity=False # could be on if you want to update the activity data but it it not optimized for that
df, df_activity, df_users, word_scores = data_import(overwrite_text=overwrite_text, overwrite_activity=overwrite_activity)
categories = df.category.unique().tolist()

# Control the offset for different categories
if 'category_offset' not in st.session_state:
  st.session_state['category_offset'] = {cat:0 for cat in categories + list(ui.CUSTOM_CATEGORIES.keys())}

# create a session state
if 'user' not in st.session_state:
  st.session_state['user'] = 0
if 'activities' not in st.session_state:
  st.session_state['activities'] = df_activity.astype(str).to_dict(orient='records')
# authenticate 
a.authenticate(df_users=df_users)

#User history recommendations (if logged in) are added to the recommendations dataframe
if st.session_state['authentication_status']:
  # select the user's activities
  df_personal = df_activity[df_activity.user_id == st.session_state['user']]
  # Likes + Views
  for cat_name, cat_activity in ui.CUSTOM_CATEGORIES.items():
    # create a new dataframe with the items that the user has liked or viewed
    df_temp = df.merge(df_personal[df_personal.activity == cat_activity], on='content_id').drop_duplicates(subset=['content_id'])
    # set the category name
    df_temp['category'] = cat_name 
    # we could use append, but this would put these categories at the bottom of the list
    categories = [cat_name] + categories 
    df = pd.concat([df_temp, df], axis=0)

# Sidebar for selecting recommendation method
with st.sidebar:
  # Search bar functions
  search_term = st.text_input("Search for shows", "")
  button_clicked = st.button("OK", key="search_button", on_click=ui.activity, args=(st.session_state['user'], 'search', search_term))
  if search_term != "":
    df = df.loc[df['text'].str.contains(search_term)]
  
  # Overwrite the N_CATEGORIES variable based on the slider input 
  N_CATEGORIES = st.slider('Number of categories:', min_value=1, max_value=len(categories), value=ui.N_CATEGORIES, step=1)
  
  # Decide which recommender method to use
  recommender_method = st.radio('Recommender system method:', ui.RECOMMENDER_METHODS)
  
  # Sort ascending or descending values
  sort_ascending = st.checkbox('Sort ascending', value=False)
  
# Main page
print(f"Rendering main page: {N_CATEGORIES * ui.N_ITEMS} total items")
for category in tqdm(categories[:N_CATEGORIES]):
    # Select the data (our recommendation algorithm)
    df_subset = df[df.category == category]
    if len(df_subset) == 0:
      continue
    # basic filtering techniques
    if recommender_method=='Views':
      df_subset = df_subset.sort_values(by='views', ascending=sort_ascending)
    elif recommender_method=='Likes':
      df_subset = df_subset.sort_values(by='likes', ascending=sort_ascending)
    elif recommender_method=='Title':
      df_subset = df_subset.sort_values(by='title', ascending=sort_ascending)
    elif recommender_method=='Date':
      df_subset = df_subset.sort_values(by='first_broadcast', ascending=sort_ascending)
    elif recommender_method=='Episode Amount':
      df_subset = df_subset.sort_values(by='episode_n', ascending=sort_ascending)
    elif recommender_method=='Random':
      df_subset = df_subset.sample(frac=1) 
    elif recommender_method=='Polarization':
      df_subset = df_subset.sort_values(by=f'{FILE_POLARIZING}_tf_idf', ascending=sort_ascending)
    elif recommender_method=='Political':
      df_subset = df_subset.sort_values(by=f'{FILE_POLITICAL}_tf_idf', ascending=sort_ascending)
      
    # actual recommendation techniques
    elif recommender_method=='Personalised':
      print(f"NOT IMPLEMENTED: {recommender_method}")
    elif recommender_method=='Collaborative filtering':
      print(f"NOT IMPLEMENTED: {recommender_method}")
    elif recommender_method=='Hybrid':
      print(f"NOT IMPLEMENTED: {recommender_method}")
          
    # Create streamlit components (category + navigation buttons)
    ui.recommendations(df=df_subset, debug=DEBUG)

if N_CATEGORIES < len(categories):
  st.subheader(f"**{len(categories)-N_CATEGORIES} more categories...**")

if len(df)==0:
  st.subheader(f"No results found")


# Print session state
# print(st.session_state['category_offset'])
# print(df_subset)