"""
data.py
-------
Fournit deux DataFrames :
  - MOVIES  : les films et leurs métadonnées (genres, courte description)
  - RATINGS : des notes (1 à 5) données par des utilisateurs synthétiques

Ce jeu de données est volontairement petit et fabriqué à la main pour que le
projet tourne sans connexion internet. Pour brancher le vrai jeu MovieLens,
voir la fonction `load_from_movielens()` tout en bas du fichier.
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Métadonnées des films : titre, genres, courte description (pour le
#    filtrage par contenu). Les genres et descriptions sont volontairement
#    écrits à la main, pas copiés depuis une source externe.
# ---------------------------------------------------------------------------
MOVIES_RAW = [
    ("Interstellar",        "sci-fi drama space",        "exploration spatiale, relativité, sacrifice familial"),
    ("Arrival",              "sci-fi drama mystery",      "premier contact, linguistique, temps non linéaire"),
    ("Gravity",               "sci-fi thriller survival",  "survie en orbite, isolement, tension continue"),
    ("The Martian",          "sci-fi adventure comedy",   "survie sur Mars, ingéniosité, ton optimiste"),
    ("Moon",                  "sci-fi drama mystery",      "solitude, identité, huis clos lunaire"),
    ("Blade Runner 2049",    "sci-fi noir drama",         "dystopie, quête d'identité, esthétique froide"),
    ("Ex Machina",           "sci-fi thriller drama",     "intelligence artificielle, manipulation, huis clos"),
    ("Her",                    "sci-fi romance drama",      "relation homme-IA, solitude urbaine, mélancolie"),
    ("The Grand Budapest Hotel","comedy drama",            "loufoque, esthétique symétrique, aventure burlesque"),
    ("Amelie",                "comedy romance drama",      "fantaisie parisienne, quête de sens, ton doux-amer"),
    ("La La Land",            "romance drama musical",     "ambition artistique, amour contrarié, nostalgie"),
    ("Eternal Sunshine",     "romance drama sci-fi",      "mémoire, rupture, mélancolie introspective"),
    ("Lost in Translation",  "drama romance comedy",      "solitude, connexion inattendue, ennui existentiel"),
    ("Whiplash",              "drama music",               "obsession, mentorat toxique, dépassement de soi"),
    ("The Social Network",   "drama biography",           "ambition, trahison, ascension fulgurante"),
    ("Parasite",               "thriller drama comedy",     "inégalités sociales, tension de classe, twist"),
    ("Se7en",                  "thriller crime drama",      "enquête macabre, tension psychologique, fatalisme"),
    ("Prisoners",              "thriller crime drama",      "vengeance, dilemme moral, tension soutenue"),
    ("Mad Max: Fury Road",   "action adventure sci-fi",   "poursuite frénétique, désert post-apo, mise en scène pure"),
    ("John Wick",              "action thriller crime",     "vengeance stylisée, chorégraphie, univers codifié"),
    ("The Dark Knight",       "action crime drama",        "chaos moral, antagoniste iconique, tension urbaine"),
    ("Inception",              "sci-fi action thriller",    "rêves imbriqués, casse mentale, ambiguïté finale"),
    ("Coco",                    "animation family drama",    "mémoire familiale, tradition, émotion musicale"),
    ("Spirited Away",         "animation family fantasy",  "monde onirique, passage à l'âge adulte, esthétique japonaise"),
]

MOVIES = pd.DataFrame(MOVIES_RAW, columns=["title", "genres", "tags"])
MOVIES.insert(0, "movie_id", range(1, len(MOVIES) + 1))
# Le texte utilisé pour le TF-IDF : genres + tags concaténés
MOVIES["content_text"] = MOVIES["genres"] + " " + MOVIES["tags"]


# ---------------------------------------------------------------------------
# 2. Notes synthétiques.
#    Idée : chaque utilisateur a un "goût" caché pour 1-2 genres. On génère
#    des notes plus hautes sur les films qui matchent son goût, plus basses
#    sinon, puis on masque ~55% des cases (comme dans la vraie vie, personne
#    n'a noté tous les films).
# ---------------------------------------------------------------------------
def _generate_ratings(seed: int = 42, n_users: int = 14, hide_ratio: float = 0.55) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    all_genres = sorted(set(g for row in MOVIES["genres"] for g in row.split()))

    rows = []
    for user_id in range(1, n_users + 1):
        liked_genres = set(rng.choice(all_genres, size=rng.integers(1, 3), replace=False))
        for _, movie in MOVIES.iterrows():
            movie_genres = set(movie["genres"].split())
            overlap = len(liked_genres & movie_genres)
            base = 2.6 + overlap * 1.1
            noise = rng.normal(0, 0.6)
            rating = np.clip(round(base + noise), 1, 5)

            if rng.random() < hide_ratio:
                continue  # note manquante : l'utilisateur n'a pas vu/noté ce film

            rows.append((user_id, movie["movie_id"], int(rating)))

    return pd.DataFrame(rows, columns=["user_id", "movie_id", "rating"])


RATINGS = _generate_ratings()


# ---------------------------------------------------------------------------
# Pour brancher le vrai jeu MovieLens (ml-latest-small) plus tard :
# ---------------------------------------------------------------------------
def load_from_movielens(movies_csv: str, ratings_csv: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remplace MOVIES/RATINGS par le vrai jeu MovieLens.
    Télécharger ml-latest-small.zip sur https://grouplens.org/datasets/movielens/
    puis pointer vers movies.csv et ratings.csv.
    """
    movies = pd.read_csv(movies_csv)  # colonnes: movieId, title, genres
    ratings = pd.read_csv(ratings_csv)  # colonnes: userId, movieId, rating, timestamp

    movies = movies.rename(columns={"movieId": "movie_id"})
    movies["genres"] = movies["genres"].str.replace("|", " ", regex=False)
    movies["tags"] = ""  # MovieLens de base n'a pas de description longue
    movies["content_text"] = movies["genres"]

    ratings = ratings.rename(columns={"userId": "user_id", "movieId": "movie_id"})
    ratings = ratings[["user_id", "movie_id", "rating"]]

    return movies, ratings


# ---------------------------------------------------------------------------
# Bascule automatique : si les fichiers MovieLens sont présents à côté de ce
# script (ou dans le dossier pointé par la variable d'env MOVIELENS_DIR),
# on les utilise à la place du jeu de données synthétique. Rien d'autre à
# changer dans le reste du projet.
# ---------------------------------------------------------------------------
import os
_movies_csv = os.path.join("movies.csv")
_ratings_csv = os.path.join("ratings.csv")

if os.path.exists(_movies_csv) and os.path.exists(_ratings_csv):
    MOVIES, RATINGS = load_from_movielens(_movies_csv, _ratings_csv)
    print(f"[data] MovieLens chargé : {len(MOVIES)} films, {len(RATINGS)} notes")
else:
    print("[data] MovieLens non trouvé -> jeu de données synthétique utilisé "
          f"(placez movies.csv et ratings.csv pour basculer)")


if __name__ == "__main__":
    print(MOVIES[["movie_id", "title", "genres"]].to_string(index=False))
    print(f"\n{len(RATINGS)} notes générées pour {RATINGS.user_id.nunique()} utilisateurs "
          f"et {RATINGS.movie_id.nunique()} films.")
