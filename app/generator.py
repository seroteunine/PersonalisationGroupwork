# Setup
import random
import names
# Custom modules
from data_import import data_import, json_dump

# Import data
df, df_activity, df_users, word_scores = data_import(overwrite_text=False, overwrite_activity=False) 

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
def generate_activity(id, age, vote, activity):
    if vote == 'left':
       persona = 0
    elif vote == 'right':
       persona = 2
    else:
       persona = 1

    #Select a random show
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

    #Add episode as being watched to activity of that user
    new_activity = {'content_id': content_id, "activity": "View episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
    activity.append(new_activity)

    #Like or dislike occasionaly
    rand = random.random()
    if rand < 0.5:
        new_activity = {'content_id': content_id, "activity": "Like episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
        activity.append(new_activity)
    elif rand > 0.8:
        new_activity = {'content_id': content_id, "activity": "Dislike episode", "user_id": id, "datetime": "2023-02-26 17:50:01.051431"}
        activity.append(new_activity)

    return

def getVote(age):
   pLabour = -0.6 * age + 52
   pCons = 0.8 * age -3.6
   pCentre = -0.2 * age + 51.6
   vote = random.choices(['left', 'centre', 'right'], weights = [pLabour, pCentre, pCons])
   return vote[0]

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
       generate_activity(id, age, vote, activity)
    activities.extend(activity)
    users.append(data)

# Write to disk as json
json_dump(users, 'users_generated.json')
json_dump(activities, 'activities_generated.json')