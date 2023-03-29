import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Returns a tuple with the vectorizer and the tf-idf scores for the corpus
def tf_idf(corpus, words) -> pd.DataFrame:
    vectorizer=TfidfVectorizer(vocabulary=words)
    X = vectorizer.fit_transform(corpus)
    vectorizer.get_feature_names_out()
    df_new = pd.DataFrame(X.toarray(), columns=words) 
    return df_new
