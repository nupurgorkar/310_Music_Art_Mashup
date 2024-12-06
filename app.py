import json
#import time

from flask import Flask, request, redirect, render_template, session
import requests
#from urllib.parse import quote
from keys import HARVARD_KEY, Spotify_client_secret, Spotify_client_id

##creating instance of app object
app = Flask(__name__)
app.secret_key = 'xupur'


@app.route('/')
def index():

    client_id = Spotify_client_id
    redirect_uri = 'http://127.0.0.1:5000/callback'
    scope = 'user-read-private user-read-email ugc-image-upload playlist-modify-public playlist-modify-private user-top-read user-read-private'  # Add required scopes

    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
    return redirect(auth_url)



@app.route('/callback')
def callback():
    ##create playlist in user's account with the tracks
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": 'http://127.0.0.1:5000/callback',
        "client_id": Spotify_client_id,
        "client_secret": Spotify_client_secret
    }

    post_request = requests.post('https://accounts.spotify.com/api/token', data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data['access_token']
    # print("Token Exchange Response:", json.dumps(response_data, indent=4))

    if not access_token:
        print("Failed to obtain access token:", response_data)
        return "Failed to authorize with Spotify."

    authorization_header = {'Authorization': f'Bearer {access_token}'}
    genre_map = find_genres(authorization_header)
    painting = random_painting()
    #print(painting.)

    #print(colors_to_genre(artist_genre_map,random_painting()))
    #print(playlist(colors_to_genre(genre_map,random_painting())))
    if painting and painting.get('colors') and painting.get('image_url'):
        color_map = colors_to_genre(genre_map, painting)
        playlist_data = playlist(color_map)
        return render_template('index.html', playlist=playlist_data, painting=painting)

    # If painting lacks required data, inform the user or provide fallback behavior
    return render_template(
        'index.html',
        message="Painting data is incomplete. Could not generate a playlist.",
        painting=painting,
    )

##allows user to click on button to generate a new painting and playlist
@app.route('/new')
def generate_new_painting():
    # Ensure the user is authenticated with Spotify by checking the session for access token
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/')  # If no token, redirect to login page

    authorization_header = {'Authorization': f'Bearer {access_token}'}
    painting = random_painting()

    if not painting:
        return render_template('index.html', message="Failed to fetch a new painting.")

    # Get the artist genre map based on the user's Spotify top tracks
    genre_map = find_genres(authorization_header)

    # if painting has colors, map them to genres and create a playlist
    if painting.get('colors') and painting.get('image_url'):
        color_map = colors_to_genre(genre_map, painting)
        playlist_data = playlist(color_map)
        return render_template('index.html', playlist=playlist_data, painting=painting)

    # If painting lacks required data, inform the user
    return render_template(
        'index.html',
        message="Painting data is incomplete. Could not generate a playlist.",
        painting=painting,
    )
## fetches random painting from a request to harvard art museum API. Returns title, artist, image_url, and colors
def random_painting():
    harvard_url = f"https://api.harvardartmuseums.org/object?apikey={HARVARD_KEY}&classification=Paintings&hasimage=1&size=20&random=20"
    response = requests.get(harvard_url)
    #print(response.json())
    if response.status_code == 200:
        data = response.json()
        if 'records' in data and data['records']:
            # Filter records to find one with both `primaryimageurl` and `colors`
            for painting in data['records']:
                image_url = painting.get('primaryimageurl', '')
                colors = painting.get('colors', [])
                if image_url and colors:
                    return {
                        "title": painting.get('title', 'Unknown Title'),
                        "image_url": image_url,
                        "artist": (painting.get('people') or [{}])[0].get('name', 'Unknown Artist'),
                        "colors": colors,
                    }
        # Return None if no valid painting is found
    return None

##takes parameters of the artist, genre, track dictionary and the random painting
##uses color data from painting to extract hues, and then associates those to an artist's genre
##returns tracks from artist associated with genre, using user's top tracks
def colors_to_genre(artist_genre_map, painting):
    colors = painting.get('colors', [])
    color_to_genre_map = {
        'Red': 'rock',
        'Orange' : 'pop',
        'Yellow': 'rap',
        'Green': 'electronic',
        'Blue': 'r&b',
        'Violet': 'art pop',
        'White': 'classical',
        'Black': 'punk',
        'Grey': 'hip hop',
        'Brown': 'indie pop'
    }

    dominant_hues = [color['hue'] for color in colors]
    # Map of hues to tracks
    hue_to_tracks = {hue: [] for hue in dominant_hues}

    # Assigning tracks to hues based on matching genres
    for artist, data in artist_genre_map.items():
        genres = data['genres']
        tracks = data['tracks']

        ##checks to see if the genre related to hues is in the artist's genres
        ##then checks to see if the tracks are already in the playlist
        for track in tracks:
            for hue in dominant_hues:
                genre = color_to_genre_map.get(hue, '').lower()
                if genre in genres:
                    if genre in genres and f"{track} by {artist}" not in hue_to_tracks[hue]:
                        hue_to_tracks[hue].append(f"{track} by {artist}")
    #print(hue_to_tracks)
    return hue_to_tracks

##generates the user's playlist
def playlist(hue_to_tracks):
    play_list = []
    added_tracks = set()  # Keeps track of unique tracks

    # Add the first track from each hue if it hasn't been added yet
    for hue, tracks in hue_to_tracks.items():
        for track in tracks:
            if track not in added_tracks:
                play_list.append(track)
                added_tracks.add(track)
                if len(play_list) >= 7:
                    return play_list

    return play_list

##spotify authorization and maps artists to genres.
## parameter: the authorization header from the spotify authorization
## mapping the artist, track, and genre because spotify doesn't have api data for the genres of tracks
def find_genres(authorization_header):

    top_tracks_api_endpoint = 'https://api.spotify.com/v1/me/top/tracks?limit=50'
    top_tracks_response = requests.get(top_tracks_api_endpoint, headers=authorization_header)

    if top_tracks_response.status_code != 200:
        return f"Error fetching top tracks: {top_tracks_response.text}"

    top_tracks = json.loads(top_tracks_response.text)
    top_tracks = top_tracks['items']

    artist_genre_map = {}

    for track in top_tracks:
        artist = track['artists'][0]
        artist_name = artist['name']
        artist_id = artist['id']

        # Get artist details (including genres)
        ## in the future, would not use this method of collecting artist data because it makes multiple API calls
        artist_api_url = f'https://api.spotify.com/v1/artists/{artist_id}'
        artist_response = requests.get(artist_api_url, headers=authorization_header)

        if artist_response.status_code == 200:
            artist_data = json.loads(artist_response.text)
            genres = artist_data.get('genres', [])
            artist_genre_map[artist_name] = {'genres': genres, 'tracks': [track['name']]}
        else:
            print(f"Failed to fetch artist info for {artist_name}: {artist_response.text}")

    #print(artist_genre_map)
    return artist_genre_map