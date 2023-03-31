import pandas as pd

df = pd.read_json('activities_generated.json')

shows_perUser = df.groupby('user_id')['show'].apply(list)

def jaccard(a, b): #with repeats
    intersection = len(set(a) & set(b))
    union = len(set(a) | set(b))
    repeats = intersection / (len(a) + len(b) - intersection)
    return (intersection / union) - repeats

df_similar = pd.DataFrame({'user_id': [], 'similar_user': [], 'recommendation': []})

#For each user, loop over all other users and calcute similarity, add user with highest similarity to df
for index1, shows1 in shows_perUser.items():
    sim_id, sim_score = 0, 0
    for index2, shows2 in shows_perUser.items():
        if index1 != index2: #Exclude comparison to self
            similarity = jaccard(shows1, shows2)
            if similarity > sim_score:
                sim_id, sim_score = index2, similarity
    #After getting the most similar user -> get shows of that user this user hasnt watched
    recommendation = set(shows_perUser.iloc[sim_id - 1]) - set(shows1)
    df_similar.loc[len(df_similar)] = [index1, sim_id, recommendation]

df_similar.to_json('recommendations.json', orient='records')