import pandas as pd
from sklearn.preprocessing import MaxAbsScaler


def main() -> None:
    anime = pd.read_csv("data/raw_anime.csv")

    anime = anime[anime["type"] == "TV"]
    anime = anime.drop(["type", "episodes"], 1)
    anime["rating"] = anime["rating"].astype(float)
    anime["rating"] = anime["rating"].fillna(anime["rating"].median())
    anime["members"] = anime["members"].astype(float)
    anime = anime.reset_index(drop=True)
    anime.to_csv("data/processed_anime.csv", index=False)

    features = pd.concat(
        [
            anime["genre"].str.get_dummies(sep=", "),
            anime[["rating"]],
            anime[["members"]],
        ],
        axis=1,
    )

    max_abs_scaler = MaxAbsScaler()
    features = max_abs_scaler.fit_transform(features)
    pd.DataFrame(features).to_csv("data/processed_features.csv", index=False)


if __name__ == "__main__":
    main()
