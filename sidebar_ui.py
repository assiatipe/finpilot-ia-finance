import streamlit as st
from database import is_user_admin


# ============================================================
# UTILITAIRES
# ============================================================

def money_dollar(x):
    try:
        return f"{float(x):,.2f} $".replace(",", " ")
    except Exception:
        return "0.00 $"


def _clean_html(text: str) -> str:
    return "\n".join(line.strip() for line in text.strip().splitlines())


def _nav_button(label: str, page: str, key: str, active_page: str, page_key: str):
    """Bouton de navigation horizontal."""
    is_current = active_page == page_key

    if st.button(
        label,
        key=key,
        use_container_width=True,
        type="primary" if is_current else "secondary",
    ):
        if active_page != page_key:
            st.switch_page(page)


# ============================================================
# NAVIGATION FINPILOT — VERSION COMPACTE
# ============================================================

def render_sidebar(active_page="dashboard", cash_balance=5100.0, logout_callback=None):
    """
    Navigation commune FinPilot.

    active_page :
    - "dashboard"     -> Accueil
    - "analyse"       -> Analyse IA
    - "portefeuille"  -> Portefeuille
    - "historique"    -> Historique
    - "profil"        -> Profil
    - "progression"   -> Progression
    - "feedback"      -> Avis
    - "admin"         -> Admin
    """

    css = """
    <style>
    /* Masquer la navigation native Streamlit */
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 0.20rem !important;
    }

    /* ======================================================
       BARRE MARCHÉ — FINE
       ====================================================== */

    .fp-market-topline {
        width: 100%;
        min-height: 28px;
        height: 28px;
        background: linear-gradient(90deg, #041226 0%, #071B39 52%, #082B5A 100%);
        border-bottom: 1px solid rgba(255,255,255,.06);
        display: flex;
        align-items: center;
        overflow: hidden;
        margin: 0;
        box-shadow: 0 5px 18px rgba(5,18,38,.10);
    }

    .fp-market-track {
        display: flex;
        align-items: center;
        gap: 1.75rem;
        white-space: nowrap;
        animation: fpTickerMove 36s linear infinite;
        padding-left: 0.9rem;
    }

    .fp-market-item {
        color: rgba(255,255,255,.82);
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .01em;
    }

    .fp-market-up {
        color: #35E6A7;
        margin-left: .30rem;
    }

    .fp-market-down {
        color: #FF5B72;
        margin-left: .30rem;
    }

    .fp-market-flat {
        color: #B7C7DA;
        margin-left: .30rem;
    }

    @keyframes fpTickerMove {
        0% { transform: translateX(0); }
        100% { transform: translateX(-45%); }
    }

    /* ======================================================
       HEADER — COMPACT, SANS GRAND VIDE
       ====================================================== */

    .fp-topnav-shell {
        position: relative;
        width: 100%;
        min-height: 64px;
        background:
            radial-gradient(circle at 8% 0%, rgba(47,124,255,.20), transparent 25%),
            linear-gradient(90deg, #061633 0%, #082447 56%, #071A33 100%);
        border-bottom: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 12px 32px rgba(6,22,51,.15);
        display: grid;
        grid-template-columns: minmax(250px, 330px) minmax(0, 1fr) minmax(170px, 210px);
        align-items: center;
        gap: 1rem;
        padding: .55rem .95rem;
        margin-bottom: .55rem;
        overflow: hidden;
    }

    .fp-topnav-shell::after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        border-radius: 50%;
        right: -105px;
        top: -125px;
        background: radial-gradient(circle, rgba(122,92,255,.24), transparent 66%);
        pointer-events: none;
    }

    .fp-brand-zone {
        display: flex;
        align-items: center;
        gap: .72rem;
        position: relative;
        z-index: 2;
    }

    .fp-logo-symbol {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        background:
            radial-gradient(circle at 30% 28%, rgba(255,255,255,.24), transparent 22%),
            linear-gradient(135deg,#2F7CFF 0%,#23D8F0 55%,#27E0B3 100%);
        position: relative;
        box-shadow: 0 11px 24px rgba(47,124,255,.27);
        flex-shrink: 0;
    }

    .fp-logo-symbol::before {
        content: "";
        position: absolute;
        width: 11px;
        height: 29px;
        left: 15.5px;
        top: 6px;
        border-radius: 999px;
        background: rgba(255,255,255,.28);
    }

    .fp-logo-symbol::after {
        content: "";
        position: absolute;
        width: 29px;
        height: 11px;
        left: 6px;
        top: 15.5px;
        border-radius: 999px;
        background: rgba(255,255,255,.28);
    }

    .fp-brand-name {
        color: white;
        font-size: 1.35rem;
        font-weight: 950;
        letter-spacing: -.04em;
        line-height: 1;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    .fp-brand-sub {
        margin-top: .18rem;
        color: rgba(255,255,255,.74);
        font-size: .78rem;
        font-weight: 750;
    }

    .fp-nav-caption {
        color: #7CF3FF;
        font-size: .58rem;
        font-weight: 950;
        letter-spacing: .10em;
        text-transform: uppercase;
        margin-top: .12rem;
    }

    .fp-header-center {
        color: rgba(255,255,255,.78);
        font-size: .82rem;
        line-height: 1.45;
        font-weight: 800;
        text-align: right;
        position: relative;
        z-index: 2;
    }

    .fp-header-cash {
        justify-self: end;
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 14px;
        padding: .52rem .78rem;
        color: white;
        position: relative;
        z-index: 2;
        min-width: 160px;
    }

    .fp-header-cash-label {
        color: rgba(255,255,255,.60);
        font-size: .62rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        line-height: 1;
    }

    .fp-header-cash-value {
        margin-top: .20rem;
        color: white;
        font-size: .96rem;
        font-weight: 950;
        line-height: 1;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    /* ======================================================
       BOUTONS NAVIGATION — PLUS FINS
       ====================================================== */

    div[data-testid="column"] .stButton > button {
        height: 42px !important;
        min-height: 42px !important;
        border-radius: 13px !important;
        font-size: .82rem !important;
        font-weight: 850 !important;
        letter-spacing: .01em !important;
        border: 1px solid rgba(210,224,245,.95) !important;
        box-shadow: 0 8px 18px rgba(22,46,90,.045) !important;
        transition: all .16s ease !important;
        text-transform: none !important;
        padding: 0 .20rem !important;
    }

    div[data-testid="column"] .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,.62) !important;
        color: #12345A !important;
    }

    div[data-testid="column"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2F7CFF, #735CFF) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        box-shadow: 0 12px 24px rgba(47,124,255,.22) !important;
    }

    div[data-testid="column"] .stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.04);
    }

    /* Réduit l'espace vertical après les boutons */
    .fp-after-nav-space {
        height: .45rem;
    }

    /* ======================================================
       SIDEBAR : panneau d'état uniquement
       ====================================================== */

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 20% 5%, rgba(47,124,255,.18), transparent 26%),
            radial-gradient(circle at 85% 92%, rgba(39,224,179,.10), transparent 28%),
            linear-gradient(180deg, #061633 0%, #08214A 55%, #071831 100%) !important;
        border-right: 1px solid rgba(255,255,255,.05);
        box-shadow: 18px 0 60px rgba(7,24,49,.18);
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.0rem !important;
        padding-left: .80rem !important;
        padding-right: .80rem !important;
    }

    .sidebar-status-card {
        position: relative;
        overflow: hidden;
        padding: 1rem .95rem;
        border-radius: 20px;
        border: 1px solid rgba(99,171,255,.28);
        background:
            radial-gradient(circle at 90% 12%, rgba(122,92,255,.26), transparent 30%),
            radial-gradient(circle at 15% 90%, rgba(39,224,179,.12), transparent 28%),
            linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
        box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 14px 36px rgba(0,0,0,.13);
        color: white;
    }

    .sidebar-status-kicker {
        color: #83EFFF;
        font-size: .70rem;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: .10em;
    }

    .sidebar-status-title {
        margin-top: .32rem;
        color: white;
        font-size: 1.05rem;
        font-weight: 950;
        line-height: 1.22;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    .sidebar-status-text {
        margin-top: .48rem;
        color: rgba(255,255,255,.78);
        font-size: .82rem;
        line-height: 1.45;
    }

    .sidebar-cash-box {
        margin-top: .85rem;
        padding: .75rem;
        border-radius: 14px;
        background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.08);
    }

    .sidebar-cash-label {
        color: rgba(255,255,255,.64);
        font-size: .68rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .sidebar-cash-value {
        margin-top: .22rem;
        color: white;
        font-size: 1.16rem;
        font-weight: 950;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    .sidebar-mini-stage {
        position: relative;
        height: 86px;
        margin-top: .85rem;
        border-radius: 16px;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(6,24,51,.42), rgba(255,255,255,.03));
        border: 1px solid rgba(255,255,255,.06);
    }

    .sidebar-stage-grid {
        position: absolute;
        inset: 0;
        background:
            linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
        background-size: 20px 20px;
        opacity: .7;
    }

    .sidebar-stage-bars {
        position: absolute;
        right: 10px;
        bottom: 8px;
        display: flex;
        align-items: flex-end;
        gap: 5px;
    }

    .sidebar-stage-bars span {
        width: 9px;
        border-radius: 999px 999px 2px 2px;
        background: linear-gradient(180deg, rgba(111,255,224,.80), rgba(47,124,255,.18));
        animation: sidebarBarFloat 2.8s ease-in-out infinite;
    }

    .sidebar-stage-bars span:nth-child(1){height:18px; animation-delay:0s;}
    .sidebar-stage-bars span:nth-child(2){height:28px; animation-delay:.15s;}
    .sidebar-stage-bars span:nth-child(3){height:40px; animation-delay:.3s;}
    .sidebar-stage-bars span:nth-child(4){height:54px; animation-delay:.45s;}
    .sidebar-stage-bars span:nth-child(5){height:38px; animation-delay:.6s;}
    .sidebar-stage-bars span:nth-child(6){height:64px; animation-delay:.75s;}

    .sidebar-note {
        margin-top: .85rem;
        color: rgba(255,255,255,.58);
        font-size: .74rem;
        line-height: 1.4;
    }

    @keyframes sidebarBarFloat {
        0%,100% { transform: translateY(0); opacity:.92; }
        50% { transform: translateY(-4px); opacity:1; }
    }

    @media (max-width: 1180px) {
        .fp-topnav-shell {
            grid-template-columns: 1fr;
            gap: .45rem;
        }

        .fp-header-center,
        .fp-header-cash {
            justify-self: stretch;
            text-align: left;
        }
    }
    </style>
    """

    st.markdown(_clean_html(css), unsafe_allow_html=True)

    market_html = """
    <div class="fp-market-topline">
        <div class="fp-market-track">
            <span class="fp-market-item">AAPL <span class="fp-market-up">+0.8% ▲</span></span>
            <span class="fp-market-item">MSFT <span class="fp-market-up">+1.1% ▲</span></span>
            <span class="fp-market-item">JNJ <span class="fp-market-flat">0.0% —</span></span>
            <span class="fp-market-item">KO <span class="fp-market-up">+0.4% ▲</span></span>
            <span class="fp-market-item">WMT <span class="fp-market-down">-0.2% ▼</span></span>
            <span class="fp-market-item">VISA <span class="fp-market-up">+0.6% ▲</span></span>
            <span class="fp-market-item">Simulation pédagogique · aucun ordre réel transmis</span>
            <span class="fp-market-item">AAPL <span class="fp-market-up">+0.8% ▲</span></span>
            <span class="fp-market-item">MSFT <span class="fp-market-up">+1.1% ▲</span></span>
            <span class="fp-market-item">JNJ <span class="fp-market-flat">0.0% —</span></span>
            <span class="fp-market-item">KO <span class="fp-market-up">+0.4% ▲</span></span>
            <span class="fp-market-item">WMT <span class="fp-market-down">-0.2% ▼</span></span>
            <span class="fp-market-item">VISA <span class="fp-market-up">+0.6% ▲</span></span>
        </div>
    </div>
    """
    st.markdown(_clean_html(market_html), unsafe_allow_html=True)

    topnav_html = f"""
    <div class="fp-topnav-shell">
        <div class="fp-brand-zone">
            <div class="fp-logo-symbol"></div>
            <div>
                <div class="fp-brand-name">FinPilot</div>
                <div class="fp-brand-sub">Marchés financiers · IA</div>
                <div class="fp-nav-caption">Copilote intelligent d'aide à la décision</div>
            </div>
        </div>

        <div class="fp-header-center">
            Analyse multicritère MCDA · recommandations explicables · simulation sans ordre réel
        </div>

        <div class="fp-header-cash">
            <div class="fp-header-cash-label">Cash disponible</div>
            <div class="fp-header-cash-value">{money_dollar(cash_balance)}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(topnav_html), unsafe_allow_html=True)

    nav_items = [
        ("Accueil", "app.py", "dashboard"),
        ("Analyse IA", "pages/analyse.py", "analyse"),
        ("Portefeuille", "pages/portefeuille.py", "portefeuille"),
        ("Historique", "pages/historique.py", "historique"),
        ("Profil", "pages/profil.py", "profil"),
        ("Progression", "pages/progression.py", "progression"),
        ("Avis", "pages/feedback.py", "feedback"),
    ]

    _uid = st.session_state.get("user_id")
    if _uid and is_user_admin(_uid):
        nav_items.append(("Admin", "pages/admin.py", "admin"))

    nav_cols = st.columns(len(nav_items) + 1, gap="small")

    for col, (label, page, page_key) in zip(nav_cols[:-1], nav_items):
        with col:
            _nav_button(label, page, f"topnav_{page_key}", active_page, page_key)

    with nav_cols[-1]:
        if st.button("Déconnexion", key="topnav_logout", use_container_width=True):
            if logout_callback:
                logout_callback()
            st.rerun()

    st.markdown('<div class="fp-after-nav-space"></div>', unsafe_allow_html=True)

    sidebar_data = {
        "dashboard": {
            "kicker": "Accueil",
            "title": "Vue générale FinPilot",
            "text": "Comprenez le rôle de l'application avant de lancer une analyse ou une simulation.",
        },
        "portefeuille": {
            "kicker": "Gestion portefeuille",
            "title": "Suivi des positions",
            "text": "Consultez vos positions, répartitions sectorielles et opérations simulées.",
        },
        "analyse": {
            "kicker": "Analyse IA",
            "title": "Scoring MCDA",
            "text": "Répondez au questionnaire et obtenez un Top 5 personnalisé et explicable.",
        },
        "historique": {
            "kicker": "Historique",
            "title": "Traçabilité",
            "text": "Retrouvez vos analyses, profils passés et ordres simulés.",
        },
        "profil": {
            "kicker": "Profil investisseur",
            "title": "Préférences utilisateur",
            "text": "Consultez les informations du compte et le profil détecté.",
        },
        "progression": {
            "kicker": "Gamification",
            "title": "Parcours FinPilot",
            "text": "Suivez vos niveaux, badges et options débloquées selon votre activité.",
        },
        "feedback": {
            "kicker": "Avis clients",
            "title": "Retour d'expérience",
            "text": "Partagez votre ressenti et consultez les retours utilisateurs.",
        },
        "admin": {
            "kicker": "Administration",
            "title": "Pilotage plateforme",
            "text": "Suivez les utilisateurs, analyses, ordres simulés et avis collectés.",
        },
    }

    current = sidebar_data.get(active_page, sidebar_data["dashboard"])

    with st.sidebar:
        sidebar_html = f"""
        <div class="sidebar-status-card">
            <div class="sidebar-status-kicker">{current["kicker"]}</div>
            <div class="sidebar-status-title">{current["title"]}</div>
            <div class="sidebar-status-text">{current["text"]}</div>

            <div class="sidebar-cash-box">
                <div class="sidebar-cash-label">Cash disponible</div>
                <div class="sidebar-cash-value">{money_dollar(cash_balance)}</div>
            </div>

            <div class="sidebar-mini-stage">
                <div class="sidebar-stage-grid"></div>
                <div class="sidebar-stage-bars">
                    <span></span><span></span><span></span><span></span><span></span><span></span>
                </div>
            </div>
        </div>

        <div class="sidebar-note">
            FinPilot est une application de simulation pédagogique : aucune opération réelle
            n'est envoyée vers un courtier externe.
        </div>
        """
        st.markdown(_clean_html(sidebar_html), unsafe_allow_html=True)
