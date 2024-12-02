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
    scope = 'user-read-private user-read-email ugc-image-upload playlist-modify-public user-top-read'  # Add required scopes

    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # spotify provides auth token
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        ##fix link? not sure
        "redirect_uri": 'http://127.0.0.1:5000/callback',
        "client_id": Spotify_client_id,
        "client_secret": Spotify_client_secret
    }
    ## fix links
    post_request = requests.post('https://accounts.spotify.com/api/token', data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data['access_token']

    authorization_header = { 'Authorization': 'Bearer ' + access_token }
    top_tracks_api_endpoint = 'https://api.spotify.com/v1/me/top-tracks?limit=20?'

    top_tracks_response = requests.get(top_tracks_api_endpoint, headers=authorization_header)
    print(top_tracks_response)
    #top_tracks = top_tracks_response.json().text


    return render_template("index.html")
    ##fetch random painting

    ##determine genre based on painting colors

    ##find the tracks that match the genre

    ##create playlist in user's account with the tracks

    ##render html template

def random_painting():
    harvard_url = f"https://api.harvardartmuseums.org/object?apikey={HARVARD_KEY}&classification=Paintings&hasimage=1&size=1&random=1"

    pass
##harvard api url with key
##get request with a response
##create a data variable with json
##get and return title of painting, image url, artists, and colors
##create a variable called colors to return


def colors_to_genre(colors):
    pass

##find dominant color in painting, perhaps using color picker library or just get colors in the harvard museum API
## genre map
## red: rock, blue: pop, yellow: rap, white: classical, black: punk
##return the assocated genre

##genre is returned in last function
def find_spotify_tracks(access_token, genre):
    pass
##spotify header with access token
##get user's top 50 tracks
##filter tracks by genre
## return 5 tracks to put in playlist


def create_playlist(access_token, title, tracks):
    pass
##painting name as playlist, tracks created earlier as param, and access token

##get user's spotify id
##create spotify playlist
##add tracks to the playlist
##return the playlist url

