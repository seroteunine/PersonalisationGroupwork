import streamlit as st
import pandas as pd
import json
import datetime
from random import random

# Constants
N_ITEMS = 5
N_CATEGORIES = 5
IMAGE_SIZE = 350
RECOMMENDER_METHODS = ( 'Views', 'Likes', 'Title', 'Date', 'Episode Amount', 'Random', 'Personalised', 'Collaborative filtering', 'Hybrid')
CUSTOM_CATEGORIES = {
  'Episodes you liked' : 'Like episode', 
  'Episodes you watched' : 'View episode'
}
EMOJIS = {
    'Episodes you liked' : ':thumbsup:',
    'Episodes you watched' : ':eyes:',
    'Arts' : ':art:',
    'Comedy' : ':laughing:',
    'Documentary' : ':newspaper:',
    'Drama' : ':drama:',
    'Entertainment' : ':clapper:',
    'CBBC' : ':tv:',
    'Documentaries' : ':newspaper:',
    'Films' : ':movie_camera:',
    'Food' : ':fork_and_knife:',
    'Music' : ':musical_note:',
    'History' : ':books:',
    'News' : ':newspaper:',
    'Science & Nature' : ':microscope:',
    'From the Archives' : ':floppy_disk:',
    'Signed' : ':pencil2:',
}

# Show a single item card (episode) in a column based on a record from the dataframe
def tile_item(column, item:dict):
  # add an view activity to the session state
  with column:
    message = f"Views: {item['views']}  |  Likes: {item['likes']}  |  Dislikes: {item['dislikes']} "
    # NOTE: use_column_width=True <- causes issues with image size for me, fix with something like width=IMAGE_SIZE?
    # NOTE: fixed width/column required for horizontal layout with less than 3 columns
    st.image(item['image'], caption=message, width=IMAGE_SIZE)
    #st.subheader(item['title']) # original title
    st.subheader(item['show'] + ' - ' + item['episode_title'])
    info = str(item['first_broadcast'].date())
    s, e = item['season'], item['episode']
    if s!=0 or e!=0:
      info += ' | '
    if s!=0:
      info += f"Season {s} "
    if e!=0:
      info += f"Episode {e} ({item['episode_n_total']} total)"
    st.caption(info)
    st.caption(item['description'])
    # view, like, dislike counter
    col1, col2, col3, col4, col5 = st.container().columns([2,1,1,1,2])
    with col2:
      st.button(':eyes:', key=random(), on_click=activity, args=(item['content_id'], 'View episode', False ))
    with col3:
      st.button(':thumbsup:', key=random(), on_click=activity, args=(item['content_id'], 'Like episode' ))
    with col4:
      st.button(':thumbsdown:', key=random(), on_click=activity, args=(item['content_id'], 'Dislike episode' ))
      
# save the activities as a file
def save_activities():
  with open('activities.json', 'w') as outfile:
    json.dump(st.session_state['activities'], outfile)

# function that processes an activity
def activity(id:str, activity:str, login_required:bool=True):
  user_id = str(st.session_state['user'])
  # check if user is logged in
  if login_required and user_id==0:
    st.info('You need to be logged in to do that!')
    return
  # check if the activity is already in the session state
  if any([a['user_id']==user_id and a['activity']==activity and a['content_id']==id for a in st.session_state['activities']]):
    st.info('You have already like/disliked this video!')
    return
  data = {'content_id': id, 'activity': activity, 'user_id': user_id, 'datetime': str(datetime.datetime.now())}
  # add to the session state
  st.session_state['activities'].append(data)
  # directly save the activities
  save_activities()

# Increment the offset for the next category
def category_offset(category:str, i:int, i_max:int):
  # get the current offset for the category
  val = st.session_state['category_offset'].get(category, 0)
  val += i
  # check if the offset is within the range of the items
  if (val<0): 
    val = 0
  if (val>i_max): 
    val = i_max
  # update the session state
  st.session_state['category_offset'][category] = val

# recommend items based on the session state
def recommendations(df:pd.DataFrame):
  # Select the first N_ITEMS per category/row in UI
  category = df['category'].iloc[0]
  offset = st.session_state['category_offset'].get(category, 0)
  df_temp = df.copy().reset_index(drop=True).loc[offset:offset+N_ITEMS-1, :]
  # title for the category
  category_title = category + ' ' + EMOJIS.get(category, 'NO EMOJI SET')
  st.subheader(category_title, anchor=category)
  # check the number of items
  nbr_items = df_temp.shape[0]
  if nbr_items != 0:    
    # create columns with the corresponding number of items
    columns = st.columns(nbr_items)
    # convert df rows to dict lists
    items = df_temp.to_dict(orient='records')
    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(x[0], x[1]) for x in zip(columns, items))
    # navigation buttons
    max_offset = len(df)-N_ITEMS
    col1, col2, col3, col4, col5 = st.container().columns([8, 1, 1, 1, 8])
    # Previous
    with col2:
      st.button(':arrow_left:', key=random(), on_click=category_offset, args=(category, -N_ITEMS, max_offset))
    # Show the current offset/page
    with col3:
      start = st.session_state["category_offset"].get(category, 0)+1
      end = st.session_state["category_offset"].get(category, 0)+N_ITEMS
      total = len(df)
      if end>total:
        end = total
      st.text(f'{start}-{end} of {total}')
    # Next
    with col4:
      st.button(':arrow_right:', key=random(), on_click=category_offset, args=(category, N_ITEMS, max_offset))