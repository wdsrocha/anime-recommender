import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


def setup_content_based_recommender(n_neighbors=6):
    features = pd.read_csv("data/processed_features.csv")
    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm="ball_tree").fit(
        features
    )
    distances, indices = nbrs.kneighbors(features)
    anime = pd.read_csv("data/processed_anime.csv")

    d = dict(zip(anime.index, anime.anime_id))
    anime_indices = np.vectorize(lambda i: d[i])(indices)

    rev_d = dict(zip(anime.anime_id, anime.index))

    return (distances, indices, anime_indices, rev_d)
