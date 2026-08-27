"""
content_based.py
-----------------
Recommandation "si vous avez aimé X, vous aimerez peut-être Y" en se basant
uniquement sur les métadonnées des films (genres + tags), pas sur le
comportement des autres utilisateurs.

Étapes :
  1. TF-IDF : chaque film devient un vecteur où chaque dimension est un mot,
     pondéré par sa fréquence dans le film et sa rareté dans l'ensemble du
     catalogue (un mot présent partout, comme "drama", pèse moins qu'un mot
     rare comme "linguistique").
  2. Similarité cosinus : on mesure l'angle entre deux vecteurs films.
     Angle petit -> vecteurs proches -> films thématiquement proches.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data import MOVIES


def build_content_similarity(movies: pd.DataFrame = MOVIES) -> pd.DataFrame:
    """Retourne une matrice film x film de similarité cosinus (0 à 1)."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(movies["content_text"])
    sim = cosine_similarity(tfidf_matrix)
    return pd.DataFrame(sim, index=movies["title"], columns=movies["title"])


CONTENT_SIM = build_content_similarity()


def content_based_recommend(title: str, n: int = 5) -> pd.DataFrame:
    """Films les plus proches thématiquement d'un film donné."""
    if title not in CONTENT_SIM.columns:
        raise ValueError(f"Film inconnu : {title}")

    scores = CONTENT_SIM[title].drop(index=title).sort_values(ascending=False)
    top = scores.head(n).reset_index()
    top.columns = ["title", "content_score"]
    return top


if __name__ == "__main__":
    for ref in ["Interstellar", "The Grand Budapest Hotel"]:
        print(f"\nFilms proches de « {ref} » :")
        print(content_based_recommend(ref, n=5).to_string(index=False))
