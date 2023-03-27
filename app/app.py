# Setup
import streamlit as st
import pandas as pd
import template as t
import authenticate as a

from data_import import data_import

# Streamlit setup
st.set_page_config(layout="wide")
st.title('BBC Video Recommender System - University Utrecht')
st.markdown('This is a demo of a video recommender system for the BBC.')

# Import data and create content_id
@st.cache_data
def static_df_import():
  return data_import()
  
df = static_df_import()

#st.title('Video Library :tv:')
categories = df.category.unique().tolist()
# Control the offset for different categories
if 'category_offset' not in st.session_state:
  st.session_state['category_offset'] = {cat:0 for cat in categories + list(t.CUSTOM_CATEGORIES.keys())}

# Load activities
df_activity = pd.read_json('activities_generated.json')

#Load users statically
@st.cache_data
def load_users():
  return pd.read_json('users_generated.json')

df_users = load_users()

# create a session state
if 'user' not in st.session_state:
  st.session_state['user'] = 0
if 'activities' not in st.session_state:
  st.session_state['activities'] = df_activity.astype(str).to_dict(orient='records')
# authenticate 
a.authenticate()

#User history recommendations (if logged in)
if st.session_state['authentication_status']:
  df_personal = df_activity[df_activity.user_id == st.session_state['user']]
  # Likes + Views
  for cat_name, cat_activity in t.CUSTOM_CATEGORIES.items():
    df_temp = df.merge(df_personal[df_personal.activity == cat_activity], on='content_id').drop_duplicates(subset=['content_id'])
    df_temp['category'] = cat_name
    categories = [cat_name] + categories #no append because of order
    df = pd.concat([df_temp, df], axis=0)

# Video categories
# Sidebar for selecting recommendation method
with st.sidebar:
  N_CATEGORIES = st.slider('Number of categories', min_value=1, max_value=len(categories), value=t.N_CATEGORIES, step=1)
  st.text('Select recommendation method:')
  recommender_method = st.radio('Recommender system method', t.RECOMMENDER_METHODS)
  sort_ascending = st.checkbox('Sort ascending', value=False)

#st.markdown("<h1 style='text-align:center'>Video Library<h1>", unsafe_allow_html=True)   
# Iterate over the categories
for category in categories[:N_CATEGORIES]:
  
    # Select the data (our recommendation algorithm)
    df_subset = df[df.category == category]
    
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
      
    # actual recommendation techniques
    elif recommender_method=='Personalised':
      print(f"NOT IMPLEMENTED: {recommender_method}")
    elif recommender_method=='Collaborative filtering':
      print(f"NOT IMPLEMENTED: {recommender_method}")
    elif recommender_method=='Hybrid':
      print(f"NOT IMPLEMENTED: {recommender_method}")
          
    # Create streamlit components (category + navigation buttons)
    t.recommendations(df=df_subset)

if N_CATEGORIES < len(categories):
  st.subheader(f"**{len(categories)-N_CATEGORIES} more categories...**")

# Print session state
# print(st.session_state['category_offset'])
# print(df_subset)