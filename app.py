import streamlit as st
import streamlit.components.v1 as components

from data import MOVIES, RATINGS
from content_based import content_based_recommend
from collaborative import build_rating_matrix, collaborative_recommend, evaluate_rmse
from hybrid import hybrid_recommend

st.set_page_config(page_title="Sillon — recommandation", page_icon="🎬", layout="centered")

st.markdown("""
<style>
.main-title{text-align:center;font-size:3rem;font-weight:800;margin-bottom:0}
.subtitle{text-align:center;color:#777;margin-bottom:2rem}
.donation{padding:1rem;border-radius:12px;border:1px solid rgba(128,128,128,.25);
text-align:center;margin-top:2rem}
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
    st.markdown("---")
    st.subheader("❤️ Soutenir Sillon")
    st.caption("Si le projet vous plaît, vous pouvez le soutenir avec PayPal.")

    # IMPORTANT : remplace cette URL par TON lien PayPal.Me ou ton lien de don.
    PAYPAL_URL = "https://www.paypal.com/donate"

    st.link_button("💙 Faire un don PayPal", PAYPAL_URL, use_container_width=True)

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
    st.subheader("👥 Recommandation collaborative")
    st.write("Prédit les notes que donnerait un utilisateur en se basant sur des profils similaires.")
    matrix = build_rating_matrix()
    user_id = st.selectbox("Choisissez un utilisateur", matrix.index)
    n = st.slider("Nombre de recommandations", 3, 10, 5)

    already_rated = RATINGS[RATINGS.user_id == user_id].merge(MOVIES, on="movie_id")
    with st.expander(f"📋 Films déjà notés par l'utilisateur {user_id}"):
        st.dataframe(already_rated[["title", "rating"]], hide_index=True, use_container_width=True)

    if st.button("🎬 Recommander", type="primary", use_container_width=True):
        results = collaborative_recommend(user_id, n=n).rename(columns={
            "title": "Film", "predicted_rating": "Note prédite"
        })
        results["Note prédite"] = results["Note prédite"].round(2)
        st.dataframe(results, hide_index=True, use_container_width=True)

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
st.markdown('<div class="donation"><strong>❤️ Vous aimez Sillon ?</strong><br>Soutenez le projet avec un petit don.</div>', unsafe_allow_html=True)

# IMPORTANT : remplace cette URL par TON lien PayPal.Me ou ton lien de don.
PAYPAL_ME = "https://www.paypal.com/donate"
components.html(f"""
<div style="text-align:center;margin-top:12px">
<a href="{PAYPAL_ME}" target="_blank"
style="display:inline-block;padding:12px 22px;background:#0070ba;color:white;
text-decoration:none;border-radius:8px;font-weight:700;font-family:Arial,sans-serif">
💙 Soutenir Sillon avec PayPal
</a>
</div>
""", height=60)
