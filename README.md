# spotifyshuffle-1
New shuffle that learns from when songs are skipped (early, middle, late, etc.) and is more likely to play songs that are listened to for longer than songs that are skipped early.
Essentially it learns from what songs you want to listen to right now/are playing on repeat and plays those songs, and is much less likely to play songs you are skipping immediately
Originally used Spotify's REST API, now uses the Spotipy library. 
Can save current playlist data (which songs are more likely to be played in a playlist) to a file and then read that playlist back in, so the program can be stopped, saved, then resumed later.
Also automatically recognizes when a song is about to end and saves that data, i.e. the data of a song being listened to completion. 

# How to Run:
First, download the files. Run the file in /executable/. If asked for a playlist URI, you need to click the three dots on a playlist, then hover on share, then hover on "Copy link to playlist". Don't click it. Hold control on MacBook (I believe command on Windows), wait until it changes to say "Copy Spotify URI", then click and paste in the command line.
If the executable does not run, install Python 3.7. If it still does not run, run these commands (Windows):
py -m pip install datetime
py -m pip install requests
py -m pip install spotipy
py -m pip install wakepy
py -m pip install pickle
