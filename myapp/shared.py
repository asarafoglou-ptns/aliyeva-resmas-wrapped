import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Spotify API credentials - you can use mine for testing, these data are not sensitive and can be refreshed if needed
SPOTIPY_CLIENT_ID = '4e6464520c2b4cf3a90ad792e5ad6504'
SPOTIPY_CLIENT_SECRET = '4dde9d4fbb604ad3b22c0ad7204e25a0'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-top-read'


# authentication
def authenticate_spotify():
    """
    Authenticate with the Spotify API using OAuth.

    Returns:
        Spotipy client: Authenticated Spotipy client object.
    """
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                     client_secret=SPOTIPY_CLIENT_SECRET,
                                                     redirect_uri=SPOTIPY_REDIRECT_URI,
                                                     scope=SCOPE))


# Data Retrieval Functions
class GetTrack:
    """
    A class with functions that retrieve various information about tracks (track ID, track features, audio features).
    """

    @staticmethod
    def get_track_ids(tracks, is_playlist=False):
        """
        Returns a list of track IDs.

        :param tracks: List of track objects
        :type tracks: dict
        :param is_playlist: Boolean indicating if the tracks are from a playlist
        :type is_playlist: bool
        :return: A list of track IDs
        """
        if is_playlist:
            return [track['track']['id'] for track in tracks['items']]
        else:
            return [track['id'] for track in tracks['items']]

    @staticmethod
    def get_track_features(sp, track_ids):
        """
        Retrieves track information for multiple tracks in a batch request.
        """
        tracks_meta = sp.tracks(track_ids)
        track_features = [
            [
                meta['name'],
                meta['album']['name'],
                meta['album']['artists'][0]['name'],
                meta['external_urls']['spotify'],
                meta['album']['images'][0]['url']
            ]
            for meta in tracks_meta['tracks']
        ]
        return track_features

    @staticmethod
    def get_audio_features(sp, track_ids):
        """
        Retrieves audio features for multiple tracks in a batch request.
        """
        audio_features = sp.audio_features(track_ids)
        return audio_features

    @staticmethod
    def collect_tracks_data(sp, source, label, is_playlist=False):
        """
        Collects track data (both metadata and audio features) from a specified source.

        :param sp: Spotipy client
        :param source: Function to retrieve tracks (e.g., sp.current_user_top_tracks, sp.playlist_tracks)
        :param label: Label indicating the source or time range
        :return: List of combined track data
        """
        tracks = source()
        track_ids = GetTrack.get_track_ids(tracks, is_playlist)

        # Fetch track features in batch
        track_features = GetTrack.get_track_features(sp, track_ids)

        # Fetch audio features in batch
        audio_features = GetTrack.get_audio_features(sp, track_ids)

        all_tracks = [
            track + [
                audio_feature['danceability'],
                audio_feature['energy'],
                audio_feature['loudness'],
                audio_feature['mode'],
                audio_feature['speechiness'],
                audio_feature['acousticness'],
                audio_feature['instrumentalness'],
                audio_feature['liveness'],
                audio_feature['valence'],
                audio_feature['tempo'],
                audio_feature['duration_ms'],
                label
            ]
            for track, audio_feature in zip(track_features, audio_features)
        ]

        return all_tracks


# Data Processing Functions
def normalize_audio_features(df, features):
    """
    Normalize audio features for comparison.

    Args:
        df (DataFrame): DataFrame containing audio features.
        features (list): List of audio features to normalize.

    Returns:
        DataFrame: DataFrame with normalized audio features.
    """
    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])
    return df


def prepare_comparison_data(df, features, label):
    """
    Prepare comparison data for analysis.

    Args:
        df (DataFrame): DataFrame containing track data.
        features (list): List of features to include in the comparison.
        label (str): Label indicating the source or time range.

    Returns:
        DataFrame: DataFrame with prepared comparison data.
    """
    comparison_data = df[df['source'] == label][features].mean().reset_index()
    comparison_data.columns = ['feature', 'value']
    comparison_data['group'] = label
    return comparison_data


# Data Retrieval
sp = authenticate_spotify()

# Data Retrieval - User's Top Tracks
time_ranges = {
    'short_term': 'Past month',
    'medium_term': 'Past 6 months',
    'long_term': 'Past year'
}

user_tracks_data = [
    track for time_range, label in time_ranges.items()
    for track in GetTrack.collect_tracks_data(sp, lambda tr=time_range: sp.current_user_top_tracks(limit=30, offset=0, time_range=tr), label)
]

# Data Retrieval - Global Top 50 Tracks
global_top_50_data = GetTrack.collect_tracks_data(
    sp, lambda: sp.playlist_items('37i9dQZEVXbMDoHDwVN2tF', limit=50, offset=0), 'Global Top 50', is_playlist=True)

# DataFrame Creation
columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover', 'danceability', 'energy', 'loudness', 'mode',
           'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_period']
df = pd.DataFrame(user_tracks_data, columns=columns)
df_global_top_50 = pd.DataFrame(global_top_50_data, columns=columns)

# Adding Source Column
df['source'] = 'User'
df_global_top_50['source'] = 'Global Top 50'

# Merging DataFrames
df_merged = pd.concat([df, df_global_top_50], ignore_index=True)

# Normalizing Audio Features
features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
df_merged = normalize_audio_features(df_merged, features)

# Data Preparation for Comparison
comparison_df_user = prepare_comparison_data(df_merged, features, 'User')
comparison_df_global = prepare_comparison_data(df_merged, features, 'Global Top 50')
df_combined = pd.concat([comparison_df_user, comparison_df_global], ignore_index=True)

