# Setup
import re
import os
import requests
import json
import pandas as pd
import numpy as np
import streamlit as st
from bs4 import BeautifulSoup   
# Custom modules
from text_analysis import tf_idf, generate_word_score

# Constants to be used in the app (modules)
DATA_DIR = '../data'
DATA_MISSING = ['No data found', 'No title found', 'No tags found', 'No image found']
DATA_MISSING_DATE = '01-01-1900'
DATA_MISSING_NUMERIC = 0
# Local file settings for runtime
FILE_USER = 'users.json' # 'users' or 'users_generated'
FILE_ACTIVITY = 'activities_generated.json' # 'activities' or 'activities_generated'
FILE_RECOMMENDATIONS = 'recommendations.json'
FILE_POLITICAL = 'political_words'
FILE_POLARIZING = 'polarizing_words_chatgpt' # 'polarizing_words' or 'polarizing_words_chatgpt'
FILES = ['political_words', 'polarizing_words', 'polarizing_words_chatgpt'] #, 'left_wing_words_chatgpt', 'right_wing_words_chatgpt']
DATA_IMPORT_METHODS = ['tf_idf', 'count']
FILTER_THRESHOLD = 1.5 # Filter threshold for recommender in standard deviation units

# Save json to disk
def json_dump(data:dict, file_name:str):
  with open(file_name, 'w') as outfile:    
    json.dump(data, outfile)

# Download poltical words from https://relatedwords.io/politics
def webscrape_poltical_words(overwrite:bool=False) -> pd.DataFrame:
    # Check if the file already exists and if not, generate it
    file_path = os.path.join(DATA_DIR, FILE_POLITICAL + '.csv')
    if os.path.exists(file_path) and not overwrite:
        return pd.read_csv(file_path)    
    print("Downloading political words...")
    
    data = requests.get('https://relatedwords.io/politics').content
    soup = BeautifulSoup(data, 'html.parser')
    words = [x.text.replace('\n', '', ) for x in soup.find_all('span', class_='term')]
    df_political = pd.DataFrame(words, columns=['word'])
    df_political.to_csv(file_path, index=False)
    return df_political

# Data import imports the data from the pickle files and cleans it to be used in the app
def data_import_bbc():
    print("Importing data from pickled files...")
    # Combine the pickled dataframes into one
    df = pd.concat([pd.read_pickle(os.path.join(DATA_DIR, x)) for x in os.listdir(DATA_DIR) if x.endswith('.pkl')])
    df.replace(DATA_MISSING, '', inplace=True) # Replace missing values with empty string for now
    df = df.loc[df['title']!="",:] # Remove rows with no title
    
    # Clean original data types
    df['first_broadcast'] = pd.to_datetime(['-'.join(x.split(' ')[-3:]) for x in df['first_broadcast']], infer_datetime_format=True) # Convert to datetime
    df.loc[df['first_broadcast'].isnull(), 'first_broadcast'] = pd.to_datetime(DATA_MISSING_DATE, infer_datetime_format=True) # Replace missing values with 1900-01-01
    df['duration_sec'] = df['duration_sec'].replace('', DATA_MISSING_NUMERIC).astype(int) 
    df['image'] = df['image'].replace('', os.path.join(DATA_DIR, 'missing_image.png')) # Replace missing values with placeholder image
    # Extract text features and combine them in lowercase
    df['text'] = [' '.join([a,b,c,d]) for a,b,c,d in \
        zip(df['title'].str.lower(), df['description'].str.lower(), df['synopsis_small'].str.lower(), df['synopsis_medium'].str.lower())] 
    df['word_count'] = df['text'].map(lambda x: len(x.split(' '))) # Word count
    # Extract datetime features
    df['year'] = df['first_broadcast'].dt.year
    df['month'] = df['first_broadcast'].dt.month
    df['day'] = df['first_broadcast'].dt.day
    df['decennia'] = np.round(df['year'], -1).astype(int)
    df['duration_min'] = df['duration_sec'] / 60
    df['duration_hour'] = df['duration_min'] / 60
    
    # Convert title to show and episode name
    df['show'] = [re.split(' - ', x, maxsplit=1)[0] for x in df['title']] # Extract show name
    df['episode_title'] = [x.replace(y.strftime('%d/%m/%Y'), '') for x,y in zip(df['title'], df['first_broadcast'])] # Remove date from title
    df['episode_title'] = [re.split(' - ', x, maxsplit=1) for x in df['title']] # Extract episode name
    df['episode_title'] = df['episode_title'].map(lambda x: x[1] if len(x) > 1 else '') \
        .map(lambda x: x.split('.')[-1] if '.' in x else x).map(lambda x: x if len(x)>2 else '')
        
    # Extract the season and episode number
    df.sort_values(by='first_broadcast', inplace=True) # Sort by date
    # Extract season number
    df['season'] = [re.findall(r'Series (\d+)', x) for x in df['title']] 
    df['season'] = df['season'].map(lambda x: x[0] if len(x) > 0 else '').replace('', DATA_MISSING_NUMERIC).astype(int) 
     # Extract episode number 
    df['episode'] = [re.findall(r'\d+', re.split(': ', x)[-1]) for x in df['title']]
    df['episode'] = df['episode'].map(lambda x: x[-1] if len(x) > 0 else '').replace('', DATA_MISSING_NUMERIC).astype(int) 
    # Episode number + total
    df['episode_n'] = df.groupby(['show']).cumcount() # Episode number cumulative
    total = df.groupby('show').max('episode_n')['episode_n'].rename('episode_n_total') # Total number of episodes for each show
    df = df.merge(total, on='show', how='left') # Merge with df
    
    # Clean up the dataframe + add index as content_id
    df.reset_index(drop=True, inplace=True)
    df['content_id'] = df.index 
    df = df.drop_duplicates()
    return df

# calculate the number of likes per episode and merge with the df
def aggregate_activity(df_activity:pd.DataFrame, activity:str, column_name:str, overwrite:bool=False) -> pd.DataFrame:
    file_path = os.path.join(DATA_DIR, f"aggregate_{column_name}.csv")
    # Check if the file already exists and if not, generate it
    if os.path.exists(file_path) and not overwrite:
        return pd.read_csv(file_path)    
    print(f"Aggregating {column_name} using action {activity}...") 
    
    # Aggregate the number of likes, dislikes and views per episode
    df = df_activity.loc[df_activity['activity']==activity, :].groupby('content_id').count()['activity'].rename(column_name).reset_index()
    df.to_csv(file_path, index=False)
    return df

"""
Combine all data sources:
- Load BBC video dataset
- Load users and activities
- Calculate the number of likes, dislikes and views per episode and merge with the df
- Iterate over file and method to add to the calculations df (tf_idf, count)
- Merge the results with the df
- Save the results

Parameters:
overwrite_text: rewrite the text file calculation to disk (tf_idf, count)
overwrite_activity: rewrite the activity file calculation to disk (number of likes, dislikes and views)
"""
@st.cache_data
def data_import(overwrite_text:bool=False, overwrite_activity:bool=False) -> tuple:
    # Load BBC video dataset
    df = data_import_bbc()
    # Load users and activities
    print("Importing users and activities...")
    df_activity = pd.read_json(FILE_ACTIVITY)
    df_users = pd.read_json(FILE_USER)
    
    # calculate the number of likes, dislikes and views per episode and merge with the df
    print("Importing aggregation of likes, dislikes and views...")
    for activity, column_name in zip(['Like episode', 'Dislike episode', 'View episode'], ['likes', 'dislikes', 'views']):
        counted = aggregate_activity(df_activity, activity, column_name, overwrite_activity)
        df = df.merge(counted, on="content_id", how="left").replace(np.nan, 0).astype({column_name: int})
    
    # iterate over file and method to add to the calculations df
    print("Importing word scores...")
    word_scores = dict()
    for file_name in FILES:
        for method in DATA_IMPORT_METHODS:
            # Generate the word scores
            df_new = generate_word_score(df, file_name=file_name, method=method, overwrite=overwrite_text, remove_zero=True)
            df_new.index = df['content_id']
            column_name = f"{file_name}_{method}"
            word_scores[column_name] = df_new 
            df_new_total = df_new.sum(axis=1).reset_index().rename(columns={'index':'content_id', 0: column_name})
            # Combine the aggregated dataframe
            df = df.merge(df_new_total, on='content_id', how='left')
    
    # Decide on polarity warning based on outlier detection of the tf-idf scores
    print("Calculating polarity warning...")
    tf_idf_files = [f"{file_name}_tf_idf" for file_name in FILES]
    for idx, check in enumerate(tf_idf_files):
        mu =  df[check].mean() # Mean
        sd =  df[check].std() # Standard deviation
        df[FILES[idx]] = df[check].apply(lambda x: 1 if x > mu + FILTER_THRESHOLD*sd else 0) # 1 if outlier
    df['score'] = df[tf_idf_files].sum(axis=1) # Sum the scores
    
    # Add the recommendations for the user
    print("Importing recommendations...")	
    df_recommendations = pd.read_json(FILE_RECOMMENDATIONS)
    
    # Save the data to disk for anyone who is interested in using it    
    df.to_csv(os.path.join(DATA_DIR, 'df.csv'), index=False)
    return df, df_activity, df_users, df_recommendations, word_scores 












# Runtime for updating the data
if __name__ == '__main__':
    # Set overwrite=False to use the cached data on disk (faster)
    df, df_activity, df_users, word_scores = data_import(overwrite_text=False, overwrite_activity=False) 
    
# Test code
if __name__ == '__test__':
    
    # Test the data import
    df = data_import_bbc()
    
    # Set overwrite=True to regenerate the data cache, e.g. if you have added new words to the csv files or generated new data
    df, df_activity, df_users, df_recommendations, word_scores = data_import(overwrite_text=False, overwrite_activity=True) 
    print(df.columns)   
    print(df.head())
    # We can access the detailed word scores by accessing the dictionary
    print(word_scores.keys())
    
    # webscrape the political words
    df_political = webscrape_poltical_words(overwrite=True)     
    
    word_scores['polarizing_words_tf_idf']
    
    # Most shows are missing the 'synopsis_large', so we will not use this column. This could skew our word count because 'synopsis_large' is the longest text column.
    # These are the columns we will use: title, description, synopsis_medium
    # Combined to single column for text analysis:
    df['text']
    
    # This shows why we need to do text pre processing 
    len(df.loc[df['description'].str.contains('trump')])
    len(df.loc[df['text'].str.contains('trump')])
    # 2 vs. 25 results when searching for 'trump'
    
    # word counts are generated to a csv file, so we can use it later from cache instead of generating it every time
    df_polarizing = generate_word_score(df, overwrite=True, file_name='polarizing_words')
    df_political = generate_word_score(df, file_name='political_words', overwrite=True, remove_zero=True)
    
    # Check the most polarizing words descriptions
    df.sort_values('polarizing_word_count', ascending=False)['title'].head(100).values
    # notice that most of these are not even political shows, most of them should therefore not be classifified as polarizing, even if they contain polarizing words
    df['polarizing_word_count'].describe()
    political_words = webscrape_poltical_words(overwrite=True)
    text = [df["text"].str.count(row["word"]) for index, row in political_words.iterrows()]
    pd.concat(text, axis=1).sum(axis=1)  
     
    # generate tf-idf scores
    corpus = df['text']
    # Get the tf-idf values for the corpus
    df_tf_idf = tf_idf(corpus, words=['trump', 'biden', 'election'])
    print(df_tf_idf.shape)
    
    # Check the most polarizing words descriptions  
    df['political_words_tf_idf'].describe()
    df['polarizing_words_tf_idf'].describe()
    
    
    

    
    word_scores['polarizing_words_tf_idf'].loc[:, ['gun', 'terrorism', 'violence']].describe()
    
    word_scores['polarizing_words_chatgpt_tf_idf'].loc[:, ['trump','biden']].describe()
    
    
