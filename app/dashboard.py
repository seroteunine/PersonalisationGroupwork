import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

from data_import import data_import, FILE_POLITICAL, FILE_POLARIZING
from user_interface import activity

st.set_page_config()
st.title('BBC Video Recommender System - University Utrecht')
st.markdown('This is a demo dashboard of a video recommender system for the BBC.')

# Import data
df, df_activity, df_users, word_scores = data_import(overwrite_text=False, overwrite_activity=False) 

# Search bar functions
search_term = st.text_input("Search for shows", "")
button_clicked = st.button("OK", key="search_button", on_click=activity, args=(0, 'search', search_term))
if search_term != "":
  df = df.loc[df['text'].str.contains(search_term)]

# Core data
with st.expander('Show raw data'):
    st.table(df.loc[:, ['content_id','category', 'title', 'show', 'episode_title', FILE_POLITICAL, FILE_POLARIZING]].sample(10))

# Select the category / grouping var
#group_by = st.selectbox('Select a category', df.category.unique().tolist())

# Calculate the mean of the numeric columns per category
df_stats = df.groupby('category').mean(numeric_only=True).reset_index()

# Make tabs
tab1, tab2, tab3, tab4 = st.tabs({ 'Pyplot Text Description': df_stats, 'Wordcloud plots' : df, 'Streamlit plots' : df , 'Data Table': df })

# PYTHON PLOT
with tab1:
    # Some plots to check the data that is in text format
    st.subheader('Text length distribution')
    fig, ax = plt.subplots(3, 2, figsize=(10, 10))
    df['title'].str.len().hist(bins=100, ax=ax[0,0])
    df['description'].str.len().hist(bins=100, ax=ax[0,1])
    df['synopsis_small'].str.len().hist(bins=100, ax=ax[1,0])
    df['synopsis_medium'].str.len().hist(bins=100, ax=ax[1,1])
    df['synopsis_large'].str.len().hist(bins=100, ax=ax[2,0])
    ax[0,0].set_title('title'), ax[0,1].set_title('description'), ax[1,0].set_title('synopsis_small'), ax[1,1].set_title('synopsis_medium'), ax[2,0].set_title('synopsis_large')
    plt.suptitle('Text length distribution') 
    st.pyplot(fig)

    # Poltical + polarizing word tf_idf
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    df[f'{FILE_POLITICAL}_tf_idf'].hist(bins=25, ax=ax[0])
    ax[0].set_title('Distribution of political word count')
    df[f'{FILE_POLARIZING}_tf_idf'].hist(bins=25, ax=ax[1])
    ax[1].set_title('Distribution of polarizing word count')
    st.pyplot(fig)
    
    # Amount of broadcast per year
    fig, ax = plt.subplots()
    broadcast_timeseries = df.groupby('decennia').count().plot(y='title', kind='bar', ax=ax)
    fig.suptitle('Amount of broadcast per decennia', fontsize=20)
    st.pyplot(fig)
    
    # Average duration per year
    fig, ax = plt.subplots()
    duration_per_year = df.groupby('decennia').mean('duration_sec').reset_index().sort_values('decennia')
    duration_per_year.plot(x = 'decennia', y= 'duration_sec', kind='bar', ax=ax)
    fig.suptitle('Average duration per decennia', fontsize=20)
    st.pyplot(fig)
    
    # Average duration per category
    fig, ax = plt.subplots()
    duration_per_category = df.groupby('category').mean('duration_sec').reset_index().sort_values('duration_sec')
    duration_per_category.plot(x = 'category', y= 'duration_sec', kind='barh', ax=ax)
    fig.suptitle('Average duration per category', fontsize=20)
    st.pyplot(fig)
    
    # Amount broadcast per category per year
    # fig, ax = plt.subplots()
    # broadcast_timeseries = df.groupby(['decennia', 'category']).count().reset_index().plot(y='title', kind='bar', color="category", ax=ax)
    # fig.suptitle('Amount of broadcast per decennia per category', fontsize=20)
    # st.pyplot(fig)

# WORDCLOUD
with tab2:
    # Wordcloud
    #with col2:
    from wordcloud import WordCloud
    from nltk.corpus import stopwords
    corpus = df['text'].str.cat(sep=' ') # Concatenate all descriptions
    #corpus = re.sub(r'[^\w\s]','',corpus) # Remove punctuation
    text = corpus.lower().split(' ') # Split into lowercased words
    
    # Create a set of stopwords using the nltk library
    stop_words = set(stopwords.words('english'))
    # Remove the stopwords from the text
    filtered_text = ' '.join(word for word in text if word not in stop_words)
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)
    # Display the word cloud
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    fig.suptitle('Wordcloud of the descriptions', fontsize=20)
    st.pyplot(fig)

# STREAMLIT PLOTS
with tab3:
    st.text('Streamlit plots') 
    # Display the mean values per category
    st.subheader('Mean political per category')
    st.bar_chart(df_stats, x = 'category', y = FILE_POLITICAL)
    st.subheader('Mean polarization per category')
    st.bar_chart(df_stats, x = 'category', y = FILE_POLARIZING)
    
# DATA TABLE
with tab4:
  st.table(df_stats)