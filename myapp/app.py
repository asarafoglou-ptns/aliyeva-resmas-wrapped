import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import plotly.graph_objects as go

# Spotify API credentials
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-top-read'


def authenticate_spotify():
    """
    Authenticates with the Spotify API using OAuth.

    Returns:
        Spotipy client: Authenticated Spotipy client object.
    """
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                     client_secret=SPOTIPY_CLIENT_SECRET,
                                                     redirect_uri=SPOTIPY_REDIRECT_URI,
                                                     scope=SCOPE))


class GetTrack:
    """
    A class with functions that retrieve various information about tracks (track ID, track features, audio features).
    """

    @staticmethod
    def get_track_ids(tracks, is_playlist=False):
        """
        Returns a list of track IDs.

        Args:
            tracks (dict): List of track objects.
            is_playlist (bool): Boolean indicating if the tracks are from a playlist.

        Returns:
            list: A list of track IDs.
        """
        if is_playlist:
            return [track['track']['id'] for track in tracks['items']]
        else:
            return [track['id'] for track in tracks['items']]

    @staticmethod
    def get_track_features(sp, track_ids):
        """
        Retrieves track information for multiple tracks in a batch request.

        Args:
            sp (Spotipy client): Authenticated Spotipy client object.
            track_ids (list): List of track IDs.

        Returns:
            list: List of track features.
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

        Args:
            sp (Spotipy client): Authenticated Spotipy client object.
            track_ids (list): List of track IDs.

        Returns:
            list: List of audio features.
        """
        audio_features = sp.audio_features(track_ids)
        return audio_features

    @staticmethod
    def collect_tracks_data(sp, source, label, is_playlist=False):
        """
        Collects track data (both metadata and audio features) from a specified source.

        Args:
            sp (Spotipy client): Authenticated Spotipy client object.
            source (function): Function to retrieve tracks (e.g., sp.current_user_top_tracks, sp.playlist_tracks).
            label (str): Label indicating the source or time range.
            is_playlist (bool): Boolean indicating if the tracks are from a playlist.

        Returns:
            list: List of combined track data.
        """
        tracks = source()
        track_ids = GetTrack.get_track_ids(tracks, is_playlist)

        track_features = GetTrack.get_track_features(sp, track_ids)
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

# Making 2 dataframes, one with user top tracks and one with the global top 50
columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover', 'danceability', 'energy', 'loudness', 'mode',
           'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_period']
df = pd.DataFrame(user_tracks_data, columns=columns)
df_global_top_50 = pd.DataFrame(global_top_50_data, columns=columns)

# Merges dataframes
df['source'] = 'User'
df_global_top_50['source'] = 'Global Top 50'
df_merged = pd.concat([df, df_global_top_50], ignore_index=True)

# Normalizing audio features so they can be compared
features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
df_merged = normalize_audio_features(df_merged, features)

# More data prep for comparison
comparison_df_user = prepare_comparison_data(df_merged, features, 'User')
comparison_df_global = prepare_comparison_data(df_merged, features, 'Global Top 50')
df_combined = pd.concat([comparison_df_user, comparison_df_global], ignore_index=True)

# Streamlit App - this is the GUI
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# CSS for styling
css = """
* {
    font-family: 'Helvetica', sans-serif !important;
}

.song-info a {
    color: #1DB954 !important;
    text-decoration: none;
}

.song-info a:hover {
    text-decoration: underline;
}

.song-info {
    margin: 5px 0;
    line-height: 1.5;
}
"""
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Navigation
page = st.sidebar.selectbox("Choose a page", ["Your Top Songs", "Audio Features Analysis"])

if page == "Your Top Songs":

    st.title("Your Top Songs")

    # Sidebar
    st.sidebar.title("Filter")
    time_period = st.sidebar.selectbox("Select time period", df['time_period'].unique(), key="time_period")
    num_songs = st.sidebar.slider("Select number of top songs", min_value=1, max_value=30, value=6, key="num_songs")
    search_query = st.sidebar.text_input("Search for a song or artist")

    def get_filtered_df(time_period, num_songs, search_query):
        """
        Filter the DataFrame based on the selected time period, number of top songs, and search query.

        Parameters:
            time_period (str): The time period for which to filter the data.
            num_songs (int): The number of top songs to retrieve.
            search_query (str): The search query to filter the data by song name or artist.

        Returns:
            pandas.DataFrame: A DataFrame containing the filtered top song data.
        """
        filtered_df = df[df['time_period'] == time_period]
        if search_query:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_query, case=False, na=False) |
                filtered_df['artist'].str.contains(search_query, case=False, na=False)
                ]
        return filtered_df.head(num_songs)

    filtered_df = get_filtered_df(time_period, num_songs, search_query)

    image_height = 400

    # Display songs
    for i in range(0, len(filtered_df), 3):
        cols = st.columns(3)
        for col, row in zip(cols, filtered_df.iloc[i:i+3].iterrows()):
            index, song = row
            with col:
                st.markdown(f"""
                    <div class="song-container">
                        <img src="{song['album_cover']}\" class=\"song-image\" width=\"{image_height}\" height=\"{image_height}\">
                        <div>
                            <p class='song-info'><strong>Song:</strong> <a href='{song['spotify_url']}' target='_blank'>
                            {song['name']}</a></p>
                            <p class='song-info'><strong>Artist:</strong> {song['artist']}</p>
                            <p class='song-info'><strong>Album:</strong> {song['album']}</p>
                        </div>
                    </div>
                    <hr class=\"separator\">
                """, unsafe_allow_html=True)

elif page == "Audio Features Analysis":

    st.title("Audio Features Analysis")

    # Sidebar options for selecting features to plot
    st.sidebar.title("Select Audio Features to Plot")
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    selected_features = [feature for feature in features if st.sidebar.checkbox(feature, True)]

    # Select data to display
    data_option = st.radio("Select data to display", ("User's Top Tracks", "Global Top 50", "Both"), horizontal=True)

    # Define colors for "Your Tracks" and "Global Top 50" as pink and blue
    colors = {'User': '#FF69B4', 'Global Top 50': '#1E90FF'}

    if selected_features:
        # Filter the combined dataframe based on the selected features and data option
        if data_option == "Both":
            filtered_combined_df = df_combined[df_combined['feature'].isin(selected_features)]
        elif data_option == "Global Top 50":
            filtered_combined_df = df_combined[
                (df_combined['feature'].isin(selected_features)) & (df_combined['group'] == "Global Top 50")]
        else:
            filtered_combined_df = df_combined[
                (df_combined['feature'].isin(selected_features)) & (df_combined['group'] == "User")]

        # Create radar chart
        fig = go.Figure()

        for group in filtered_combined_df['group'].unique():
            group_df = filtered_combined_df[filtered_combined_df['group'] == group]
            fig.add_trace(go.Scatterpolar(
                r=group_df['value'],
                theta=group_df['feature'],
                fill='toself',
                name=group,
                line=dict(color=colors[group])  # Set color based on group
            ))

        fig.update_layout(
            polar=dict(
                bgcolor='#000000',
                radialaxis=dict(visible=True, range=[0, 1], showline=False, ticks=''),
                angularaxis=dict(visible=True, showline=False, ticks='', tickfont=dict(size=18))
            ),
            showlegend=True,
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#ffffff'),
            height=600,
            width=700,
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        #### What do these audio features mean?
        This radar chart displays the normalized values of selected audio features. The chart compares the average values 
        between "Your Tracks" and the "Global Top 50". The audio features include:
        - **Danceability:** Describes the suitability of a track for dancing based on a combination of musical elements
        - **Energy:** Represents a perceptual measure of intensity and activity
        - **Loudness:** The overall loudness of a track in decibels (dB)
        - **Speechiness:** Indicates the presence of spoken words in a track
        - **Acousticness:** Measures the likelihood of a track being acoustic
        - **Instrumentalness:** Predicts whether a track contains no vocals
        - **Liveness:** Detects the presence of an audience in the recording
        - **Valence:** Describes the musical positiveness of a track
        - **Tempo:** The overall estimated tempo of a track in beats per minute (BPM)
        """)
    else:
        st.write("Please select at least one feature to display the radar chart.")
