import base64
import requests
import datetime
from urllib.parse import urlencode
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

spotify_api_key = os.getenv("SPOTIFY_API_KEY")
spotify_api_key_secret = os.getenv("SPOTIFY_API_KEY_SECRET")


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data["access_token"]
        expires_in = data["expires_in"]
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        return headers

    def get_resource(self, lookup_id, resource_type="albums", version="v1"):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def base_search(self, query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        resp = requests.get(lookup_url, headers=headers)
        if resp.status_code not in range(200, 299):
            return {}
        return resp.json()

    def search(
        self, query=None, operator=None, operator_query=None, search_type="artist"
    ):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)


def get_id_and_year(song_name, artist_name):
    """
    Example:

    song_id, song_year = get_id_and_year('margaritaville','jimmy buffett')

    print("Song ID is:", song_id)
    print("Release year is:", song_year)

    Output:
    Song ID is: 4EEjMyQub6tgFVshlM9j1M
    Release year is: 1987

    """

    spotify = SpotifyAPI(spotify_api_key, spotify_api_key_secret)
    token = spotify.get_access_token()
    if token == None:
        return "Failed to get Spotify token"

    try:
        song_data = spotify.search(
            {"track": song_name, "artist": artist_name}, search_type="track"
        )
        song_id = song_data["tracks"]["items"][0]["id"]
        release_date = song_data["tracks"]["items"][0]["album"]["release_date"]
        format = "%Y-%m-%d"
        song_year = datetime.datetime.strptime(release_date, format).year
    except:
        return "There was an error finding your song. Please enter another song."

    return song_id, song_year


def retrieve_audio_features(spotify_id):
    """
    Example:

    retrieve_audio_features('4EEjMyQub6tgFVshlM9j1M')

    returns a python dict
    [{'danceability': 0.611,
    'energy': 0.578,
    'key': 1,
    'loudness': -14.171,
    'mode': 1,
    'speechiness': 0.0676,
    'acousticness': 0.0598,
    'instrumentalness': 0.0219,
    'liveness': 0.0983,
    'valence': 0.884,
    'tempo': 100.625,
    'type': 'audio_features',
    'id': '4N0TP4Rmj6QQezWV88ARNJ',
    'uri': 'spotify:track:4N0TP4Rmj6QQezWV88ARNJ',
    'track_href': 'https://api.spotify.com/v1/tracks/4N0TP4Rmj6QQezWV88ARNJ',
    'analysis_url': 'https://api.spotify.com/v1/audio-analysis/4N0TP4Rmj6QQezWV88ARNJ',
    'duration_ms': 266133,
    'time_signature': 4}]

    """

    auth_manager = SpotifyClientCredentials(spotify_api_key, spotify_api_key_secret)
    spotipy_instance = spotipy.Spotify(auth_manager=auth_manager)

    audio_features = spotipy_instance.audio_features(tracks=[spotify_id])
    return audio_features
