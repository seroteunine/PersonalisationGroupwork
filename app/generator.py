import json
import names
import random
import pandas as pd
from data_import import data_import
df = data_import()

N_PERSONAS = 3
N_USERS_PER_PERSONA = 30

users = []
activities = []

show_titles = df['show'].unique()

neutral_shows = ['Race Across the World', 'Do Black Lives Still Matter?','The Weakest Link', 'Luther', 'Morning Live', 'QAnon: After the Storm?', 'Why Ships Crash', 'Israel and Iran: The Hidden War', 'Scottish Parliament']
right_shows = ['Peaky Blinders', 'Top Gear', 'The Apprentice', "Dragons' Den", 'Panorama', "The Apprentice: You're Fired"]*2 + neutral_shows
left_shows = ['The Green Planet', 'Universe', 'Take a Hike', 'Turkey with Simon Reeve', 'Africa', 'The Blue Planet']*2 + neutral_shows
combined = [left_shows, neutral_shows, right_shows]

def generate_activity(id, persona, activity):
    previous_watched = [item['content_id'] for item in activity]

    #Get show
    rand = random.randint(0,1)
    if rand < 0.1: #Choose random show to watch
        show = random.sample(show_titles.tolist(), 1)
    else: #Choose a show corresponding to persona
        show = random.sample(combined[persona], 1)

    #Get unique episode from that show
    df_show = df[df['show'] == show[0]]
    random_episode = df_show.sample()
    content_id = int(random_episode['content_id'])
    if content_id in previous_watched: #Prevent double watch
       random_episode = df_show.sample()
       content_id = int(random_episode['content_id'])

    #Save episode as watched
    new_activity = {'content_id': content_id, "activity": "View episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
    activity.append(new_activity)

    #Sometimes like that episode as well
    rand = random.randint(0,1)
    if rand < 0.4:
        new_activity = {'content_id': content_id, "activity": "Like episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
        activity.append(new_activity)
  
    return activity


for persona in range(N_PERSONAS):
  for user in range(N_USERS_PER_PERSONA):
    id = user + persona * N_USERS_PER_PERSONA + 1
    data = {'name': names.get_first_name() + str(id), 'id': id, 'password': 'recommender'}
    activity = []
    for N in range(random.randint(10, 30)):
      generate_activity(id, persona, activity)
    activities.extend(activity)
    users.append(data)

def save_activities():
  with open('activities_generated.json', 'w') as outfile: 
    json.dump(activities, outfile)  

def save_users():
  with open('users_generated.json', 'w') as outfile:    
    json.dump(users, outfile)

save_activities()
save_users()