import streamlit as st


def money_dollar(x):
    try:
        return f"{float(x):,.2f} $".replace(",", " ")
    except Exception:
        return "0.00 $"


def _clean_html(text: str) -> str:
    return "\n".join(line.strip() for line in text.strip().splitlines())


def render_sidebar(active_page="dashboard", cash_balance=5100.0, logout_callback=None):
    """
    Sidebar FinPilot premium commune à toutes les pages.

    active_page doit être :
    - "dashboard"
    - "portefeuille"
    - "analyse"
    - "historique"
    - "profil"
    """

    css = """
    <style>
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 20% 5%, rgba(47,124,255,.20), transparent 26%),
            radial-gradient(circle at 85% 92%, rgba(39,224,179,.10), transparent 28%),
            linear-gradient(180deg, #061633 0%, #08214A 55%, #071831 100%) !important;
        border-right: 1px solid rgba(255,255,255,.05);
        box-shadow: 18px 0 60px rgba(7,24,49,.22);
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.35rem !important;
        padding-left: .85rem !important;
        padding-right: .85rem !important;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
    }

    .sidebar-brand-wrap {
        display:flex;
        align-items:center;
        gap:.9rem;
        margin:.45rem 0 1.45rem 0;
        padding-bottom:1.05rem;
        border-bottom:1px solid rgba(255,255,255,.09);
        position:relative;
    }

    .fp-logo-symbol {
        width:50px;
        height:50px;
        border-radius:17px;
        background:
            radial-gradient(circle at 30% 28%, rgba(255,255,255,.24), transparent 22%),
            linear-gradient(135deg,#2F7CFF 0%,#23D8F0 55%,#27E0B3 100%);
        position:relative;
        box-shadow:0 14px 32px rgba(47,124,255,.30);
        flex-shrink:0;
    }

    .fp-logo-symbol::before {
        content:"";
        position:absolute;
        width:14px;
        height:36px;
        left:18px;
        top:7px;
        border-radius:999px;
        background:rgba(255,255,255,.27);
    }

    .fp-logo-symbol::after {
        content:"";
        position:absolute;
        width:36px;
        height:14px;
        left:7px;
        top:18px;
        border-radius:999px;
        background:rgba(255,255,255,.27);
    }

    .sidebar-logo-name {
        color:white;
        font-size:1.72rem;
        font-weight:900;
        letter-spacing:-.04em;
        line-height:1;
    }

    .sidebar-logo-sub {
        color:rgba(255,255,255,.76);
        font-size:.90rem;
        margin-top:.25rem;
    }

    div[data-testid="stSidebar"] .stButton > button {
        height:58px !important;
        border-radius:15px !important;
        font-weight:800 !important;
        font-size:1rem !important;
        border:1px solid rgba(255,255,255,.08) !important;
        background:rgba(255,255,255,.08) !important;
        color:white !important;
        justify-content:flex-start !important;
        padding-left:1rem !important;
        box-shadow:none !important;
        transition:all .18s ease !important;
    }

    div[data-testid="stSidebar"] .stButton > button:hover {
        background:rgba(255,255,255,.12) !important;
        transform:translateX(2px);
        border-color:rgba(255,255,255,.16) !important;
    }

    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background:linear-gradient(90deg,#2F7CFF,#7A3CFF) !important;
        color:white !important;
        box-shadow:0 16px 34px rgba(47,124,255,.28) !important;
        border:1px solid rgba(255,255,255,.16) !important;
    }

    .sidebar-visual-card {
        position:relative;
        overflow:hidden;
        margin-top:1.8rem;
        padding:1.15rem 1.1rem 1rem 1.1rem;
        border-radius:22px;
        border:1px solid rgba(99,171,255,.28);
        background:
            radial-gradient(circle at 90% 10%, rgba(122,60,255,.26), transparent 28%),
            radial-gradient(circle at 18% 85%, rgba(39,224,179,.12), transparent 28%),
            linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.04));
        box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 14px 36px rgba(0,0,0,.14);
        color:white;
    }

    .sidebar-visual-card::before {
        content:"";
        position:absolute;
        width:160px;
        height:160px;
        border-radius:50%;
        border:1px solid rgba(111,255,224,.12);
        top:-70px;
        right:-72px;
    }

    .sidebar-visual-card::after {
        content:"";
        position:absolute;
        width:74px;
        height:74px;
        border-radius:50%;
        background:radial-gradient(circle, rgba(111,255,224,.35), rgba(111,255,224,.04) 70%, transparent 72%);
        top:14px;
        right:18px;
        filter:blur(.2px);
    }

    .sidebar-visual-kicker {
        color:#83EFFF;
        font-size:.75rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.10em;
        position:relative;
        z-index:2;
    }

    .sidebar-visual-title {
        font-size:1.08rem;
        font-weight:900;
        margin-top:.35rem;
        position:relative;
        z-index:2;
        color:white;
    }

    .sidebar-visual-text {
        margin-top:.45rem;
        color:rgba(255,255,255,.78);
        line-height:1.5;
        font-size:.88rem;
        position:relative;
        z-index:2;
    }

    .sidebar-mini-stage {
        position:relative;
        height:106px;
        margin-top:1rem;
        border-radius:18px;
        overflow:hidden;
        background:linear-gradient(180deg, rgba(6,24,51,.42), rgba(255,255,255,.03));
        border:1px solid rgba(255,255,255,.06);
    }

    .sidebar-stage-grid {
        position:absolute;
        inset:0;
        background:
            linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
        background-size:20px 20px;
        opacity:.7;
    }

    .sidebar-stage-bars {
        position:absolute;
        right:12px;
        bottom:10px;
        display:flex;
        align-items:flex-end;
        gap:6px;
    }

    .sidebar-stage-bars span {
        width:10px;
        border-radius:999px 999px 2px 2px;
        background:linear-gradient(180deg, rgba(111,255,224,.80), rgba(47,124,255,.18));
        box-shadow:0 0 12px rgba(111,255,224,.12);
        animation:sidebarBarFloat 2.8s ease-in-out infinite;
    }

    .sidebar-stage-bars span:nth-child(1){height:22px; animation-delay:0s;}
    .sidebar-stage-bars span:nth-child(2){height:34px; animation-delay:.15s;}
    .sidebar-stage-bars span:nth-child(3){height:48px; animation-delay:.3s;}
    .sidebar-stage-bars span:nth-child(4){height:62px; animation-delay:.45s;}
    .sidebar-stage-bars span:nth-child(5){height:44px; animation-delay:.6s;}
    .sidebar-stage-bars span:nth-child(6){height:72px; animation-delay:.75s;}

    .sidebar-stage-line {
        position:absolute;
        border-top:3px solid #66EEFF;
        border-radius:999px;
        opacity:.95;
        filter:drop-shadow(0 0 8px rgba(102,238,255,.4));
    }

    .sidebar-line-a {
        width:82px;
        height:32px;
        left:16px;
        top:42px;
        transform:rotate(-12deg);
        border-left:3px solid transparent;
        border-right:3px solid transparent;
        animation:sidebarWaveA 4.8s ease-in-out infinite;
    }

    .sidebar-line-b {
        width:88px;
        height:40px;
        left:82px;
        top:28px;
        transform:rotate(12deg);
        border-left:3px solid transparent;
        border-right:3px solid transparent;
        animation:sidebarWaveB 4.8s ease-in-out infinite;
    }

    .sidebar-stage-dot {
        position:absolute;
        width:9px;
        height:9px;
        border-radius:50%;
        background:#BFFFFF;
        box-shadow:0 0 12px rgba(191,255,255,.72);
        animation:sidebarDotPulse 2.5s ease-in-out infinite;
    }

    .sidebar-stage-dot.dot1 { left:70px; top:46px; }
    .sidebar-stage-dot.dot2 { left:120px; top:36px; animation-delay:.5s; }
    .sidebar-stage-dot.dot3 { left:156px; top:50px; animation-delay:1s; }

    .sidebar-figure-wrap {
        position:absolute;
        left:14px;
        bottom:12px;
        width:44px;
        height:44px;
    }

    .figure-dashboard,
    .figure-wallet,
    .figure-analysis,
    .figure-history,
    .figure-profile {
        width:44px;
        height:44px;
        position:relative;
    }

    .figure-dashboard::before,
    .figure-wallet::before,
    .figure-analysis::before,
    .figure-history::before,
    .figure-profile::before {
        content:"";
        position:absolute;
        inset:0;
        border-radius:14px;
        background:linear-gradient(135deg, rgba(47,124,255,.9), rgba(122,60,255,.88));
        box-shadow:0 10px 20px rgba(0,0,0,.16);
    }

    .figure-dashboard::after {
        content:"";
        position:absolute;
        left:10px;
        top:12px;
        width:24px;
        height:18px;
        border-left:3px solid #fff;
        border-bottom:3px solid #fff;
        transform:skewX(-20deg);
        border-radius:2px;
    }

    .figure-wallet::after {
        content:"";
        position:absolute;
        left:9px;
        top:13px;
        width:26px;
        height:18px;
        border:3px solid #fff;
        border-radius:7px;
        box-sizing:border-box;
        box-shadow: inset -7px 0 0 rgba(255,255,255,.16);
    }

    .figure-analysis::after {
        content:"";
        position:absolute;
        left:10px;
        bottom:10px;
        width:4px;
        height:12px;
        background:#fff;
        border-radius:3px;
        box-shadow:
            8px -6px 0 0 #fff,
            16px -14px 0 0 #fff;
    }

    .figure-history::after {
        content:"";
        position:absolute;
        left:11px;
        top:11px;
        width:22px;
        height:22px;
        border:3px solid #fff;
        border-radius:50%;
        box-sizing:border-box;
    }

    .figure-history span {
        position:absolute;
        width:12px;
        height:3px;
        border-radius:99px;
        background:white;
        left:21px;
        top:22px;
        transform:rotate(28deg);
        z-index:2;
    }

    .figure-profile::after {
        content:"";
        position:absolute;
        left:14px;
        top:9px;
        width:16px;
        height:16px;
        border-radius:50%;
        background:#fff;
        box-shadow: 0 18px 0 4px rgba(255,255,255,.95);
    }

    .sidebar-chip-row {
        display:flex;
        gap:.5rem;
        flex-wrap:wrap;
        margin-top:.95rem;
        position:relative;
        z-index:2;
    }

    .sidebar-chip {
        padding:.42rem .7rem;
        border-radius:999px;
        background:rgba(255,255,255,.09);
        border:1px solid rgba(255,255,255,.08);
        color:white;
        font-size:.79rem;
        font-weight:800;
    }

    .sidebar-note {
        margin-top:.95rem;
        color:rgba(255,255,255,.54);
        font-size:.78rem;
        line-height:1.45;
    }

    @keyframes sidebarBarFloat {
        0%,100% { transform:translateY(0); opacity:.92; }
        50% { transform:translateY(-4px); opacity:1; }
    }

    @keyframes sidebarWaveA {
        0%,100% { transform:translateY(0) rotate(-12deg); }
        50% { transform:translateY(-3px) rotate(-9deg); }
    }

    @keyframes sidebarWaveB {
        0%,100% { transform:translateY(0) rotate(12deg); }
        50% { transform:translateY(-2px) rotate(15deg); }
    }

    @keyframes sidebarDotPulse {
        0%,100% { transform:scale(1); opacity:.9; }
        50% { transform:scale(1.35); opacity:1; }
    }
    </style>
    """

    st.markdown(_clean_html(css), unsafe_allow_html=True)

    sidebar_data = {
        "dashboard": {
            "kicker": "Espace investisseur",
            "title": "Vue dashboard",
            "text": "Suivez votre situation globale, votre cash et vos indicateurs clés dans une interface claire.",
            "figure": "figure-dashboard",
        },
        "portefeuille": {
            "kicker": "Gestion portefeuille",
            "title": "Suivi des positions",
            "text": "Consultez vos positions, répartitions sectorielles et opérations simulées dans une vue structurée.",
            "figure": "figure-wallet",
        },
        "analyse": {
            "kicker": "Analyse IA",
            "title": "Scoring intelligent",
            "text": "Répondez au questionnaire investisseur et obtenez des recommandations avec score MCDA.",
            "figure": "figure-analysis",
        },
        "historique": {
            "kicker": "Historique",
            "title": "Traçabilité",
            "text": "Retrouvez vos analyses, vos profils passés et vos opérations dans une chronologie lisible.",
            "figure": "figure-history",
        },
        "profil": {
            "kicker": "Profil",
            "title": "Compte investisseur",
            "text": "Gérez votre profil, vos préférences et vos réglages dans un espace simple et moderne.",
            "figure": "figure-profile",
        },
        "feedback": {
            "kicker": "Avis & Retours",
            "title": "Votre expérience",
            "text": "Partagez votre ressenti après simulation et consultez les retours de la communauté.",
            "figure": "figure-profile",
        },
    }

    current = sidebar_data.get(active_page, sidebar_data["dashboard"])

    with st.sidebar:
        st.markdown(
            _clean_html("""
            <div class="sidebar-brand-wrap">
                <div class="fp-logo-symbol"></div>
                <div>
                    <div class="sidebar-logo-name">FinPilot</div>
                    <div class="sidebar-logo-sub">Marchés · IA</div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        nav_pages = [
            ("▦  Tableau de bord", "app.py", "dashboard"),
            ("◫  Portefeuille", "pages/portefeuille.py", "portefeuille"),
            ("◉  Analyses IA", "pages/analyse.py", "analyse"),
            ("◷  Historique", "pages/historique.py", "historique"),
            ("◎  Profil", "pages/profil.py", "profil"),
            ("◈  Avis", "pages/feedback.py", "feedback"),
        ]

        for label, page, page_key in nav_pages:
            is_current = active_page == page_key
            if st.button(
                label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
            ):
                if active_page != page_key:
                    st.switch_page(page)

        visual_html = f"""
        <div class="sidebar-visual-card">
            <div class="sidebar-visual-kicker">{current["kicker"]}</div>
            <div class="sidebar-visual-title">{current["title"]}</div>
            <div class="sidebar-visual-text">{current["text"]}</div>

            <div class="sidebar-mini-stage">
                <div class="sidebar-stage-grid"></div>
                <div class="sidebar-stage-line sidebar-line-a"></div>
                <div class="sidebar-stage-line sidebar-line-b"></div>
                <div class="sidebar-stage-dot dot1"></div>
                <div class="sidebar-stage-dot dot2"></div>
                <div class="sidebar-stage-dot dot3"></div>
                <div class="sidebar-stage-bars">
                    <span></span><span></span><span></span><span></span><span></span><span></span>
                </div>
                <div class="sidebar-figure-wrap">
                    <div class="{current["figure"]}"><span></span></div>
                </div>
            </div>

            <div class="sidebar-chip-row">
                <div class="sidebar-chip">Cash : {money_dollar(cash_balance)}</div>
                <div class="sidebar-chip">Libre-service</div>
            </div>
        </div>

        <div class="sidebar-note">
            FinPilot est une application de simulation pédagogique :
            aucune opération réelle n’est envoyée vers un courtier externe.
        </div>
        """

        st.markdown(_clean_html(visual_html), unsafe_allow_html=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        if st.button("Déconnexion", key="btn_logout", use_container_width=True):
            if logout_callback:
                logout_callback()
            st.rerun()