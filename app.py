import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
from keys import HARVARD_KEY, Spotify_client_secret, Spoitfy_client_id


##creating instance of app object
app = Flask(__name__)

@app.route('/')
def index():
    auth_url = 'https://accounts.spotify.com/authorize'
    return redirect(auth_url)

@app.route('/callback/q')
def callback():
    # spotify provides auth token
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        ##fix link? not sure
        "redirect_uri": "http://127.0.0.1:5000/callback/q",
        "client_id": Spoitfy_client_id,
        "client_secret": Spotify_client_secret
    }
    ## fix links
    post_request = requests.post('https://accounts.spotify.com/api/token', data=code_payload)
    response_data = json.loads(post_request.text)
    access_token = response_data['access_token']

    ##fetch random painting

    ##determine genre based on painting colors

    ##find the tracks that match the genre

    ##create playlist in user's account with the tracks

## def random_painting

##harvard api url with key
##get request with a response
##create a data variable with json
##get and return title of painting, image url, artists, and colors


## def colors_to_genre

##find dominant color in painting, perhaps using color picker library or just get colors in the harvard museum API
## genre map
## red: rock, blue: pop, yellow: rap, white: classical, black: punk
##return the assocated genre

## def find_spotify_tracks

##spotify header with access token
##get user's top 50 tracks
##filter tracks by genre
## return 5 tracks


## def create_playlist
##painting name as playlist, tracks created earlier as param, and access token

##get user's spotify id
##create spotify playlist
##add tracks to the playlist
##return the playlist url

