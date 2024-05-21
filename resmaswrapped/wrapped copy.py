import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time

# my spotify API credentials
SPOTIPY_CLIENT_ID = '4e6464520c2b4cf3a90ad792e5ad6504'
SPOTIPY_CLIENT_SECRET = '4dde9d4fbb604ad3b22c0ad7204e25a0'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-top-read'

# authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

# get the top tracks
top_tracks_short = sp.current_user_top_tracks(limit=10, offset=0, time_range='short_term')


class GetTrack:
    """
 A class with functions that retrieve various information about tracks (for now: ID and features).
 """

    @staticmethod
    def get_track_ids(time_frame):
        """
  Returns a list of track IDs.

  :param time_frame: short, medium, and long-term listening habits
  :type time_frame: dict
  :return: A list of track IDs
  """
        track_ids = []
        for song in time_frame['items']:
            track_ids.append(song['id'])
        return track_ids

    @staticmethod
    def get_track_features(sp, track_id):
        """
  Retrieves track information - name of the song, album, artist, spotify url, and album cover.
  """
        meta = sp.track(track_id)
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        spotify_url = meta['external_urls']['spotify']
        album_cover = meta['album']['images'][0]['url']
        track_info = [name, album, artist, spotify_url, album_cover]
        return track_info


# get the track IDs
track_ids = GetTrack.get_track_ids(top_tracks_short)

# Loop over track IDs to get track features
tracks = []
for track_id in track_ids:
    time.sleep(0.5)  # Sleep to respect rate limits
    track = GetTrack.get_track_features(sp, track_id)
    tracks.append(track)

# Create a DataFrame with the track information
df = pd.DataFrame(tracks, columns=['name', 'album', 'artist', 'spotify_url', 'album_cover'])

# Print the DataFrame
print(df)
