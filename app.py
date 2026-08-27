import streamlit as st
from data import MOVIES, RATINGS
from content_based import content_based_recommend
from collaborative import build_rating_matrix, collaborative_recommend, evaluate_rmse

st.set_page_config(page_title="Sillon — recommandation", page_icon="🎬", layout="centered")

st.markdown("""
<style>
.main-title{text-align:center;font-size:3rem;font-weight:800;margin-bottom:0}
.subtitle{text-align:center;color:#777;margin-bottom:2rem}

.profile-card {
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 16px;
    padding: 20px 14px;
    margin-bottom: 10px;
    text-align: center;
    min-height: 190px;
}

.avatar {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(128,128,128,.12);
    margin: 0 auto 12px auto;
    font-size: 2rem;
}

.big-avatar {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(128,128,128,.12);
    font-size: 2.5rem;
}

.profile-name {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.profile-stats {
    color: #777;
    line-height: 1.7;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 18px;
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 16px;
    margin-bottom: 20px;
}

.profile-header h2 {
    margin: 0;
}

.profile-header p {
    margin: 4px 0 0 0;
    color: #777;
}

.social-box {
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,.25);
    text-align: center;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 Sillon</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Système de recommandation de films — contenu, collaboratif et hybride</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Navigation")
    mode = st.radio("Mode de recommandation", [
        "Par contenu (à partir d'un film)",
        "Collaboratif (à partir d'un utilisateur)",
        "Hybride"
    ])
    st.markdown("---")
    st.markdown(f"**Catalogue :** {len(MOVIES)} films")
    st.markdown(f"**Notes :** {len(RATINGS)}")
    st.markdown(f"**Utilisateurs :** {RATINGS.user_id.nunique()}")

if mode == "Par contenu (à partir d'un film)":
    st.subheader("🎯 Recommandation par contenu")
    st.write("Trouve des films thématiquement proches d'un film que vous aimez à partir des genres et tags.")
    title = st.selectbox("Choisissez un film", MOVIES["title"].sort_values())
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    if st.button("🎬 Recommander", type="primary", use_container_width=True):
        results = content_based_recommend(title, n=n).rename(columns={
            "title": "Film", "content_score": "Score de similarité"
        })
        results["Score de similarité"] = results["Score de similarité"].round(3)
        st.dataframe(results, hide_index=True, use_container_width=True)

elif mode == "Collaboratif (à partir d'un utilisateur)":
    st.subheader("👥 Profils cinéphiles")
    st.write(
        "Explorez les profils et découvrez les recommandations générées pour chaque profil."
    )

    matrix = build_rating_matrix()
    users = list(matrix.index)
    selected_user = st.session_state.get("selected_user")

    cols = st.columns(3)

    for i, uid in enumerate(users):
        user_ratings = RATINGS[RATINGS.user_id == uid]
        avg_rating = (
            user_ratings["rating"].mean()
            if not user_ratings.empty
            else 0
        )
        movie_count = len(user_ratings)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="profile-card">
                    <div class="avatar">👤</div>
                    <div class="profile-name">Utilisateur {uid}</div>
                    <div class="profile-stats">
                        🎬 {movie_count} films<br>
                        ⭐ {avg_rating:.1f}/5 de moyenne
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "Voir le profil",
                key=f"profile_{uid}",
                use_container_width=True
            ):
                st.session_state["selected_user"] = uid
                st.rerun()

    if selected_user is not None:
        uid = selected_user

        st.markdown("---")

        user_ratings = RATINGS[RATINGS.user_id == uid].merge(
            MOVIES,
            on="movie_id"
        )

        avg_rating = (
            user_ratings["rating"].mean()
            if not user_ratings.empty
            else 0
        )

        st.markdown(
            f"""
            <div class="profile-header">
                <div class="big-avatar">👤</div>
                <div>
                    <h2>Utilisateur {uid}</h2>
                    <p>
                        🎬 {len(user_ratings)} films notés
                        &nbsp; • &nbsp;
                        ⭐ {avg_rating:.1f}/5
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### ❤️ Films notés")

        st.dataframe(
            user_ratings[["title", "rating"]].sort_values(
                "rating",
                ascending=False
            ),
            hide_index=True,
            use_container_width=True
        )

        st.markdown("### 🎬 Recommandations pour ce profil")

        n = st.slider(
            "Nombre de recommandations",
            3,
            10,
            5,
            key=f"n_{uid}"
        )

        results = collaborative_recommend(
            uid,
            n=n
        ).rename(
            columns={
                "title": "Film",
                "predicted_rating": "Note prédite"
            }
        )

        results["Note prédite"] = results["Note prédite"].round(2)

        st.dataframe(
            results,
            hide_index=True,
            use_container_width=True
        )

        if st.button(
            "← Retour aux profils",
            use_container_width=True
        ):
            st.session_state.pop("selected_user", None)
            st.rerun()

    with st.expander("📊 Évaluation du modèle (RMSE)"):
        st.write("Plus le RMSE est bas, meilleur est le modèle.")

        if st.button("Calculer le RMSE"):
            st.metric("RMSE", f"{evaluate_rmse():.3f}")

else:
    st.subheader("🧠 Recommandation hybride")
    st.write("Combine les recommandations par contenu et collaboratives selon une pondération personnalisable.")
    matrix = build_rating_matrix()
    user_id = st.selectbox("Choisissez un utilisateur", matrix.index)
    alpha = st.slider("Pondération (0 = tout collaboratif, 1 = tout contenu)", 0.0, 1.0, 0.5, 0.1)
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    if st.button("🎬 Recommander", type="primary", use_container_width=True):
        results = hybrid_recommend(user_id, alpha=alpha, n=n).rename(columns={
            "title": "Film", "hybrid_score": "Score hybride"
        })
        results["Score hybride"] = results["Score hybride"].round(3)
        st.dataframe(results, hide_index=True, use_container_width=True)

st.markdown("---")

st.markdown(
    '<div class="social-box">'
    '<strong>❤️ Vous aimez Sillon ?</strong><br>'
    'Soutenez le projet avec un petit follow sur Instagram ou GitHub.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.link_button(
        "📸 Instagram",
        "https://www.instagram.com/viqster09/",
        use_container_width=True
    )

with col2:
    st.link_button(
        "💻 GitHub",
        "https://github.com/viqster09",
        use_container_width=True
    )
