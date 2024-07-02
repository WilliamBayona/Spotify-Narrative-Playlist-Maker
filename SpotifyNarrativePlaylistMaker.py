from pydtmc import MarkovChain
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from dotenv import load_dotenv
import os
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import random

#About Gemini KEY
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
GOOGLE_API_KEY="YOURKEY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

chat = model.start_chat(history=[])



load_dotenv()

def clear_cache():
    # Remove cached token file
    try:
        os.remove(".cache")
    except FileNotFoundError:
        pass


def authenticate_spotify():
    clear_cache()
    client_id = "CLIENT_ID"
    client_secret ="CLIENT_SECRET"
    client_uri = "http://127.0.0.1:8080/"

    scope = "user-top-read playlist-modify-public"
    
    token = SpotifyOAuth(client_id=client_id,client_secret=client_secret,redirect_uri=client_uri,scope = scope)
    spotifyObject = spotipy.Spotify(auth_manager = token)
    
    return spotifyObject


def create_playlist(sp, playlist_name):
    username = sp.current_user()
    sp.user_playlist_create(user=username["id"],name=playlist_name,public=True,description="Maybe I should stop")


# Authenticate user
sp = authenticate_spotify()

#Get the Tracks 
tracks = results = sp.current_user_top_tracks(time_range="long_term", limit=50)

trackList=[]
promptList=[]

for i, item in enumerate(results['items']):
    trackList.append(item["name"])
    promptList.append(str(item['name']) + ' by ' + str(item['artists'][0]['name']))

#print(trackList)

prompt = "Here is a list of 50 songs " + str(promptList) + ", can you please return me a list of some of feelings this songs express, separated by commas. If you find any sexually explicit song, ignore it"
print(prompt)
response = chat.send_message(prompt)

print("***************************************************+****************************+****************************+****************************+****************************+****************************+")

feelingsList = response.text.split(',')

p = []

#Create a Markov chain haha
num_states = len(feelingsList)
probability = 1 / (num_states)

tinyp = []
for i in range(0,len(feelingsList)):
    tinyp.append(probability)


for i in range(0,len(feelingsList)):
    p.append(tinyp)
    

mc = MarkovChain(p=p,states=feelingsList)

#Simulate the Markov chain
firstone = random.choice(feelingsList)

sequence = [firstone]

for i in range(1, 3):
    current_state = sequence[-1]
    next_state = mc.next(current_state, seed=random.randint(1, 34))
    print((' ' if i < 10 else '') + f'{i}) {current_state} -> {next_state}')
    sequence.append(next_state)

secondone = sequence[1]
thirdone = sequence[2]


#Return of Gemini!!!!!

prompt = "ok, can you please take 10 of those songs and organize them, if you hear them on order you can feel a story, which start with the feeling of " + firstone + ", then " + secondone + ", and ends with the feeling of " + thirdone +", just give me the list of songs. If you find any sexually explicit, ignore it"
response2 = chat.send_message(prompt)
print(response2.text)

prompt = "please give me a list of the 10 songs titles you selected separated by commas, dont use **"
songsresponse = chat.send_message(prompt)
print(songsresponse.text)
finalSongsList = songsresponse.text.split(',')


prompt = "please give the story a protagonist with a random name and genre, and a secondary character (with a random name) or antagonist"
response2 = chat.send_message(prompt)

prompt = "summarice the story in one sentence of 10 words"
description = chat.send_message(prompt)

prompt = "give the story a short title"
title = chat.send_message(prompt)




 
# Interact with authenticated user
username = sp.current_user()
playlist = sp.user_playlist_create(user=username["id"],name=str(title.text),public=True,description=str(description.text))

resultList = []
#i =finalSongsList[1]
#result = sp.search(q=i,type=tracks,limit=1)

print(finalSongsList)
for i in range(0,len(finalSongsList)):
   result = sp.search(q=finalSongsList[i],type="track",limit=1)
   resultUri = result['tracks']['items'][0]['uri']
   resultName = result['tracks']['items'][0]["name"]
   resultList.append(resultUri)

print(resultList)
print(resultName)

sp.playlist_add_items(playlist["id"], resultList)

