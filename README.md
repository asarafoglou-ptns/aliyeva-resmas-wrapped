# resmaswrapped

This Python package is a year-round version of Spotify wrapped - it allows you to get your top 30 songs from the last month, 6 months, or year. You can also visually compare the audio features of your top songs to the global top 50. This app is for anyone who actively uses Spotify and wants to learn more about their listening habits. If you're too impatient to wait for Spotify Wrapped, this is for you. None of the functions in the package are meant to be called on by the user - you just have to input your Spotify Client ID and Client Secret (details on how to do that below), and my app takes care of the rest!

## Requirements
```python
# requirements should download automatically, but if not, you can also find them in requirements.txt:
spotipy~=2.23.0
streamlit~=1.35.0
faicons
shiny
seaborn
pandas~=2.0.3
plotly~=5.9.0
scikit-learn~=1.3.0
setuptools~=68.0.0
```
## Generating a Client ID and Client Secret
Open this for a really simple tutorial on how to generate your client ID and client secret:
https://developer.spotify.com/documentation/web-api/concepts/apps
When asked for the redirect URI, enter: http://localhost:8888/callback

## Downloading the package
1. In the python terminal, run
```python
pip install git+https://github.com/asarafoglou-ptns/resmaswrapped.git
```
2. Once that is installed, run the following in the terminal, replacing the strings with your actual client ID & secret.
  These commands set your client ID and secret as environment variables.
```python
export SPOTIPY_CLIENT_ID='YOUR CLIENT ID HERE'
export SPOTIPY_CLIENT_SECRET='YOUR CLIENT SECRET HERE'
```

3. In the terminal, run
```python
streamlit run path/to/app/myapp/app.py

# in case you can't find the path, run
pip show myapp
```
4. Allow Spotify authentication and enjoy!

## Flowchart
<img width="699" alt="Screenshot 2024-05-31 at 21 27 28" src="https://github.com/asarafoglou-ptns/resmaswrapped/assets/157810991/c48958aa-3475-47f0-ac03-10a199f42782">

## UI Tutorial
1. Press arrow to display sidebar
   <img width="1470" alt="Screenshot 2024-05-26 at 22 33 49" src="https://github.com/asarafoglou-ptns/resmaswrapped/assets/157810991/7a97eb46-8855-4851-82bd-c4a936ee6f3c">
2. Options in sidebar:
- Choose a page: your top songs or audio features analysis
- Dropdown menu to filter by time period (past month, 6 months, year)
- Slide to increase/decrease number of songs displayed
- Search for a song
     <img width="1469" alt="Screenshot 2024-05-26 at 22 34 20" src="https://github.com/asarafoglou-ptns/resmaswrapped/assets/157810991/e83aadcd-bb9e-4be8-87fd-17effe4d227a">
3. Audio features analysis options:
- Check which audio features you would like displayed on the radar plot
- See your own top 30’s audio features, the global top 50's, or compare both
- Scroll to see what the audio features mean
      <img width="1469" alt="Screenshot 2024-05-31 at 21 26 40" src="https://github.com/asarafoglou-ptns/resmaswrapped/assets/157810991/9d6b0650-29c9-4948-bb11-51a3dfcaa498">





