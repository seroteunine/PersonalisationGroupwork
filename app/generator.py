# Setup
import random
import names
# Custom modules
from data_import import data_import, json_dump

# Import data
df, df_activity, df_users, word_scores = data_import(overwrite_text=False, overwrite_activity=False) 

#N_PERSONAS = int(3) #1 = left, 2 = neutral, 3 = right
N_USERS = int(100)

users = []
activities = []

# User preferences
show_titles = df['show'].unique()
neutral_shows = ['Race Across the World', 'Do Black Lives Still Matter?','The Weakest Link', 'Luther', 'Morning Live', 'QAnon: After the Storm?', 'Why Ships Crash', 'Israel and Iran: The Hidden War', 'Scottish Parliament']
right_shows = ['Peaky Blinders', 'Top Gear', 'The Apprentice', "Dragons' Den", 'Panorama', "The Apprentice: You're Fired"]*2 + neutral_shows
left_shows = ['The Green Planet', 'Universe', 'Take a Hike', 'Turkey with Simon Reeve', 'Africa', 'The Blue Planet']*2 + neutral_shows
combined = [left_shows, neutral_shows, right_shows]

# Generate a single activity based on pre-defined logic/personas
def generate_activity(id, persona, activity):
    #Get show
    if persona == 'left':
       persona = 1
    elif persona == 'right':
       persona = 3
    else:
       persona = 2

    rand = random.random()
    if rand < 0.1: #Choose random show to watch
        show = random.sample(show_titles.tolist(), 1)
    else: #Choose a show corresponding to persona
        show = random.sample(combined[persona], 1)

    #Get unique episode from that show
    df_show = df[df['show'] == show[0]]
    random_episode = df_show.sample()
    content_id = int(random_episode['content_id'])
    previous_watched = [item['content_id'] for item in activity]
    if content_id in previous_watched: #Prevent double watch
       random_episode = df_show.sample()
       content_id = int(random_episode['content_id'])

    #Save episode as watched
    new_activity = {'content_id': content_id, "activity": "View episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
    activity.append(new_activity)

    #Sometimes like or dislike
    rand = random.random()
    if rand < 0.5:
        new_activity = {'content_id': content_id, "activity": "Like episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
        activity.append(new_activity)
    elif rand > 0.8:
        new_activity = {'content_id': content_id, "activity": "Dislike episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
        activity.append(new_activity)

    return activity

def getVote(age):
   return 'left'

# Generate users and activities
for user in range(N_USERS):
    #Create userdata
    id = user + 1
    if id <= 44: #Young generation 16-34
       age = random.sample(range(20,35), 1)[0]
    elif id < 84: #Middle generation 35-54
       age = random.sample(range(35, 55), 1)[0]
    else: #Old generation 55+
       age = random.sample(range(55, 71), 1)[0]

    vote = getVote(age)

    data = {'name': names.get_first_name() + str(id), 'id': id, 'password': 'recommender', 'age': age, 'vote': vote}

    #Create user activity
    activity = []
    for n in range(random.randint(10, 50)):
      new_activity = generate_activity(id, vote, activity)
    activities.extend(activity)
    users.append(data)

# Write to disk as json
json_dump(users, 'users_generated.json')
json_dump(activities, 'activities_generated.json')