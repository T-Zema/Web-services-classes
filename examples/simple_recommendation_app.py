from flask import Flask, jsonify, make_response, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yaml
import os

app = Flask(__name__)

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    config_path = os.path.join(base_dir, 'config.yaml')
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file 'config.yaml' was not found in {base_dir}. Please check the file location.")
        exit(1) 

config = load_config()

# Spotify client initialization using credentials from the YAML file
auth_manager = SpotifyClientCredentials(
    client_id=config['spotify']['CLIENT_ID'], 
    client_secret=config['spotify']['CLIENT_SECRET']
)
sp = spotipy.Spotify(auth_manager=auth_manager)

@app.route('/get_music_recommendations')
def get_music_data():
    # Retrieve seed_artists from the query parameters, allow multiple values
    seed_artists = request.args.getlist('seed_artists')  # Returns a list of items for 'seed_artists' parameter
    seed_tracks = request.args.getlist('seed_tracks')
    # Handle cases where no seed_artists are provided
    if not seed_artists:
        return make_response(jsonify({'error': 'No seed artists provided'}), 400)  # HTTP 400 Bad Request

    try:
        rr = sp.recommendations(seed_artists=seed_artists, seed_tracks=seed_tracks, seed_genres=[], limit=10)
        
        songs_list = [song['name'] for song in rr['tracks']]
        artist_list = [artist['album']['artists'][0]['name'] for artist in rr['tracks']]
        pairs = list(zip(artist_list, songs_list))

        first_track = rr['tracks'][0]
        response_data = {
            'Artist_track_pairs': pairs,
            'first_track_album_art': first_track['album']['images'][0]['url'],
            'first_track_album_name': first_track['album']['name'],
            'first_track_artist_name': first_track['album']['artists'][0]['name']
        }

        return make_response(jsonify(response_data), 200)  # HTTP 200 OK
    except Exception as e:
        return make_response(jsonify({'error': 'Failed to retrieve data', 'details': str(e)}), 500)  # HTTP 500 Internal Server Error

if __name__ == '__main__':
    app.run(debug=True)
