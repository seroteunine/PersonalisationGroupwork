import pandas as pd
from tqdm import tqdm

MIN_RECOMMENDATIONS = 5

df = pd.read_json('activities_generated.json')

shows_perUser = df.groupby('user_id')['show'].apply(list)

def jaccard(a, b): #with repeats
    a, b = set(a), set(b)
    intersection = len(a & b)
    union = len(a | b)
    # Avoid recommending shows if there are too few recommendations (users are too similar)
    # if (len(b) - intersection) < MIN_RECOMMENDATIONS:
    #     return 0
    repeats = intersection / (len(a) + len(b) - intersection)
    return (intersection / union) #- repeats

df_similar = pd.DataFrame({'user_id': [], 'similar_user': [], 'show': []})

#For each user, loop over all other users and calcute similarity, add user with highest similarity to df
for index1, shows1 in tqdm(shows_perUser.items()):
    sim_id, sim_score = 0, 0
    for index2, shows2 in shows_perUser.items():
        if index1 != index2: #Exclude comparison to self
            similarity = jaccard(shows1, shows2)
            if similarity > sim_score:
                sim_id, sim_score = index2, similarity
    #After getting the most similar user -> get shows of that user this user hasnt watched
    recommendation = list(set(shows_perUser.iloc[sim_id - 1]) - set(shows1))
    df_similar = pd.concat([df_similar, pd.DataFrame({'user_id': [index1], 'similar_user': [sim_id], 'show': [recommendation]})])
    # df_similar.loc[len(df_similar)] = [index1, sim_id, recommendation]
df_similar = df_similar.explode('show').reset_index(drop=True)
df_similar.to_json('recommendations.json', orient='records')