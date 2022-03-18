import random
import pickle
import time
from vars import *
from threading import Thread
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

client_id = CLIENT_ID
client_secret = CLIENT_SECRET
oauth = ""
realplaylist = {}
scope='user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-recently-played playlist-read-private'
client_credentials = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8888/callback'))

def savedata(playlist, path=None):
    if not path:
        path = input("Path to write to? ")
    with open(path, 'wb') as f:
        pickle.dump(playlist, f)


def readdata(path):
    with open(path, 'rb') as f:
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


def getoauth():
    bearer = "Basic " + client_id + ":" + client_secret
    """
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    auth_code = requests.get(AUTH_URL, {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': 'http://localhost:8888/callback',
        'scope': 'user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-recently-played playlist-read-private'
    })
    print(sp.currently_playing())
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    with open("/Users/sarathym/Documents/spotifyshuffle-1/src/data/html.html", "w") as f:
        f.write(auth_code.text)

    webbrowser.get(chrome_path).open('file:///Users/sarathym/Documents/spotifyshuffle-1/src/data/html.html')
    """
    # 5tK6wV2Wj3J5hypX7VBixZ
    url = "https://accounts.spotify.com/api/token"
    #response = requests.post(url, headers={"Authorization": bearer, "Content-Type": "x-www-form-urlencoded"}, form={"grant_type": 'client_credentials'})
    response = requests.post(url, {
        'grant_type': 'client_credentials',
        #'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-recently-played playlist-read-private'
    })
    return response.json()['access_token']


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
    recentlyplayed = sp.current_user_recently_played()
    set = {}
    retry = True
    while retry:
        retry = False
        for jawn in recentlyplayed['items']:
            if jawn['track']['id'] == randList[0]:
                retry = True
                randList = random.choices(list1, list2)
    """
    Make it so the random selection isn't a recently played song. 
    endpoint is only returning error code 500 (server error) 
    Will work on it when I can figure out how to not get error code 500
    
    cont = False
    # 1AYl34jkt472GoaBVRvWjH
    url = "https://api.spotify.com/v1/me/player/recently-played"
    while not cont:
        response = requests.get(url, headers={"Authorization": "Bearer " + oauth, "Content-Type": "application/json", "Accept": "application/json"})
        songs = response.json()
        print(response.json())
        for jawn in songs['items']:
            if jawn:
                print(jawn)
    """

    return randList


def awaitsongend():
    while True:
        runtime = sp.currently_playing()['item']['duration_ms']
        curr = sp.currently_playing()['item']['id']
        print(curr)
        if runtime-sp.currently_playing()['progress_ms'] > 5000:
            time.sleep((runtime-sp.currently_playing()['progress_ms']-5000)/1000)
            print("When called: " + curr + " Now: " + sp.currently_playing()['item']['id'])
            if sp.currently_playing()['item']['id'] == curr:
                skip()
        else:
            if sp.currently_playing()['item']['id'] == curr:
                skip()


def awaitsongend2():
    runtime = sp.currently_playing()['item']['duration_ms']
    curr = sp.currently_playing()['item']['id']
    print(curr)
    if runtime-sp.currently_playing()['progress_ms'] > 5000:
        time.sleep((runtime-sp.currently_playing()['progress_ms']-5000)/1000)
        print("When called: " + curr + " Now: " + sp.currently_playing()['item']['id'])
        if sp.currently_playing()['item']['id'] == curr:
            skip()
    else:
        if sp.currently_playing()['item']['id'] == curr:
            skip()


def skip():
    currscore = sp.currently_playing()['progress_ms']/sp.currently_playing()['item']['duration_ms']
    id = sp.currently_playing()['item']['id']
    if id in realplaylist:
        tmp = realplaylist[id]
        #print(tmp)
        tmp[0] += currscore
        tmp[1] += 1

    #print(realplaylist)
    next = selectnextsong(realplaylist)[0]
    sp.add_to_queue(next)
    print(trackdata(next))
    time.sleep(0.5)
    sp.next_track()


if __name__=="__main__":
    loop = True
    playlist = {}
    action1 = None
    playlistURI = None
    playlistPath = None

    #oauth = getoauth()
    #print(oauth)

    while loop:
        action1 = input("(C)reate new playlist or (R)ead playlist from file? ")
        if action1.lower() == "c":
            playlistURI = input("Playlist URI? ")
            url = "https://api.spotify.com/v1/playlists/" + playlistURI
            #response = requests.get(url, headers={"Authorization": "Bearer " + oauth, "Content-Type": "application/json", "Accept": "application/json"})
            #response = sp.playlist(playlistURI)
            #songs = response.json()
            songs = sp.playlist(playlistURI)
            tmp1 = songs['tracks']['next']
            length = songs['tracks']['total']
            for jawn in songs['tracks']['items']:
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
        elif action1.lower() == "r":
            playlistPath = input("Playlist path? ")
            #playlistPath = '/Users/sarathym/Documents/spotifyshuffle-1/src/data/save.txt'
            playlist = readdata(playlistPath)
            loop = False
        else:
            print("Unrecognized input!")

    realplaylist = {}
    for item in playlist:
        if (trackdata(item)):
            realplaylist[item] = playlist[item]

    #print(playlist)
    #print(realplaylist)
    action1 = action1.lower()
    #print("random selections: ")
    #print(trackdata(selectnextsong(realplaylist)[0]))
    cont = True
    t = Thread(target=awaitsongend)
    t.daemon = True
    t.start()
    while cont:
        t2 = Thread(target=awaitsongend2)
        t2.daemon = True
        t2.start()
        inp = input("(S)kip song, Sa(v)e data, (P)rint data, (Q)uit: ")
        inp = inp.lower()
        if inp == "s":
            # 5tK6wV2Wj3J5hypX7VBixZ
            url = "https://api.spotify.com/v1/me/player/currently-playing"
            #response = requests.get(url, headers={"Authorization": "Bearer " + oauth, "Content-Type": "application/json", "Accept": "application/json"})
            skip()
        elif inp == "v":
            path = "/Users/sarathym/Documents/spotifyshuffle-1/src/data/save.txt"
            savedata(realplaylist)
        elif inp == "q":
            cont = False
        elif inp == "p":
            print(realplaylist)
        else:
            print("Input not recognized!")
