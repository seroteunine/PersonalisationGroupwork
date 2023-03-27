import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import os

# Constants
DATA_DIR = '../data'
DATA_MISSING = ['No data found', 'No title found', 'No tags found', 'No image found']

# Data import imports the data from the pickle files and cleans it to be used in the app
def data_import_bbc():
    df = pd.concat([pd.read_pickle(os.path.join(DATA_DIR, x)) for x in os.listdir(DATA_DIR) if x.endswith('.pkl')])
    # Replace missing values
    df.replace(DATA_MISSING, '', inplace=True)
    #df.loc[df.isnull().sum()] 
    # Clean data types
    df['first_broadcast'] = pd.to_datetime(['-'.join(x.split(' ')[-3:]) for x in df['first_broadcast']], infer_datetime_format=True) # Convert to datetime
    df.loc[df['first_broadcast'].isnull(), 'first_broadcast'] = pd.to_datetime('01-01-1900', infer_datetime_format=True) # Replace missing values with 1900-01-01
    df['duration_sec'] = df['duration_sec'].replace('', 0).astype(int) # Convert to int, replace missing values with 0
    df['image'] = df['image'].replace('', os.path.join(DATA_DIR, 'missing_image.png')) # Replace missing values with placeholder image
    df.sort_values(by='first_broadcast', inplace=True) # Sort by date
    # Extract datetime features
    df['year'] = df['first_broadcast'].dt.year
    df['month'] = df['first_broadcast'].dt.month
    df['day'] = df['first_broadcast'].dt.day
    df['decennia'] = np.round(df['year'], -1).astype(int)
    df['duration_min'] = df['duration_sec'] / 60
    df['duration_hour'] = df['duration_min'] / 60
    # Convert title to show, season, episode
    df['show'] = [re.split(' - ', x, maxsplit=1)[0] for x in df['title']] # Extract show name
    df['episode_title'] = [x.replace(y.strftime('%d/%m/%Y'), '') for x,y in zip(df['title'], df['first_broadcast'])] # Remove date from title
    df['episode_title'] = [re.split(' - ', x, maxsplit=1) for x in df['title']] # Extract episode name
    df['episode_title'] = df['episode_title'].map(lambda x: x[1] if len(x) > 1 else '').map(lambda x: x.split('.')[-1] if '.' in x else x).map(lambda x: x if len(x)>2 else '') # Clean episode title
    #df['episode_title'] = [' '.join(re.findall(r'\w+', t.replace(s, ''))) for t, s in zip(df['title'], df['show'])] # Extract episode title by removing show name
    df['season'] = [re.findall(r'Series (\d+)', x) for x in df['title']] # Extract season number
    df['season'] = df['season'].map(lambda x: x[0] if len(x) > 0 else '').replace('', 0).astype(int) # Convert to int, replace missing values with 0
    df['episode'] = [re.findall(r'\d+', re.split(': ', x)[-1]) for x in df['title']] # Extract episode number 
    df['episode'] = df['episode'].map(lambda x: x[-1] if len(x) > 0 else '').replace('', 0).astype(int) # Convert to int, replace missing values with 0
    # Episode number + total
    df['episode_n'] = df.groupby(['show']).cumcount() # Episode number cumulative
    total = df.groupby('show').max('episode_n')['episode_n'].rename('episode_n_total') # Total number of episodes for each show
    df = df.merge(total, on='show', how='left') # Merge with df
    # Clean up the dataframe + add index as content_i d
    df.reset_index(drop=True, inplace=True)
    df['content_id'] = df.index 
    df = df.drop_duplicates()
    return df

  # calculate the number of likes per episode and merge with the df
def aggregate_activity(df_activity:pd.DataFrame, activity:str, column_name:str) -> pd.DataFrame:
  return df_activity.loc[df_activity['activity']==activity, :].groupby('content_id').count()['activity'].rename(column_name).reset_index()

# Combine all data sources
def data_import():
    # Load BBC video dataset
    df = data_import_bbc()
    # Load users and activities
    df_activity = pd.read_json('activities_generated.json')
    # calculate the number of likes, dislikes and views per episode and merge with the df
    for activity, column_name in zip(['Like episode', 'Dislike episode', 'View episode'], ['likes', 'dislikes', 'views']):
        counted = aggregate_activity(df_activity, activity, column_name)
        df = df.merge(counted, on="content_id", how="left").replace(np.nan, 0).astype({column_name: int})
    return df

if __name__ == '__main__':
        # Load data
    df = data_import()
    print(df.columns)   
    print(df.head())
    
        # Some plots to check the data
    # Amount of broadcast per year
    broadcast_timeseries = df.groupby('decennia').count().plot(y='title', kind='bar')
    plt.show()
    # Average duration per year
    duration_per_year = df.groupby('decennia').mean('duration_sec').reset_index().sort_values('duration_sec')
    duration_per_year.plot(x = 'decennia', y= 'duration_sec', kind='bar')
    plt.show()
    # Average duration per category
    duration_per_category = df.groupby('category').mean('duration_sec').reset_index().sort_values('duration_sec')
    duration_per_category.plot(x = 'category', y= 'duration_sec', kind='barh')
    plt.show()
    
        # Lets do some simple text analysis
    import pandas as pd
    from wordcloud import WordCloud
    from nltk.corpus import stopwords
    corpus = df['description'].str.cat(sep=' ') # Concatenate all descriptions
    corpus = re.sub(r'[^\w\s]','',corpus) # Remove punctuation
    text = corpus.lower().split(' ') # Split into lowercased words
    
    # Create a set of stopwords using the nltk library
    stop_words = set(stopwords.words('english'))
    # Remove the stopwords from the text
    filtered_text = ' '.join(word for word in text if word not in stop_words)
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)
    # Display the word cloud
    import matplotlib.pyplot as plt
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.suptitle('Wordcloud of the descriptions', fontsize=20)
    plt.show()
    
    