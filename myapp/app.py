import streamlit as st
from shared import df
import os

# Page layout, reminder: must be the first st. command in script
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# create relative path to styles.css file
css_path = os.path.join(os.getcwd(), 'static', 'styles.css')

with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# page title
st.title("Your Top Songs")

# create a sidebar to select time period and number of albums
st.sidebar.markdown("""
    <style>
    * {
        font-family: 'Helvetica', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("Filter")
time_period = st.sidebar.selectbox("Select time period", df['time_period'].unique(), key="time_period")
num_songs = st.sidebar.slider("Select number of top songs", min_value=1, max_value=20, value=6, key="num_songs")

def get_filtered_df(time_period, num_songs):
    return df[df['time_period'] == time_period].head(num_songs)


# filter the DataFrame based on the selected time period and number of top songs
filtered_df = get_filtered_df(time_period, num_songs)

image_height = 400

# Display the songs in a vertical list with larger images
for i in range(0, len(filtered_df), 3):
    cols = st.columns(3)
    for col, row in zip(cols, filtered_df.iloc[i:i+3].iterrows()):
        index, song = row
        with col:
            st.markdown(f"""
                <div class="song-container">
                    <img src="{song['album_cover']}" class="song-image" width="{image_height}" height="{image_height}">
                    <div>
                        <p class='song-info'><strong>Song:</strong> <a href='{song['spotify_url']}' target='_blank'>{song['name']}</a></p>
                        <p class='song-info'><strong>Artist:</strong> {song['artist']}</p>
                        <p class='song-info'><strong>Album:</strong> {song['album']}</p>
                    </div>
                </div>
                <hr class="separator">
            """, unsafe_allow_html=True)
