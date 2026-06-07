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


def render_sidebar(active_page="dashboard", cash_balance=5100.0, logout_callback=None):
    """
    Navigation commune FinPilot.

    active_page :
    - "dashboard"     -> Accueil
    - "assistant"     -> Assistant IA
    - "analyse"       -> Analyse IA
    - "portefeuille"  -> Portefeuille
    - "historique"    -> Historique
    - "profil"        -> Profil
    - "progression"   -> Progression
    - "feedback"      -> Avis
    - "admin"         -> Admin
    """

    # Detect query-param based logout
    if st.query_params.get("logout") == "true":
        st.query_params.clear()
        if logout_callback:
            logout_callback()
        st.rerun()

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
       HEADER — COMPACT ET DESIGN PREMIUM MOCKUP
       ====================================================== */

    .fp-topnav-shell {
        position: relative;
        width: 100%;
        min-height: 85px;
        background: linear-gradient(90deg, #020C1B 0%, #081B33 50%, #020C1B 100%);
        border-bottom: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 12px 32px rgba(6,22,51,.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 1.5rem;
        margin-bottom: 0.8rem;
        overflow: hidden;
        border-radius: 16px;
    }

    .header-wave {
        position: absolute;
        bottom: 0;
        left: 10%;
        right: 15%;
        width: 75%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    }

    .fp-brand-zone {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        position: relative;
        z-index: 2;
    }

    .fp-logo-symbol {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: linear-gradient(135deg, #2F7CFF 0%, #23D8F0 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 20px rgba(47,124,255,0.3);
        flex-shrink: 0;
    }

    .fp-brand-name {
        color: white;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: -.03em;
        line-height: 1.1;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    .fp-brand-sub {
        color: rgba(255,255,255,.7);
        font-size: .8rem;
        font-weight: 500;
        line-height: 1.1;
    }

    .fp-nav-caption {
        color: #23D8F0;
        font-size: .65rem;
        font-weight: 700;
        letter-spacing: .05em;
        text-transform: uppercase;
        margin-top: .15rem;
    }

    /* CARD CASH DISPONIBLE */
    .fp-header-cash {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 0.6rem 1.2rem;
        color: white;
        position: relative;
        z-index: 2;
        min-width: 190px;
        backdrop-filter: blur(10px);
    }

    .fp-cash-indicator {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 6px;
        height: 6px;
        background-color: #23D8F0;
        border-radius: 50%;
        box-shadow: 0 0 8px #23D8F0;
    }

    .fp-header-cash-icon {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .fp-header-cash-info {
        display: flex;
        flex-direction: column;
    }

    .fp-header-cash-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        line-height: 1.2;
    }

    .fp-header-cash-value {
        margin-top: .15rem;
        color: white;
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.2;
        font-family: 'Sora', 'Inter', sans-serif;
    }

    /* ======================================================
       HTML NAVBAR REDESIGN
       ====================================================== */
    .fp-navbar {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 0.5rem;
        padding: 0.5rem 0.2rem;
        margin-bottom: 1rem;
        width: 100%;
        -webkit-overflow-scrolling: touch;
    }

    .fp-navbar::-webkit-scrollbar {
        display: none;
    }

    .fp-nav-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.1rem;
        border-radius: 30px;
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.8);
        color: #4A5568 !important;
        font-size: 0.88rem;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.2s ease;
        white-space: nowrap;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .fp-nav-link:hover {
        transform: translateY(-1px);
        background: #F7FAFC;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .fp-nav-link svg {
        stroke: #718096;
        transition: stroke 0.2s ease;
    }

    .fp-nav-link:hover svg {
        stroke: #4A5568;
    }

    .fp-nav-link.active {
        background: linear-gradient(135deg, #2F7CFF, #23D8F0) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        box-shadow: 0 10px 20px rgba(47,124,255,0.25) !important;
    }

    .fp-nav-link.active svg {
        stroke: #FFFFFF !important;
    }

    .fp-nav-link.active:hover {
        filter: brightness(1.05);
    }

    /* SIDEBAR NATIVE REMOVAL */
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    .main .block-container {
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
    }

    @media (max-width: 900px) {
        .fp-topnav-shell {
            flex-direction: column;
            gap: 1rem;
            align-items: flex-start;
        }
        .fp-header-cash {
            width: 100%;
        }
        .header-wave {
            display: none;
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

    logo_svg = """<svg width="22" height="22" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="0"><path d="M12 2c0 5.523 4.477 10 10 10-5.523 0-10 4.477-10 10 0-5.523-4.477-10-10-10 5.523 0 10-4.477 10-10z"></path></svg>"""

    waveform_svg = """
    <svg class="header-wave" viewBox="0 0 800 120" preserveAspectRatio="none">
      <line x1="100" y1="0" x2="100" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="200" y1="0" x2="200" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="300" y1="0" x2="300" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="400" y1="0" x2="400" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="500" y1="0" x2="500" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="600" y1="0" x2="600" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <line x1="700" y1="0" x2="700" y2="120" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
      <path d="M 0,100 C 150,90 200,110 300,70 C 400,30 450,95 500,40 C 550,-15 620,110 700,50 C 750,15 780,45 800,20" fill="none" stroke="rgba(35, 216, 240, 0.4)" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M 0,100 C 150,90 200,110 300,70 C 400,30 450,95 500,40 C 550,-15 620,110 700,50 C 750,15 780,45 800,20 L 800,120 L 0,120 Z" fill="url(#wave-gradient)" opacity="0.15"/>
      <defs>
        <linearGradient id="wave-gradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#23D8F0"/>
          <stop offset="100%" stop-color="#23D8F0" stop-opacity="0"/>
        </linearGradient>
      </defs>
    </svg>
    """

    wallet_svg = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#23D8F0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>"""

    topnav_html = f"""
    <div class="fp-topnav-shell">
        {waveform_svg}
        <div class="fp-brand-zone">
            <div class="fp-logo-symbol">
                {logo_svg}
            </div>
            <div>
                <div class="fp-brand-name">FinPilot</div>
                <div class="fp-brand-sub">Marchés financiers · IA</div>
                <div class="fp-nav-caption">Copilote intelligent d'aide à la décision</div>
            </div>
        </div>

        <div class="fp-header-cash">
            <div class="fp-cash-indicator"></div>
            <div class="fp-header-cash-icon">
                {wallet_svg}
            </div>
            <div class="fp-header-cash-info">
                <div class="fp-header-cash-label">Cash disponible</div>
                <div class="fp-header-cash-value">{money_dollar(cash_balance)}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(_clean_html(topnav_html), unsafe_allow_html=True)

    svg_home = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>"""
    svg_robot = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><rect x="4" y="8" width="16" height="12" rx="4"/><circle cx="9" cy="14" r="1" fill="currentColor"/><circle cx="15" cy="14" r="1" fill="currentColor"/></svg>"""
    svg_chart = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""
    svg_wallet = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>"""
    svg_clock = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>"""
    svg_user = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>"""
    svg_trophy = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.45 1-1 1H4v2h16v-2h-5c-.55 0-1-.45-1-1v-2.34"></path><path d="M12 2a6 6 0 0 1 6 6v5a6 6 0 0 1-6 6 6 6 0 0 1-6-6V8a6 6 0 0 1 6-6Z"></path></svg>"""
    svg_star = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>"""
    svg_shield = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>"""
    svg_logout = """<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>"""

    nav_items = [
        ("Accueil", "/", "dashboard", svg_home),
        ("Assistant IA", "/assistant", "assistant", svg_robot),
        ("Analyse IA", "/analyse", "analyse", svg_chart),
        ("Portefeuille", "/portefeuille", "portefeuille", svg_wallet),
        ("Historique", "/historique", "historique", svg_clock),
        ("Profil", "/profil", "profil", svg_user),
        ("Progression", "/progression", "progression", svg_trophy),
        ("Avis", "/feedback", "feedback", svg_star),
    ]

    _uid = st.session_state.get("user_id")
    if _uid and is_user_admin(_uid):
        nav_items.append(("Admin", "/admin", "admin", svg_shield))

    nav_html = '<div class="fp-navbar">'
    for label, url, page_key, svg_code in nav_items:
        is_active = (active_page == page_key)
        active_class = "active" if is_active else ""
        nav_html += f"""
        <a href="{url}" class="fp-nav-link {active_class}" target="_self">
            {svg_code}
            <span>{label}</span>
        </a>
        """

    nav_html += f"""
    <a href="/?logout=true" class="fp-nav-link" target="_self">
        {svg_logout}
        <span>Déconnexion</span>
    </a>
    """
    nav_html += '</div>'
    st.markdown(_clean_html(nav_html), unsafe_allow_html=True)


