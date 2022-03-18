# spotifyshuffle-1
New shuffle that learns from when songs are skipped (early, middle, late, etc.) and is more likely to play songs that are listened to for longer than songs that are skipped early.
Essentially it learns from what songs you want to listen to right now/are playing on repeat and plays those songs, and is much less likely to play songs you are skipping immediately
Originally used Spotify's REST API, now uses the Spotipy library. 
Can save current playlist data (which songs are more likely to be played in a playlist) to a file and then read that playlist back in, so the program can be stopped, saved, then resumed later.
Also automatically recognizes when a song is about to end and saves that data, i.e. the data of a song being listened to completion. 
