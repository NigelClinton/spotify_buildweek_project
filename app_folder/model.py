import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def euclidian_distance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    dist = np.linalg.norm(point1 - point2)
    return dist


def find_recommendations(user_song_features, song_id):

    # Read in spotify data from csv
    spotify_df = pd.read_csv(
        "https://raw.githubusercontent.com/dankositzke/spotify-song-recommender/heroku-deployment/app_folder/assets/spotify_songs_dataset.csv",
        sep=",",
    )

    # Remove input song from df so we do not recommend the input song back to the user
    if song_id in spotify_df["id"].values:
        i = spotify_df[spotify_df["id"] == song_id].index
        spotify_df = spotify_df.drop(i)

    # Filter df for songs with release year equal to user input
    df = spotify_df[spotify_df["year"] == user_song_features[-1]]

    # If less than 100 songs with matching year, add more songs
    song_year = user_song_features[-1]
    song_year_list = [song_year]
    while len(df) < 100:
        song_year += 1
        song_year_list.append(song_year)
        df = spotify_df[spotify_df["year"].isin(song_year_list)]

    # Sample 100 random songs from that year
    df = df.sample(100).reset_index()

    # Normalize numerical audio features
    scaler = MinMaxScaler()
    df_normalized = scaler.fit_transform(
        df[
            [
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
                "duration_ms",
                "time_signature",
            ]
        ]
    )

    # Convert user_song_features to df for MinMaxScaler
    user_song_features_df = pd.DataFrame(
        [user_song_features[:-1]],
        columns=[
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "duration_ms",
            "time_signature",
        ],
    )

    # Compute euclidian distance as a similarity metric, find 10 most similar songs
    input_song_normalized = scaler.transform(user_song_features_df)
    df["euc_dist"] = ""
    for i, features in enumerate(df_normalized):
        df.at[i, "euc_dist"] = euclidian_distance(input_song_normalized, features)
    top_ten = df.sort_values(by=["euc_dist"]).head(10)

    song_list = list(top_ten["name"])
    artist_list = list(top_ten["artists"])
    album_list = list(top_ten["album"])

    # Remove brackets from artist_list elements
    for i, artist in enumerate(artist_list):
        artist_list[i] = artist.replace("[", "").replace("]", "").replace("'", "")

    recommendations = list(zip(song_list, artist_list, album_list))

    return recommendations
