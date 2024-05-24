import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

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
        return [song['id'] for song in time_frame['items']]

    @staticmethod
    def get_track_features(sp, track_id):
        """
        Retrieves track information - name of the song, album, artist
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

    @staticmethod
    def get_multiple_track_features(sp, track_ids):
        """
        Retrieves track information for multiple tracks in a batch request.
        """
        tracks_meta = sp.tracks(track_ids)
        track_features = []
        for meta in tracks_meta['tracks']:
            name = meta['name']
            album = meta['album']['name']
            artist = meta['album']['artists'][0]['name']
            spotify_url = meta['external_urls']['spotify']
            album_cover = meta['album']['images'][0]['url']
            track_info = [name, album, artist, spotify_url, album_cover]
            track_features.append(track_info)
        return track_features

def collect_tracks_data(sp, time_ranges):
    all_tracks = []

    for time_period in time_ranges:
        top_tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range=time_period)
        track_ids = GetTrack.get_track_ids(top_tracks)

        # Fetch track features in batch
        track_features = GetTrack.get_multiple_track_features(sp, track_ids)
        for track in track_features:
            track.append(time_period)  # Add the time period as the last element
            all_tracks.append(track)

    return all_tracks


time_ranges = ['short_term', 'medium_term', 'long_term']

# Use our function to get the track data
tracks_data = collect_tracks_data(sp, time_ranges)

# Create a pandas DataFrame with the data
df = pd.DataFrame(tracks_data, columns=['name', 'album', 'artist', 'spotify_url', 'album_cover', 'time_period'])
