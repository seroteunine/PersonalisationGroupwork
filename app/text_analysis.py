import pandas as pd
import numpy as np
import os
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_DIR = '../data'

# Returns a tuple with the vectorizer and the tf-idf scores for the corpus
def tf_idf(corpus, words) -> pd.DataFrame:
    vectorizer=TfidfVectorizer(vocabulary=words)
    X = vectorizer.fit_transform(corpus)
    vectorizer.get_feature_names_out()
    df_new = pd.DataFrame(X.toarray(), columns=words) 
    return df_new

# Generate a dataframe with the number of times each word occurs in the descriptions
def generate_word_score(df:pd.DataFrame, method:str="tf_idf", file_name = 'polarizing_words', 
                        overwrite:bool=False, remove_zero:bool=True, remove_stop_words:bool=True) -> pd.DataFrame:
    # Define the file paths
    file_path = os.path.join(DATA_DIR, file_name + '.csv')
    file_path_new = os.path.join(DATA_DIR, f"{file_name}_{method}.csv")
    # Check if the file already exists and if not, generate it
    if os.path.exists(file_path_new) and not overwrite:
        return pd.read_csv(file_path_new)    
    print(f"Generating scores for {file_name} using {method} for {len(df)} observations...") 
    
    # Import the words we want to match/score/count
    words = pd.read_csv(file_path)
    # Convert to a list of lowercased words
    words = set(words['word'].str.lower())
    if remove_stop_words:
        nltk.download('stopwords')
        stop_words = set(nltk.corpus.stopwords.words('english'))
        words = words.difference(stop_words)
    words = list(words)
    
    # Concatenate all text and remove punctuation
    corpus_combined = df['text'].str.cat(sep=' ') 
    corpus_combined = re.sub(r'[^\w\s]','',corpus_combined) 
    # Split into lowercased words
    text_combined = corpus_combined.lower().split(' ')
    
    # Find the intersection between the words in the text and the words
    intersection = set(text_combined).intersection(words) 
    p, t = len(intersection), len(words)
    print(f"{p/t:.2%} of the words are both in the text and in the word list ({p}/{t})") 
    
    if method=="tf_idf":
        # Use the function to calculate the tf-idf scores and sum the scores (of all words) for each observation
        df_new = tf_idf(corpus=df['text'],words=words)
        
    elif method=="count":
        # Count the number of times each word occurs in the text
        text = [df["text"].str.count(word) for word in words]
        df_new = pd.concat(text, axis=1) # combine to dataframe
        df_new.columns = words
        # Remove no words found
        if remove_zero:
            word_found = df_new.sum(axis=0) > 0
            df_new = df_new.loc[:, word_found]
    # Save the results
    df_new.to_csv(file_path_new, index=False)
    return df_new