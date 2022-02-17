# Spotify Song Predictor
Lambda School - DS UNIT 4 Build Week Project

This application predicts which songs are most similar to an user input song title. Using the Spotify API, various features of the song input are analyzed using a k-1 next nearest neighbor analysis of the audio features.

The goal of this project is to provide users with the ability to discover new music according to their favorite songs through the analysis of various features of the songs.

# Build Status
Currently in development.

# Application Link
[Spotify Song Predictor](https://spotify-buildweek-unit3.herokuapp.com/)

# Decription
This application predicts which songs are most similar to an user input song title. Using the Spotify API, various features of the song input are analyzed using a euclidian distance analysis of the audio features.

The goal of this project is to provide users with the ability to discover new music according to their favorite songs through the analysis of various features of the songs.

# Usage

Built with

The languages used for this project include:

* Python
* HTML/CSS
The packages used include:

* Pandas
* Numpy
* Scikit Learn
* Spotipy
* Flask

# Features
The application uses Flask to power the search query/input. From the user input, the song title is passed through Spotipy's search functionality and generates the track_id and audio features. These features are then passed through the predict.py file which uses a K-1 Nearest Neighbors model to predict the songs whose features most closely resemble the input track. The track id's of the recommended songs are brought back through the front end and presented to the User as a list of songs with links to open the songs in Spotify.

#API Reference
[Spotify](https://developer.spotify.com/documentation/web-api/)
Authentication and client credentials are required to access this application. An .env file is with "CLIENT_ID" and "CLIENT_SECRET" variables is required for use.

# Team
* Dan Kositzke (ML Model / Flask App)
* Josiah Coates (Heroku Master)
* Nigel Clinton (Html / CSS)
