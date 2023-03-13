import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import os

DATA_DIR = '../data'
DATA_MISSING = ['No data found', 'No title found', 'No tags found', 'No image found']

# Data import imports the data from the pickle files and cleans it to be used in the app
def data_import():
    df = pd.concat([pd.read_pickle(os.path.join(DATA_DIR, x)) for x in os.listdir(DATA_DIR) if x.endswith('.pkl')])
    # Replace missing values
    df.replace(DATA_MISSING, '', inplace=True)
    df.loc[df.isnull().sum()] 
    # Clean data types
    df['first_broadcast'] = pd.to_datetime(['-'.join(x.split(' ')[-3:]) for x in df['first_broadcast']], infer_datetime_format=True) # Convert to datetime
    df.loc[df['first_broadcast'].isnull(), 'first_broadcast'] = pd.to_datetime('01-01-1900', infer_datetime_format=True) # Replace missing values with 1900-01-01
    df['duration_sec'] = df['duration_sec'].replace('', 0).astype(int) # Convert to int, replace missing values with 0
    # Create new columns
    df['year'] = df['first_broadcast'].dt.year
    df['month'] = df['first_broadcast'].dt.month
    df['day'] = df['first_broadcast'].dt.day
    df['decennia'] = np.round(df['year'], -1).astype(int)
    df['duration_min'] = df['duration_sec'] / 60
    df['duration_hour'] = df['duration_min'] / 60
    return df.drop_duplicates()


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
    
    