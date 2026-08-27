import streamlit as st

from data import MOVIES, RATINGS
from content_based import content_based_recommend
from collaborative import build_rating_matrix, collaborative_recommend, evaluate_rmse
from hybrid import hybrid_recommend

st.set_page_config(page_title="Sillon — recommandation", page_icon="🎬", layout="centered")

st.title("🎬 Sillon")
st.caption("Système de recommandation de films — contenu, collaboratif et hybride")

mode = st.sidebar.radio(
    "Mode de recommandation",
    ["Par contenu (à partir d'un film)", "Collaboratif (à partir d'un utilisateur)", "Hybride"],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Catalogue** : {len(MOVIES)} films")
st.sidebar.markdown(f"**Notes** : {len(RATINGS)} notes, {RATINGS.user_id.nunique()} utilisateurs")

if mode == "Par contenu (à partir d'un film)":
    st.subheader("Recommandation par contenu")
    st.write("Trouve des films thématiquement proches (genres, tags) d'un film que vous aimez.")

    title = st.selectbox("Choisissez un film", MOVIES["title"].sort_values())
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    if st.button("Recommander", type="primary"):
        results = content_based_recommend(title, n=n)
        st.dataframe(results, hide_index=True, use_container_width=True)

elif mode == "Collaboratif (à partir d'un utilisateur)":
    st.subheader("Recommandation collaborative")
    st.write("Prédit les notes que donnerait un utilisateur, en se basant sur des profils similaires.")

    matrix = build_rating_matrix()
    user_id = st.selectbox("Choisissez un utilisateur", matrix.index)
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    already_rated = RATINGS[RATINGS.user_id == user_id].merge(MOVIES, on="movie_id")
    with st.expander(f"Films déjà notés par l'utilisateur {user_id}"):
        st.dataframe(already_rated[["title", "rating"]], hide_index=True, use_container_width=True)

    if st.button("Recommander", type="primary"):
        results = collaborative_recommend(user_id, n=n)
        st.dataframe(results, hide_index=True, use_container_width=True)

    with st.expander("Évaluation du modèle (RMSE)"):
        st.write(
            "On cache 20% des notes connues, on les prédit, puis on compare "
            "à la vraie note. Plus le nombre est bas, meilleur est le modèle."
        )
        if st.button("Calculer le RMSE"):
            st.metric("RMSE", f"{evaluate_rmse():.3f}")

else:
    st.subheader("Recommandation hybride")
    st.write("Combine contenu et collaboratif selon un curseur de pondération.")

    matrix = build_rating_matrix()
    user_id = st.selectbox("Choisissez un utilisateur", matrix.index)
    alpha = st.slider(
        "Pondération (0 = tout collaboratif, 1 = tout contenu)",
        0.0, 1.0, 0.5, 0.1,
    )
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    if st.button("Recommander", type="primary"):
        results = hybrid_recommend(user_id, alpha=alpha, n=n)
        st.dataframe(results, hide_index=True, use_container_width=True)
