"""
collaborative.py
-----------------
Recommandation "les gens qui notent comme vous ont aimé ça" en se basant
uniquement sur la matrice utilisateurs x films (aucune métadonnée de film).

Étapes :
  1. Construire la matrice utilisateurs x films à partir des notes connues
     (les cases non notées restent vides).
  2. Centrer chaque ligne sur la moyenne de l'utilisateur (un utilisateur
     sévère qui met 3/5 à son film préféré doit être comparable à un
     utilisateur généreux qui met 5/5 au même film).
  3. Factoriser la matrice centrée avec TruncatedSVD : on la résume en
     quelques "facteurs latents" (des axes de goût qu'on ne nomme pas à la
     main, l'algorithme les découvre depuis les données).
  4. Reconstruire une matrice complète (y compris les cases vides) à partir
     de ces facteurs -> ce sont les notes prédites.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD

from data import MOVIES, RATINGS


def build_rating_matrix(ratings: pd.DataFrame = RATINGS) -> pd.DataFrame:
    """Matrice utilisateurs (lignes) x films (colonnes), NaN si pas noté."""
    return ratings.pivot_table(index="user_id", columns="movie_id", values="rating")


def fit_svd_predictions(ratings: pd.DataFrame = RATINGS, n_factors: int = 4) -> pd.DataFrame:
    """
    Retourne une matrice utilisateurs x films des notes PRÉDITES
    (y compris pour les cases initialement vides).
    """
    matrix = build_rating_matrix(ratings)

    user_means = matrix.mean(axis=1)
    centered = matrix.sub(user_means, axis=0).fillna(0)

    n_factors = min(n_factors, min(centered.shape) - 1)
    svd = TruncatedSVD(n_components=n_factors, random_state=42)
    latent_users = svd.fit_transform(centered)          # utilisateurs -> facteurs latents
    reconstructed = latent_users @ svd.components_        # facteurs latents -> films

    predicted = pd.DataFrame(reconstructed, index=matrix.index, columns=matrix.columns)
    predicted = predicted.add(user_means, axis=0)
    return predicted.clip(1, 5)


PREDICTED_RATINGS = fit_svd_predictions()


def collaborative_recommend(user_id: int, n: int = 5) -> pd.DataFrame:
    """Films non notés par l'utilisateur, triés par note prédite décroissante."""
    matrix = build_rating_matrix()
    if user_id not in matrix.index:
        raise ValueError(f"Utilisateur inconnu : {user_id}")

    already_rated = matrix.loc[user_id].dropna().index
    preds = PREDICTED_RATINGS.loc[user_id].drop(index=already_rated)
    top = preds.sort_values(ascending=False).head(n).reset_index()
    top.columns = ["movie_id", "predicted_rating"]
    top = top.merge(MOVIES[["movie_id", "title"]], on="movie_id")
    return top[["title", "predicted_rating"]]


def evaluate_rmse(ratings: pd.DataFrame = RATINGS, test_ratio: float = 0.2, seed: int = 0) -> float:
    """
    Évalue la qualité des prédictions : on cache volontairement 20% des
    notes connues, on prédit sur le reste, puis on compare prédiction vs
    vraie note cachée (RMSE = erreur quadratique moyenne, plus bas = mieux).
    """
    rng = np.random.default_rng(seed)
    shuffled = ratings.sample(frac=1, random_state=seed).reset_index(drop=True)
    cutoff = int(len(shuffled) * (1 - test_ratio))
    train, test = shuffled.iloc[:cutoff], shuffled.iloc[cutoff:]

    predicted = fit_svd_predictions(train)

    errors = []
    for _, row in test.iterrows():
        if row.user_id in predicted.index and row.movie_id in predicted.columns:
            pred = predicted.loc[row.user_id, row.movie_id]
            errors.append((pred - row.rating) ** 2)

    return float(np.sqrt(np.mean(errors))) if errors else float("nan")


if __name__ == "__main__":
    for uid in [1, 4]:
        print(f"\nRecommandations pour l'utilisateur {uid} :")
        print(collaborative_recommend(uid, n=5).to_string(index=False))

    print(f"\nRMSE sur notes cachées : {evaluate_rmse():.3f}")
