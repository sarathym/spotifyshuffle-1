import random
import pickle
import time
from threading import Thread
import requests
import uuid
import vars
import tekore as tk
from datetime import datetime
from collections import deque
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

CLIENT_ID = vars.CLIENT_ID
CLIENT_SECRET = vars.CLIENT_SECRET

oauth = ""
time_since_skip = 0
verbose = False
realplaylist = {}
scope='user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-recently-played playlist-read-private'
# token = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
conf = (CLIENT_ID, CLIENT_SECRET, "http://localhost:8888/callback")
token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)

sp = tk.Spotify(token)
# cache_token = token.get_access_token()
# sp = spotipy.Spotify(cache_token)
# client_credentials = SpotifyClientCredentials(client_id, client_secret)
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8888/callback'))


def savedata(playlist):
    with open('/home/manojksarathy/src/bruh.txt', 'wb') as f:
        pickle.dump(playlist, f)
    jawn = json.dumps(playlist)


def readdata():
    playlistURI = "1AYl34jkt472GoaBVRvWjH"
    print("Getting playlist")
    songs = sp.playlist(playlistURI)
    tmp1 = songs['tracks']['next']
    j = 2
    length = songs['tracks']['total']
    for jawn in songs['tracks']['items']:
        j+=1
        track = jawn['track']
        #              total score, total plays
        if track:
            playlist[track['id']] = [0, 0]

    tmp1 = songs['tracks']['next']
    i = 0
    while tmp1:
        if not i > length:
            print(tmp1)
            #url = "https://api.spotify.com/v1/playlists/" + tmp1
            #response = requests.get(tmp1, headers={"Authorization": "Bearer " + oauth, "Content-Type": "application/json", "Accept": "application/json"})
            songs = sp.playlist_items(playlistURI, offset=len(playlist))
            for jawn in songs['items']:
                #              total score, total plays
                if jawn:
                    playlist[jawn['track']['id']] = [0, 0]

            tmp1 = songs['next']
        i+=1
    # playlist uri - https://open.spotify.com/playlist/1AYl34jkt472GoaBVRvWjH
    # oath - Authorization: Bearer BQCDIWAiSAcYnqufAHR7MaPXajB5fM3Mz2KRRVgbVVYjqNddszxQy7knblQV-d8tFkNS3lFzkIEfodH1xicGwE2KTDrLkZEFRMXhYpmvu8sV3Vgmu1veVuWht5rnnIMkMaH2eJAq1e3RpjfX2NyCM7bf3AcHYkFkXBLeDh9hK1fV0saBql2F1XBrGw
    loop = False
    with open('/home/manojksarathy/src/bruh.txt', 'rb') as f:
        return pickle.load(f)


def trackdata(track_id):
    if track_id:
        url = "https://api.spotify.com/v1/tracks/" + track_id
        #response2 = requests.get(url, headers={"Authorization": "Bearer " +oauth})
        #response = response2.json()
        response = sp.track(track_id)
        if response:
            #   return {"name": response['name'], "album": response['album']['name'],
            #           "artist": response['album']['artists'][0]['name'], "release_date": response['album']['release_date'],
            #           "duration": response['duration_ms']}
            if response.get('album'):
                return {"name": response.get('name'), "album": response.get('album').get('name'),
                        "artist": response['album']['artists'][0]['name'], "release_date": response['album']['release_date'],
                        "duration": response['duration_ms']}

        else:
            return None
    else:
        return None


def selectnextsong(playlist):
    total = 0
    list1 = []
    list2 = []
    dict = {}
    #print(playlist)
    for item in playlist:
        total += playlist[item][0]

    for item in playlist:
        list1.append(item)
        if playlist[item][0] == 0:
            list2.append(0.5)
        else:
            list2.append(playlist[item][0]/total)

    #print(list1)
    #print(list2)
    randList = random.choices(list1, list2)
    recentlyplayed = sp.playback_recently_played()
    retry = True
    while retry:
        retry = False
        for jawn in recentlyplayed['items']:
            if jawn['track']['id'] == randList[0]:
                retry = True
                randList = random.choices(list1, list2)

    return randList


def awaitsongend():
    recently = deque()
    recognized = []
    while True:
        if not sp.playback_currently_playing():
            break
        # id, progress, total duration
        # /Users/sarathym/Documents/spotifyshuffle-1/src/data/bruh.txt
        # spotify:playlist:1AYl34jkt472GoaBVRvWjH
        curr = [sp.playback_currently_playing()['item']['id'], sp.playback_currently_playing()['progress_ms'], sp.playback_currently_playing()['item']['duration_ms']]
        if len(recently) >= 10:
            recently.popleft()

        recently.append(curr)
        time.sleep(3)

        currid = sp.playback_currently_playing()['item']['id']
        if verbose:
            print(str(datetime.now()) + " INFO: When called: " + trackdata(curr[0])['name'] + " Now: " + trackdata(currid)['name'])

        if not currid == curr[0]:
            if curr[0] in realplaylist:
                if verbose:
                    print(str(datetime.now()) + " INFO: Updating data for " + trackdata(curr[0])['name'])

                tmp = realplaylist[curr[0]]
                currscore = curr[1]/curr[2]
                tmp[0] += currscore
                tmp[1] += 1
                realplaylist[curr[0]] = tmp

            nextsong = selectnextsong(realplaylist)[0]
            sp.playback_queue_add(nextsong)

        recognized = checkforskips(recently, recognized)


def checkforskips(recently, recognized):
    recentlyplayed = sp.playback_recently_played(limit=10)
    read = []
    recognized2 = []
    for jawn in recently:
        read.append(jawn[0])

    for jawn in recentlyplayed['items']:
        id = jawn['track']['id']
        recognized2.append(id)
        if id not in read and id not in recognized:
            if verbose:
                print(str(datetime.now()) + " INFO: Skipped: " + id)
            if id in realplaylist:
                tmp = realplaylist[id]
                runtime = jawn['track']['duration_ms']
                tmp[0] += (runtime-1000)/runtime
                tmp[1] += 1
                realplaylist[id] = tmp

    return recognized2


if __name__=="__main__":
    loop = True
    action1 = None
    print("INFO: Starting Program")
    playlistURI = None
    playlistPath = None
    #set_keepawake(keep_screen_awake=False)
    #url = "https://api.spotify.com/v1/me/player/currently-playing"
    #response = requests.get(url, headers={"Authorization": "Bearer BQAPVGy1w3lX9HKB283TOyXMcCLNZ9t5qLNivhDA3xs4nyKwP3TvNnTyiLdWpzlSKPOLPJFhmA983f0WdgPAbXOPC3nH-hUpWrbPpWhdbRYbwCh95uLt0N6YryFgWVR0dGLl0dubyA-JFv37llRMzsjnRdvpLLi919yJgIb3Oatwe4x5BhPZGPVKuFBP"})
    #print(response.json())

    playlist = readdata()
    realplaylist = {}
    for item in playlist:
        if (trackdata(item)):
            realplaylist[item] = playlist[item]
    realplaylist = playlist
    cont = True
    t = Thread(target=awaitsongend)
    t.daemon = True
    t.start()
    while True:
        savedata(realplaylist)
        time.sleep(600)

    #unset_keepawake()
