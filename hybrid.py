"""
hybrid.py
---------
Combine les deux moteurs :
  - le score "contenu" d'un film pour un utilisateur = sa similarité moyenne
    avec les films que cet utilisateur a le mieux notés (>= 4)
  - le score "collaboratif" = la note prédite par la SVD (rapportée sur 0-1)

score_final = alpha * contenu + (1 - alpha) * collaboratif

alpha proche de 1 -> recommandations basées sur les thèmes déjà aimés
alpha proche de 0 -> recommandations basées sur des profils similaires
"""

import pandas as pd

from data import MOVIES, RATINGS
from content_based import CONTENT_SIM
from collaborative import build_rating_matrix, PREDICTED_RATINGS


def _content_score_for_user(user_id: int) -> pd.Series:
    """Moyenne de similarité de chaque film avec les films aimés (note >= 4)."""
    matrix = build_rating_matrix()
    user_ratings = matrix.loc[user_id].dropna()
    liked_ids = user_ratings[user_ratings >= 4].index
    liked_titles = MOVIES.set_index("movie_id").loc[liked_ids, "title"]

    if len(liked_titles) == 0:
        return pd.Series(0.0, index=MOVIES["title"])

    return CONTENT_SIM[liked_titles].mean(axis=1)


def hybrid_recommend(user_id: int, alpha: float = 0.5, n: int = 5) -> pd.DataFrame:
    matrix = build_rating_matrix()
    already_rated_ids = matrix.loc[user_id].dropna().index
    already_rated_titles = set(MOVIES.set_index("movie_id").loc[already_rated_ids, "title"])

    content_scores = _content_score_for_user(user_id)

    collab = PREDICTED_RATINGS.loc[user_id]
    collab_norm = (collab - collab.min()) / (collab.max() - collab.min() + 1e-9)
    collab_scores = collab_norm.rename(index=MOVIES.set_index("movie_id")["title"])

    combined = alpha * content_scores + (1 - alpha) * collab_scores
    combined = combined.drop(index=[t for t in already_rated_titles if t in combined.index])

    top = combined.sort_values(ascending=False).head(n).reset_index()
    top.columns = ["title", "hybrid_score"]
    return top


if __name__ == "__main__":
    for alpha in [0.2, 0.5, 0.8]:
        print(f"\nUtilisateur 4, alpha={alpha} :")
        print(hybrid_recommend(user_id=4, alpha=alpha, n=5).to_string(index=False))
