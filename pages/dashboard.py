import streamlit as st
from collections import Counter

from auth import logout
from database import (
    load_user_history,
    load_user_recommended_actions,
    get_user_cash_balance,
)
from styles import load_global_styles
from utils import get_history_summary
from ui_helpers import nav_with_transition

LOGO_PATH = "assets/finpilot_logo_final.png"

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="FinPilot | Dashboard",
    page_icon=LOGO_PATH,
    layout="wide",
)

st.markdown(load_global_styles(), unsafe_allow_html=True)

# =========================
# AUTH
# =========================

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Veuillez vous connecter depuis la page principale.")
    st.stop()

if "user_id" not in st.session_state:
    st.warning("Session invalide.")
    st.stop()

# =========================
# DATA
# =========================

user_id = st.session_state.user_id

history_rows = load_user_history(user_id)
recommended_rows = load_user_recommended_actions(user_id)

insights = get_history_summary(
    history_rows,
    recommended_rows
)

cash_balance = get_user_cash_balance(user_id)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    try:
        st.image(LOGO_PATH, width=62)
    except Exception:
        pass

    st.markdown(
        """
        <div class="sidebar-brand-wrap">

            <div class="sidebar-logo-name">
                FinPilot
            </div>

            <div class="sidebar-logo-sub">
                AI Investment Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # NAVIGATION

    nav_items = [
        ("Dashboard",    "app.py",                  "Chargement dashboard..."),
        ("Analyse IA",   "pages/analyse.py",         "Préparation analyse..."),
        ("Portefeuille", "pages/portefeuille.py",    "Chargement portefeuille..."),
        ("Historique",   "pages/historique.py",      "Chargement historique..."),
        ("Profil",       "pages/profil.py",           "Chargement profil..."),
    ]

    for label, page, msg in nav_items:

        # FIX : key unique préfixée "nav_" pour éviter le conflit avec les boutons Quick Actions
        if st.button(label, use_container_width=True, key=f"nav_{label}"):

            if page != "app.py":
                nav_with_transition(page, msg)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # USER BOX

    st.markdown(
        f"""
        <div class="sidebar-user">

            <div class="sidebar-user-name">
                {st.session_state.get('user_name', 'Utilisateur')}
            </div>

            <div class="sidebar-user-email">
                {st.session_state.get('user_email', '')}
            </div>

            <div class="sidebar-cash">

                <span class="sidebar-cash-label">
                    CASH DISPONIBLE
                </span>

                <span class="sidebar-cash-value">
                    {cash_balance:,.2f} $
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="glass-card"
             style="
                padding:1rem;
                margin-top:1rem;
             ">

            <div style="
                color:#FFFFFF;
                font-size:1rem;
                font-weight:800;
                margin-bottom:0.6rem;
            ">
                FinPilot AI
            </div>

            <div style="
                color:#B8C7DA;
                line-height:1.7;
                font-size:0.9rem;
            ">
                Intelligence artificielle financière,
                recommandations intelligentes et
                analyse comportementale investisseur.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # FIX : key unique pour le bouton Déconnexion
    if st.button("Déconnexion", use_container_width=True, key="nav_logout"):
        logout()
        st.switch_page("app.py")

# =========================
# HERO SECTION
# =========================

st.markdown(
    f"""
    <div class="glass-card fp-fade-in"
         style="
            padding:2.4rem;
            margin-bottom:1.5rem;
            position:relative;
            overflow:hidden;
         ">

        <div style="
            position:absolute;
            top:-140px;
            right:-120px;
            width:320px;
            height:320px;
            border-radius:50%;
            background:
                radial-gradient(
                    circle,
                    rgba(47,124,255,0.22),
                    transparent 70%
                );
        "></div>

        <div style="
            position:absolute;
            bottom:-120px;
            left:-80px;
            width:280px;
            height:280px;
            border-radius:50%;
            background:
                radial-gradient(
                    circle,
                    rgba(122,92,255,0.18),
                    transparent 70%
                );
        "></div>

        <div class="section-label">
            AI INVESTMENT PLATFORM
        </div>

        <div style="height:1rem;"></div>

        <div class="page-title">
            Bonjour {st.session_state.get('user_name', 'Investisseur')} 👋
        </div>

        <div class="page-subtitle" style="max-width:760px;">
            Analysez les marchés financiers avec l'intelligence artificielle,
            optimisez votre portefeuille et recevez des recommandations
            personnalisées selon votre profil investisseur.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# KPI
# =========================

k1, k2, k3, k4 = st.columns(4)

cards = [
    (
        "Analyses réalisées",
        str(insights["nb_analyses"]),
        "historique utilisateur"
    ),
    (
        "Profil dominant",
        insights["profil_dominant"] or "—",
        "profil investisseur"
    ),
    (
        "Horizon dominant",
        insights["horizon_dominant"] or "—",
        "vision marché"
    ),
    (
        "Cash disponible",
        f"{cash_balance:,.0f} $",
        "liquidité actuelle"
    ),
]

for col, (title, value, sub) in zip(
    [k1, k2, k3, k4],
    cards
):

    with col:

        st.markdown(
            f"""
            <div class="kpi-card fp-fade-in">

                <div class="kpi-title">
                    {title}
                </div>

                <div class="kpi-value">
                    {value}
                </div>

                <div class="kpi-sub">
                    {sub}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# =========================
# MAIN CONTENT
# =========================

left, right = st.columns([1.8, 1], gap="large")

# =========================
# LEFT
# =========================

with left:

    secteurs_txt = (
        ", ".join(insights["secteurs_favoris"])
        if insights["secteurs_favoris"]
        else "aucune préférence sectorielle forte"
    )

    actions_txt = (
        ", ".join(insights["actions_recurrentes"][:5])
        if insights["actions_recurrentes"]
        else "aucune action récurrente"
    )

    st.markdown(
        f"""
        <div class="glass-card fp-fade-in"
             style="
                padding:1.5rem;
                min-height:320px;
             ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:1.4rem;
            ">

                <div>

                    <div style="
                        color:#FFFFFF;
                        font-size:1.2rem;
                        font-weight:800;
                    ">
                        Lecture intelligente IA
                    </div>

                    <div style="
                        color:#8FA7C4;
                        margin-top:0.25rem;
                    ">
                        Synthèse comportementale investisseur
                    </div>

                </div>

                <div style="
                    background:rgba(49,230,168,0.12);
                    color:#31E6A8;
                    padding:0.5rem 0.9rem;
                    border-radius:999px;
                    font-size:0.76rem;
                    font-weight:800;
                ">
                    IA ACTIVE
                </div>

            </div>

            <div style="
                color:#C7D4E7;
                line-height:1.9;
                font-size:1rem;
            ">

                Votre profil dominant est
                <span style="color:#FFFFFF;font-weight:800;">
                    {insights['profil_dominant'] or 'non disponible'}
                </span>.

                Votre horizon dominant est
                <span style="color:#FFFFFF;font-weight:800;">
                    {insights['horizon_dominant'] or 'non disponible'}
                </span>.

                Les secteurs les plus fréquents sont
                <span style="color:#31E6A8;font-weight:700;">
                    {secteurs_txt}
                </span>.

                Les actions les plus analysées sont
                <span style="color:#69D8FF;font-weight:700;">
                    {actions_txt}
                </span>.

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# RIGHT
# =========================

with right:

    st.markdown(
        """
        <div class="side-widget fp-fade-in">

            <div class="side-widget-title">
                Actions fréquentes
            </div>
        """,
        unsafe_allow_html=True,
    )

    ticker_counts = Counter(
        r[0] for r in recommended_rows
    ).most_common(5)

    if ticker_counts:

        max_count = ticker_counts[0][1]

        for ticker, count in ticker_counts:

            pct = int((count / max_count) * 100)

            st.markdown(
                f"""
                <div class="widget-list-item">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">

                        <div class="widget-list-title">
                            {ticker}
                        </div>

                        <div style="
                            color:#8FA7C4;
                            font-size:0.82rem;
                        ">
                            {count} analyses
                        </div>

                    </div>

                    <div class="alloc-bar-wrap">

                        <div class="alloc-bar"
                             style="width:{pct}%">
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# QUICK ACTIONS
# =========================

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:

    # FIX : key "qa_analyse" distincte de "nav_Analyse IA"
    if st.button(
        "Lancer une analyse IA",
        use_container_width=True,
        type="primary",
        key="qa_analyse"
    ):

        nav_with_transition(
            "pages/analyse.py",
            "Préparation analyse IA..."
        )

with c2:

    # FIX : key "qa_portefeuille" distincte de "nav_Portefeuille"
    if st.button(
        "Voir portefeuille",
        use_container_width=True,
        key="qa_portefeuille"
    ):

        nav_with_transition(
            "pages/portefeuille.py",
            "Chargement portefeuille..."
        )

with c3:

    # FIX : key "qa_historique" distincte de "nav_Historique"
    if st.button(
        "Voir historique",
        use_container_width=True,
        key="qa_historique"
    ):

        nav_with_transition(
            "pages/historique.py",
            "Chargement historique..."
        )