    # Setup
import streamlit as st
import pandas as pd
import template as t
from data_import import data_import
import authenticate as a
import json
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

# open the activities json file
with open('activities.json') as json_file:
  users_activities = json.load(json_file)

# Load users and activities
df_activity = pd.read_json('activities.json')
df_users = pd.read_json('users.json')

# create a session state
if 'user' not in st.session_state:
  st.session_state['user'] = 0

if 'activities' not in st.session_state:
  st.session_state['activities'] = users_activities

# authenticate 
a.authenticate()

#User history
if st.session_state['user'] != 0:
  st.title('Your personal history:')
  df_personal = df_activity[df_activity.user_id == st.session_state['user']]
  likes = df_personal['content_id']
  for like in likes:
    st.subheader('You liked episode: ' + str(like))


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
