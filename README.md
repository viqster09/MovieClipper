# Sillon — système de recommandation

Système de recommandation de films avec trois approches : par contenu (TF-IDF),
collaboratif (factorisation SVD) et hybride.

## Installation

```bash
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

Ça ouvre une page dans le navigateur avec trois modes : contenu, collaboratif, hybride.

## Lancer sans interface (dans le terminal)

Chaque module peut tourner seul pour voir des exemples dans la console :

```bash
python3 data.py            # aperçu du jeu de données
python3 content_based.py   # exemples de recommandation par contenu
python3 collaborative.py   # exemples de recommandation collaborative + RMSE
python3 hybrid.py          # exemples de recommandation hybride
```

## Structure du projet

```
recommender/
├── data.py            # jeu de données (films + notes)
├── content_based.py   # TF-IDF + similarité cosinus
├── collaborative.py   # matrice utilisateurs x films + SVD
├── hybrid.py           # combinaison pondérée des deux
├── app.py              # interface Streamlit
└── requirements.txt
```

## Le jeu de données

Ce projet utilise un petit jeu de données **synthétique** (24 films connus,
14 utilisateurs, ~150 notes) généré dans `data.py`, pour que le projet tourne
sans rien télécharger. Chaque utilisateur synthétique a un goût caché pour
1-2 genres, ce qui donne des recommandations cohérentes à observer.

## Brancher le vrai jeu MovieLens

Pour des résultats plus réalistes (et beaucoup plus de films) :

1. Télécharger `ml-latest-small.zip` sur https://grouplens.org/datasets/movielens/
2. Dézipper, tu obtiens `movies.csv` et `ratings.csv`
3. Dans `data.py`, remplacer les lignes :

```python
MOVIES = pd.DataFrame(MOVIES_RAW, ...)
RATINGS = _generate_ratings()
```

par :

```python
from data import load_from_movielens
MOVIES, RATINGS = load_from_movielens("chemin/vers/movies.csv", "chemin/vers/ratings.csv")
```

Le reste du code (`content_based.py`, `collaborative.py`, `hybrid.py`, `app.py`)
n'a besoin d'aucune modification : il consomme `MOVIES` et `RATINGS` sans
savoir d'où ils viennent.

## Comment ça marche, en résumé

| Approche | Principe | Fichier |
|---|---|---|
| Contenu | Vectorise genres/tags (TF-IDF), compare les films entre eux (similarité cosinus) | `content_based.py` |
| Collaboratif | Factorise la matrice notes utilisateurs x films (SVD) pour prédire les notes manquantes | `collaborative.py` |
| Hybride | Moyenne pondérée des deux scores, réglable via un paramètre `alpha` | `hybrid.py` |

## Limites connues

- Le jeu de données synthétique est petit : le TF-IDF a peu de vocabulaire
  pour bien distinguer les films. Avec MovieLens (des milliers de films),
  les résultats sont nettement plus fins.
- La SVD est ici calculée en une fois sur toute la matrice ; pour une vraie
  application en production, il faudrait la recalculer périodiquement à
  mesure que de nouvelles notes arrivent.
