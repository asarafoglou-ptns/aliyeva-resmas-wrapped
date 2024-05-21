pip install spotipy
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time

SPOTIPY_CLIENT_ID='insert client id'
SPOTIPY_CLIENT_SECRET='insert client secret'
SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
SCOPE = 'user-top-read'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

results = sp.current_user_top_tracks()
top_tracks_short = sp.current_user_top_tracks(limit=10, offset=0, time_range= 'short_term')

def get_track_ids(time_frame):
 track_ids = []
 for song in time_frame['items']:
 track_ids.append(song['id'])
 return track_ids

track_ids = get_track_ids(top_tracks_short)

def get_track_features(id):
 meta = sp.track(id)
 # meta
 name = meta['name']
 album = meta['album']['name']
 artist = meta['album']['artists'][0]['name']
 spotify_url = meta['external_urls']['spotify']
 album_cover = meta['album']['images'][0]['url']
 track_info = [name, album, artist, spotify_url, album_cover]
 return track_info

# loop over track ids
tracks = []
for i in range(len(track_ids)):
 time.sleep(.5)
 track = get_track_features(track_ids[i])
 tracks.append(track)
# create dataset
df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover'])
