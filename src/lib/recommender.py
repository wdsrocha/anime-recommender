from random import choices
from typing import Dict

import numpy as np
import pandas as pd

from src.lib.content_based_recommender import setup_content_based_recommender


class Recommender:
    def __init__(self):
        self.anime_df = pd.read_csv("data/processed_anime.csv")
        (
            self.distances,
            self.indices,
            self.anime_indices,
            self.rev_d,
        ) = setup_content_based_recommender()

    def get_anime_name(self, anime_id):
        # TODO: re-implement this with proper pandas tools
        # TODO: don't handle exception like this...
        try:
            return self.anime_df[self.anime_df["anime_id"] == anime_id].values[0][1]
        except IndexError:
            return "WARNING: Anime not in DB"

    def is_anime_valid(self, anime_id: int) -> bool:
        """Returns true if the anime exists in dataframe, false otherwise"""
        return (self.anime_df["anime_id"] == anime_id).any()

    def recommend_from_top(self) -> int:
        """Recommends based on famous and best rated animes"""
        ok_anime_df = self.anime_df[
            (self.anime_df["members"] > 10 ** 5)
            & (self.anime_df["rating"] > 8.5)
            & (self.anime_df["name"].str.contains("Season") == False)
        ]
        return int(ok_anime_df["anime_id"].sample())

    def recommend(self, anime_list=None) -> int:
        # Anime list must ALWAYS come raw from jikanpy API
        if anime_list is None:
            anime_list = []

        seen_anime_ids = set([anime["mal_id"] for anime in anime_list])

        # ignore every anime that
        # - hasn't been scored by the user
        # - isn't on our csv
        anime_list = [
            anime
            for anime in anime_list
            if anime["score"] and self.is_anime_valid(anime["mal_id"])
        ]

        # good enough recommendations for a cold start
        if anime_list is None:
            return self.recommend_from_top()

        # standardize user scores
        # - now the scores are fair
        # - we know when an anime should't count towards recommendation!
        # possible problem: when the lowest score is a high one (like 8)
        # it will be considered as bad anime. TODO: handle this somehow
        user_scores = np.asarray([anime["score"] for anime in anime_list])
        user_scores = (user_scores - np.mean(user_scores)) / np.std(user_scores)

        freq: Dict[int, float] = {}
        anime_ids = [anime["mal_id"] for anime in anime_list]
        for anime_id, user_score in zip(anime_ids, user_scores):
            df_id = self.rev_d[anime_id]
            for recommended_anime_id in self.anime_indices[df_id][1:]:
                # don't recommend seen animes
                if recommended_anime_id not in seen_anime_ids:
                    if recommended_anime_id in freq:
                        freq[recommended_anime_id] += user_score
                    else:
                        freq[recommended_anime_id] = user_score

        ids, p = [], []
        for key in sorted(freq, key=freq.get, reverse=True)[:10]:
            if freq[key] > 0:
                ids.append(key)
                p.append(freq[key])

        if len(ids) == 0:
            return self.recommend_from_top()

        return choices(ids, weights=p)[0]


if __name__ == "__main__":
    from jikanpy import Jikan

    username = input("MAL username: ")
    print("Fetching data from API...")
    anime_list = Jikan().user(username, "animelist")["anime"]
    print("Executing recommendation algorithms...")
    r = Recommender()
    anime_id = r.recommend(anime_list)
    print()
    print(
        f"Recommendation: {r.get_anime_name(anime_id)}\n"
        f"Link: https://myanimelist.net/anime/{anime_id}"
    )
