import pandas as pd

df = pd.read_pickle('../data/arts.pkl')
print(df.iloc[0])