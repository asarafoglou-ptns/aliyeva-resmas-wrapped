import streamlit as st
import plotly.graph_objects as go
from shared import df, df_combined  # import the DataFrames from shared.py

# page layout, reminder: must be the first st. command in script
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# some css here for styling
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

# navigation
page = st.sidebar.selectbox("Choose a page", ["Your Top Songs", "Audio Features Analysis"])

if page == "Your Top Songs":

    st.title("Your Top Songs")

    # sidebar
    st.sidebar.title("Filter")
    time_period = st.sidebar.selectbox("Select time period", df['time_period'].unique(), key="time_period")
    num_songs = st.sidebar.slider("Select number of top songs", min_value=1, max_value=30, value=6, key="num_songs")
    search_query = st.sidebar.text_input("Search for a song or artist")

    def get_filtered_df(time_period, num_songs, search_query):
        filtered_df = df[df['time_period'] == time_period]
        if search_query:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_query, case=False, na=False) |
                filtered_df['artist'].str.contains(search_query, case=False, na=False)
            ]
        return filtered_df.head(num_songs)

    # filters the dataframe based on the selected time period, number of top songs, and search query
    filtered_df = get_filtered_df(time_period, num_songs, search_query)

    image_height = 400

    # displays the songs in a vertical list with large images
    for i in range(0, len(filtered_df), 3):
        cols = st.columns(3)
        for col, row in zip(cols, filtered_df.iloc[i:i+3].iterrows()):
            index, song = row
            with col:
                st.markdown(f"""
                    <div class="song-container">
                        <img src="{song['album_cover']}" class="song-image" width="{image_height}" height="{image_height}">
                        <div>
                            <p class='song-info'><strong>Song:</strong> <a href='{song['spotify_url']}' target='_blank'>
                            {song['name']}</a></p>
                            <p class='song-info'><strong>Artist:</strong> {song['artist']}</p>
                            <p class='song-info'><strong>Album:</strong> {song['album']}</p>
                        </div>
                    </div>
                    <hr class="separator">
                """, unsafe_allow_html=True)

elif page == "Audio Features Analysis":
    st.title("Audio Features Analysis")

    # Sidebar options for selecting features to plot
    st.sidebar.title("Select Features for Radar Chart")
    features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    selected_features = [feature for feature in features if st.sidebar.checkbox(feature, True)]

    # selects data to display
    data_option = st.radio("Select data to display", ("User's Top Tracks", "Global Top 50", "Both"), horizontal=True)

    if selected_features:
        # Filter the combined DataFrame based on the selected features and data option
        if data_option == "Both":
            filtered_combined_df = df_combined[df_combined['feature'].isin(selected_features)]
        elif data_option == "Global Top 50":
            filtered_combined_df = df_combined[(df_combined['feature'].isin(selected_features)) & (df_combined['group'] == "Global Top 50")]
        else:
            filtered_combined_df = df_combined[(df_combined['feature'].isin(selected_features)) & (df_combined['group'] == "User")]


        custom_colors = ['#FF6347', '#32CD32', '#1E90FF']

        # creates radar chart
        fig = go.Figure()

        for idx, group in enumerate(filtered_combined_df['group'].unique()):
            group_df = filtered_combined_df[filtered_combined_df['group'] == group]
            fig.add_trace(go.Scatterpolar(
                r=group_df['value'],
                theta=group_df['feature'],
                fill='toself',
                name=group,
                line=dict(color=custom_colors[idx % len(custom_colors)])
            ))

        fig.update_layout(
            polar=dict(
                bgcolor='#000000',
                radialaxis=dict(visible=True, range=[0, 1], showline=False, ticks=''),
                angularaxis=dict(visible=True, showline=False, ticks='')
            ),
            showlegend=True,
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#ffffff'),
            height=700,
            width=700
        )

        st.subheader("Radar Chart of Selected Features (Normalized)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Please select at least one feature to display the radar chart.")
