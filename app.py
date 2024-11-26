import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
from keys import HARVARD_KEY, Spotify_client_secret, Spoitfy_client_id


##setup
app = Flask(__name__)

@app.route('/')
