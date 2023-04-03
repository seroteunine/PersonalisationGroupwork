# Packages
import streamlit as st
import pandas as pd
import datetime
from random import random
# Custom modules
from data_import import json_dump, FILE_ACTIVITY, FILE_POLITICAL, FILE_POLARIZING, FILES

# Constants
N_ITEMS = 5 # Number of items to show in the UI (per category)
N_CATEGORIES = 7 # Number of categories to show in the UI
# Sort/filter options for the recommender system
RECOMMENDER_METHODS = ('Views', 'Likes', 'Title', 'Date', 'Episode Amount', 'Random', \
                       'Political', 'Polarization', 'Political + Polarization', 'Personalised', 'Collaborative filtering', 'Hybrid')
# Custom categories for logged in users
CUSTOM_CATEGORIES = {
  'Episodes you liked' : 'Like episode', 
  'Episodes you watched' : 'View episode'
}
# Emojis for the categories (for the UI)
EMOJIS = {
    'Recommended' : ':tv:',
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

# Table containing the word scores for the different files
def item_match_score(item:dict, word_scores:dict, file:str='polarizing_words_chatgpt', method:str='tf_idf'):
    file_name = file + '_' + method
    scores = word_scores[file_name].iloc[item['content_id']]
    words_found = scores[scores > 0]
    words_found.name = file_name
    st.table(words_found)

# Show a single item card (episode) in a column based on a record from the dataframe
def tile_item(column, item:dict, word_scores:dict, debug:bool=False):
  with column:
    # Image with caption
    header = item['show']
    if item['episode_title'] != '':
      header += ' - ' + item['episode_title']
    st.subheader(header)
    message = f"Views: {item['views']}  |  Likes: {item['likes']}  |  Dislikes: {item['dislikes']}"
    st.image(item['image'], caption=message)
    
    # Text below the image logic
    info = str(item['first_broadcast'].date())
    s, e = item['season'], item['episode']
    if s!=0 or e!=0:
      info += ' | '
    if s!=0:
      info += f"Season {s} "
    if e!=0:
      info += f"Episode {e} ({item['episode_n_total']} total)"
    
    # Display the info and the description
    st.caption(info)
    if item['description'] != '':
      st.caption(item['description'])
    if item['synopsis_medium'] != '':
      st.caption(item['synopsis_medium']) # Display additional text
            
    # view, like, dislike counter
    col1, col2, col3, col4, col5 = st.container().columns([1,1,1,1,1])
    with col2:
      st.button(':eyes:', key=random(), on_click=activity, args=(item['content_id'], 'View episode', "view", False ))
    with col3:
      st.button(':thumbsup:', key=random(), on_click=activity, args=(item['content_id'], 'Like episode', "like", True ))
    with col4:
      st.button(':thumbsdown:', key=random(), on_click=activity, args=(item['content_id'], 'Dislike episode', "dislike", True ))
    
    # warning when the tf-idf scores are high for the episode
    if item[FILE_POLITICAL] and item[FILE_POLARIZING]:
      st.error('This might be considered as political and polarizing content')
    elif item[FILE_POLITICAL]:
      st.warning('This might be considered as political content')
    elif item[FILE_POLARIZING]:
      st.warning('This might be considered as polarizing content')
      
    # Display additional text when in debug mode
    if debug:
      # Display the political and polarizing words
      st.caption(f"Political: {item[f'{FILE_POLITICAL}_count']}  |  Polarizing: {item[f'{FILE_POLARIZING}_count']}  |  Total: {item['word_count']}")
      st.caption(f"Political tf_idf: {item[f'{FILE_POLITICAL}_tf_idf']:0.3f}  |  Polarizing tf_idf: {item[f'polarizing_words_tf_idf']:0.3f}  |  Polarizing tf_idf chatgpt: {item[f'polarizing_words_chatgpt_tf_idf']:0.3f}")
      st.caption(f"Political + Polarization: {item['score']:0.3f}")
      for file in FILES:
        item_match_score(item, word_scores, file)
      
# function that processes an activity
def activity(id:str, activity:str, data="", login_required:bool=True, datetime:datetime=datetime.datetime.now()):
  user_id = str(st.session_state['user'])
  # check if user is logged in
  if login_required and user_id==0:
    st.info('You need to be logged in to do that!')
    return
  # check if the activity is already in the session state
  if any([a['user_id']==user_id and a['activity']==activity and a['content_id']==id for a in st.session_state['activities']]):
    st.info(f'You have already performed {activity} on this video!')
    return
  record = {'content_id': id, 'activity': activity, 'user_id': user_id, 
          'datetime': str(datetime), 'data': data}
  # add to the session state
  st.session_state['activities'].append(record)
  # directly save the activities
  json_dump(st.session_state['activities'], FILE_ACTIVITY)

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
def recommendations(df:pd.DataFrame, word_scores:dict, debug:bool=False):
  # Select the first N_ITEMS per category/row in UI
  category = df['category'].iloc[0]
  offset = st.session_state['category_offset'].get(category, 0)
  df_temp = df.copy().drop_duplicates(subset=['content_id']).reset_index(drop=True).loc[offset:offset+N_ITEMS-1, :]
  # title for the category
  category_title = category + ' ' + EMOJIS.get(category, 'NO EMOJI SET')
  st.subheader(category_title, anchor=category)
  # check the number of items
  nbr_items = df_temp.shape[0]
  if nbr_items != 0:    
    # create columns with the corresponding number of items
    columns = st.columns(N_ITEMS)
    # convert df rows to dict lists
    items = df_temp.to_dict(orient='records')
    # apply tile_item to each column-item tuple (created with python 'zip')
    any(tile_item(column=x[0], item=x[1], word_scores=word_scores, debug=debug) for x in zip(columns, items))
    # navigation buttons
    max_offset = len(df)-N_ITEMS
    col1, col2, col3, col4, col5 = st.container().columns([4, 1, 1, 1, 4])
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