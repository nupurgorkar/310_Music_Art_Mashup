import json


from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
from keys import HARVARD_KEY, Spotify_client_secret, Spotify_client_id

##creating instance of app object
app = Flask(__name__)

@app.route('/')
def index():

    client_id = Spotify_client_id
    redirect_uri = 'http://127.0.0.1:5000/callback'
    scope = 'user-read-private user-read-email ugc-image-upload playlist-modify-public playlist-modify-private user-top-read user-read-private'  # Add required scopes

    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # spotify provides auth token
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
    #print("Token Exchange Response:", json.dumps(response_data, indent=4))

    if not access_token:
        print("Failed to obtain access token:", response_data)
        return "Failed to authorize with Spotify."

    authorization_header = {'Authorization': f'Bearer {access_token}'}
    top_tracks_api_endpoint = 'https://api.spotify.com/v1/me/top/tracks?limit=50'


    top_tracks_response = requests.get(top_tracks_api_endpoint, headers=authorization_header)

    if top_tracks_response.status_code != 200:
        return f"Error fetching top tracks: {top_tracks_response.text}"

    top_tracks = json.loads(top_tracks_response.text)
    top_tracks = top_tracks['items']
    artists = []
    artist_genre_map = {}

    for track in top_tracks:
        #artists.append(track['artists'][0]['name'])
        artist = track['artists'][0]
        artist_name = artist['name']
        artist_id = artist['id']

        # Get artist details (including genres)
        artist_api_url = f'https://api.spotify.com/v1/artists/{artist_id}'
        artist_response = requests.get(artist_api_url, headers=authorization_header)

        if artist_response.status_code == 200:
            artist_data = json.loads(artist_response.text)
            genres = artist_data.get('genres', [])
            artist_genre_map[artist_name] = {'genres': genres, 'tracks': [track['name']]}
        else:
            print(f"Failed to fetch artist info for {artist_name}: {artist_response.text}")

    print(colors_to_genre(artist_genre_map,random_painting()))
    print(playlist(colors_to_genre(artist_genre_map,random_painting())))
    return render_template('index.html', sorted_array=artist_genre_map, painting = random_painting())
    ##fetch random painting
    ##determine genre based on painting colors

    ##find the tracks that match the genre

    ##create playlist in user's account with the tracks

    ##render html template

## fetches random painting from a request to harvard art museum API. Returns title, artist, image_url, and colors
def random_painting():
    harvard_url = f"https://api.harvardartmuseums.org/object?apikey={HARVARD_KEY}&classification=Paintings&hasimage=1&size=1&random=1"
    response = requests.get(harvard_url)

    if response.status_code == 200:
        painting = response.json().get('records', [])[0]
        return {
                "title": painting.get('title', 'Unknown Title'),
                "image_url": painting.get('primaryimageurl', ''),
                "artist": painting.get('people', [{}])[0].get('name', 'Unknown Artist'),
                "colors": painting.get('colors', [])
        }
    return None

def colors_to_genre(artist_genre_map, painting):
    colors = painting.get('colors', [])
    color_to_genre_map = {
        'Red': 'Rock',
        'Orange' : 'Pop',
        'Violet': 'Dance Pop',
        'Blue': 'R&b',
        'Yellow': 'Rap',
        'White': 'Classical',
        'Black': 'Punk',
        'Green': 'Techno',
        'Grey': 'Hip Hop'
    }

    # Extract dominant hues
    dominant_hues = [color['hue'] for color in colors]

    # Create a map of hues to genres
    hue_to_tracks = {hue: [] for hue in dominant_hues}

    # Assign tracks to hues based on matching genres
    for artist, data in artist_genre_map.items():
        genres = data['genres']
        tracks = data['tracks']

        for track in tracks:
        # Assume each track contains genre information

            for hue in dominant_hues:
                genre = color_to_genre_map.get(hue, '').lower()
                if genre and any(genre in g.lower() for g in genres):
                    hue_to_tracks[hue].append(f"{track} by {artist}")

    return hue_to_tracks

def playlist(hue_to_tracks):
    play_list = []
    for hue, tracks in hue_to_tracks.items():
        if tracks:
            track = tracks[0]
            play_list.append(track)

    return play_list

def find_genres(access_token):
    pass
##spotify header with access token
##get user's top 50 tracks
##filter tracks by genre
## return 5 tracks to put in playlist

