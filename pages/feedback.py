import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import (
    init_db,
    get_user_cash_balance,
    save_feedback,
    get_user_feedbacks,
    get_feedback_stats,
    user_has_given_feedback_today,
    FEEDBACK_CATEGORIES,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Avis clients",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.user_id
cash_balance = get_user_cash_balance(user_id)

render_sidebar(
    active_page="feedback",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# STYLES LOCAUX
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

.block-container {
    padding-top: 0.7rem !important;
    padding-bottom: 3rem !important;
}

.fb-hero {
    position: relative;
    overflow: hidden;
    padding: 2.2rem 2.5rem;
    border-radius: 0 0 30px 30px;
    color: white;
    background:
        radial-gradient(circle at 90% 20%, rgba(122,92,255,.55), transparent 25%),
        linear-gradient(120deg, #051633 0%, #0A2D78 50%, #2563EB 100%);
    box-shadow: 0 20px 55px rgba(8,25,70,.22);
    margin-bottom: 1.5rem;
}
.fb-hero-label {
    color: #83EFFF;
    font-size: .82rem;
    font-weight: 900;
    letter-spacing: .10em;
    text-transform: uppercase;
    margin-bottom: .6rem;
}
.fb-hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -.04em;
    line-height: 1.1;
    margin-bottom: .75rem;
}
.fb-hero-sub {
    color: rgba(255,255,255,.85);
    font-size: 1.05rem;
    line-height: 1.7;
    max-width: 680px;
}

.fb-card {
    background: #FFFFFF;
    border: 1px solid #DCE7F8;
    border-radius: 22px;
    padding: 1.6rem 1.8rem;
    box-shadow: 0 10px 32px rgba(22,46,90,.07);
    margin-bottom: 1rem;
}
.fb-card-title {
    color: #10233F;
    font-family: 'Sora', sans-serif;
    font-size: 1.18rem;
    font-weight: 800;
    margin-bottom: .4rem;
}
.fb-card-sub {
    color: #64748B;
    font-size: .95rem;
    line-height: 1.6;
    margin-bottom: 1.1rem;
}

/* ÉTOILES */
.star-row {
    display: flex;
    gap: .35rem;
    margin-bottom: 1rem;
}
.star-label {
    color: #10233F;
    font-weight: 800;
    font-size: .95rem;
    margin-bottom: .55rem;
}

/* AVIS EXISTANTS */
.review-card {
    background: #F6FAFF;
    border: 1px solid #DCE7F8;
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .75rem;
}
.review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .45rem;
}
.review-stars {
    color: #F59E0B;
    font-size: 1.05rem;
    letter-spacing: .05em;
}
.review-cat {
    display: inline-block;
    padding: .3rem .65rem;
    border-radius: 999px;
    background: #EAF2FF;
    color: #2F7CFF;
    font-size: .78rem;
    font-weight: 800;
    border: 1px solid #CFE0FF;
}
.review-date {
    color: #94A3B8;
    font-size: .82rem;
}
.review-msg {
    color: #334155;
    font-size: .95rem;
    line-height: 1.65;
}

/* STAT CARDS */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.2rem;
}
.stat-card {
    background: #FFFFFF;
    border: 1px solid #DCE7F8;
    border-radius: 20px;
    padding: 1.2rem 1.35rem;
    box-shadow: 0 8px 24px rgba(22,46,90,.06);
    text-align: center;
}
.stat-value {
    color: #10233F;
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    line-height: 1.1;
}
.stat-label {
    color: #64748B;
    font-size: .85rem;
    margin-top: .3rem;
}

/* BARRE DE NOTE */
.dist-row {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin-bottom: .45rem;
}
.dist-label {
    color: #475569;
    font-size: .88rem;
    font-weight: 700;
    width: 18px;
    text-align: right;
    flex-shrink: 0;
}
.dist-bar-wrap {
    flex: 1;
    height: 8px;
    background: #EEF4FF;
    border-radius: 999px;
    overflow: hidden;
}
.dist-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #F59E0B, #FBBF24);
}
.dist-count {
    color: #94A3B8;
    font-size: .82rem;
    width: 24px;
    text-align: left;
    flex-shrink: 0;
}

.fb-empty {
    text-align: center;
    padding: 2rem 1rem;
    color: #94A3B8;
    font-size: .95rem;
    line-height: 1.7;
}
.fb-empty b {
    color: #64748B;
    display: block;
    font-size: 1.05rem;
    margin-bottom: .4rem;
}

.fb-success-banner {
    background: linear-gradient(135deg, #E9FBF5, #F0FFF8);
    border: 1px solid #A7F3D0;
    border-radius: 16px;
    padding: 1rem 1.3rem;
    color: #065F46;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: .7rem;
}

.fb-warning-banner {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-radius: 16px;
    padding: 1rem 1.3rem;
    color: #92400E;
    font-weight: 700;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def stars_display(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


def rating_color(n: int) -> str:
    colors = {1: "#EF4444", 2: "#F97316", 3: "#F59E0B", 4: "#3B82F6", 5: "#10B981"}
    return colors.get(n, "#F59E0B")


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="fb-hero">
    <div class="fb-hero-label">✦ Votre opinion compte</div>
    <div class="fb-hero-title">Avis clients et retours utilisateurs</div>
    <div class="fb-hero-sub">
        Après votre simulation, partagez votre ressenti sur la clarté, la simplicité et l’utilité des recommandations.
        Ces retours permettent de valider le prototype et d’améliorer l’expérience utilisateur.
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# STATS GLOBALES
# ============================================================

stats = get_feedback_stats()
total_avis = stats["total"]
avg_rating = stats["avg_rating"]
distribution = stats["distribution"]

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{avg_rating:.1f} / 5</div>
        <div class="stat-label">Note moyenne globale</div>
        <div style="color:#F59E0B;font-size:1.2rem;margin-top:.35rem;">{stars_display(round(avg_rating))}</div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_avis}</div>
        <div class="stat-label">Avis déposés au total</div>
    </div>
    """, unsafe_allow_html=True)

with col_s3:
    top_cat = list(stats["by_category"].keys())[0] if stats["by_category"] else "—"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value" style="font-size:1.35rem;">{top_cat}</div>
        <div class="stat-label">Catégorie la plus citée</div>
    </div>
    """, unsafe_allow_html=True)

# Distribution des notes
if total_avis > 0:
    st.markdown('<div class="fb-card">', unsafe_allow_html=True)
    st.markdown('<div class="fb-card-title">Distribution des notes</div>', unsafe_allow_html=True)
    for note in range(5, 0, -1):
        cnt = distribution.get(str(note), 0)
        pct = int(cnt / total_avis * 100) if total_avis > 0 else 0
        st.markdown(f"""
        <div class="dist-row">
            <div class="dist-label">{note}</div>
            <div style="color:#F59E0B;font-size:.9rem;flex-shrink:0;">★</div>
            <div class="dist-bar-wrap">
                <div class="dist-bar-fill" style="width:{pct}%;"></div>
            </div>
            <div class="dist-count">{cnt}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# FORMULAIRE D'AVIS
# ============================================================

left_col, right_col = st.columns([1.1, 1], gap="large")

with left_col:
    st.markdown('<div class="fb-card">', unsafe_allow_html=True)
    st.markdown('<div class="fb-card-title">Laisser un avis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fb-card-sub">Partagez votre retour après votre simulation. '
        'Un seul avis par jour est accepté.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    already_submitted = user_has_given_feedback_today(user_id)

    if already_submitted:
        st.markdown("""
        <div class="fb-warning-banner">
            ⏳ Vous avez déjà soumis un avis aujourd'hui. Revenez demain pour en laisser un nouveau.
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.get("feedback_just_sent"):
            st.markdown("""
            <div class="fb-success-banner">
                ✅ Merci pour votre avis ! Il a bien été enregistré.
            </div>
            """, unsafe_allow_html=True)
            st.session_state.feedback_just_sent = False

        with st.form("form_feedback", clear_on_submit=True):
            # NOTE (étoiles via selectbox stylé)
            st.markdown('<div class="star-label">Votre note</div>', unsafe_allow_html=True)
            rating = st.select_slider(
                "Note",
                options=[1, 2, 3, 4, 5],
                value=4,
                format_func=lambda x: f"{'★' * x}{'☆' * (5 - x)}  ({x}/5)",
                label_visibility="collapsed",
            )

            # CATÉGORIE
            category = st.selectbox(
                "Catégorie",
                options=FEEDBACK_CATEGORIES,
                index=0,
            )

            # MESSAGE
            message = st.text_area(
                "Votre commentaire",
                placeholder="Décrivez votre expérience avec FinPilot après votre simulation…",
                height=145,
                max_chars=1000,
            )

            char_info = f"{len(message)}/1000 caractères" if message else "0/1000 caractères"
            st.caption(char_info)

            submitted = st.form_submit_button(
                "Envoyer mon avis",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not message or len(message.strip()) < 10:
                    st.error("Votre commentaire doit contenir au moins 10 caractères.")
                else:
                    ok = save_feedback(user_id, rating, category, message)
                    if ok:
                        st.session_state.feedback_just_sent = True
                        st.rerun()
                    else:
                        st.error("Une erreur est survenue. Veuillez réessayer.")


# ============================================================
# MES AVIS (colonne droite)
# ============================================================

with right_col:
    st.markdown("""
    <div class="fb-card">
        <div class="fb-card-title">Mes avis précédents</div>
        <div class="fb-card-sub">Retrouvez ici tous vos retours sur FinPilot.</div>
    </div>
    """, unsafe_allow_html=True)

    my_feedbacks = get_user_feedbacks(user_id)

    if not my_feedbacks:
        st.markdown("""
        <div class="fb-empty">
            <b>Aucun avis encore</b>
            Soumettez votre premier retour après votre prochaine simulation.
        </div>
        """, unsafe_allow_html=True)
    else:
        for fb in my_feedbacks:
            note = int(fb.get("rating", 3))
            cat = fb.get("category", "Général")
            msg = fb.get("message", "")
            date_str = str(fb.get("created_at", ""))[:16].replace("T", " ")
            star_str = stars_display(note)

            st.markdown(f"""
            <div class="review-card">
                <div class="review-header">
                    <div style="display:flex;align-items:center;gap:.6rem;">
                        <span class="review-stars" style="color:{rating_color(note)};">{star_str}</span>
                        <span class="review-cat">{cat}</span>
                    </div>
                    <div class="review-date">{date_str}</div>
                </div>
                <div class="review-msg">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
