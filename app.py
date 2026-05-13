import streamlit as st
import plotly.graph_objects as go
from textwrap import dedent

from auth import init_auth_state, render_auth_screen, logout
from database import (
    init_db,
    get_user_cash_balance,
    load_user_history,
    load_user_recommended_actions,
    get_portfolio_positions,
    has_user_capital_configured,
    set_user_initial_capital,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar
from utils import get_history_summary, get_risk_score


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Accueil",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    render_auth_screen()
    st.stop()


# ============================================================
# HTML HELPER
# ============================================================

def html(content: str):
    cleaned = "\n".join(line.strip() for line in dedent(content).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def money(value):
    try:
        return f"{float(value):,.2f}".replace(",", " ")
    except Exception:
        return "0.00"


def money_dollar(value):
    return f"{money(value)} $"


def safe_username():
    username = (
        st.session_state.get("user_name")
        or st.session_state.get("username")
        or st.session_state.get("email")
        or "Investisseur"
    )
    username = str(username).strip()
    if "@" in username:
        username = username.split("@")[0]
    return username[:1].upper() + username[1:] if username else "Investisseur"


# ============================================================
# PAGE CAPITAL INITIAL
# ============================================================

def render_capital_setup(user_id):
    if "capital_form_value" not in st.session_state:
        st.session_state.capital_form_value = 5000.0

    if "capital_quick_choice" not in st.session_state:
        st.session_state.capital_quick_choice = "5 000 $"

    if "capital_last_choice" not in st.session_state:
        st.session_state.capital_last_choice = st.session_state.capital_quick_choice

    preset_values = {
        "1 000 $": 1000.0,
        "5 000 $": 5000.0,
        "10 000 $": 10000.0,
        "25 000 $": 25000.0,
        "50 000 $": 50000.0,
        "100 000 $": 100000.0,
    }

    html("""
    <style>
    [data-testid="stSidebar"] { display:none !important; }
    .block-container {
        max-width: 1450px !important;
        padding-top: 2.4rem !important;
    }
    .capital-hero-card {
        background:
            radial-gradient(circle at 92% 18%, rgba(255,255,255,0.16), transparent 30%),
            linear-gradient(135deg, #061633 0%, #0B2F78 48%, #2F7CFF 100%);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 30px;
        padding: 2.4rem 2.5rem;
        color: white;
        min-height: 300px;
        box-shadow: 0 24px 65px rgba(14,56,150,0.20);
        position: relative;
        overflow: hidden;
    }
    .capital-hero-label {
        color:#62E6FF;
        text-transform:uppercase;
        letter-spacing:.10em;
        font-weight:900;
        font-size:.92rem;
        margin-bottom:.85rem;
    }
    .capital-hero-title {
        font-size:3.2rem;
        line-height:1.05;
        font-weight:900;
        letter-spacing:-.055em;
        margin-bottom:1rem;
    }
    .capital-hero-text {
        max-width:850px;
        color:rgba(255,255,255,.90);
        font-size:1.08rem;
        line-height:1.7;
    }
    .capital-chip-row {
        display:flex;
        gap:.7rem;
        flex-wrap:wrap;
        margin-top:1.3rem;
    }
    .capital-chip {
        padding:.55rem .95rem;
        border-radius:999px;
        color:white;
        background:rgba(255,255,255,.14);
        border:1px solid rgba(255,255,255,.17);
        font-weight:800;
    }
    .capital-side-panel,
    .capital-feature-card,
    .capital-form-card,
    .capital-preview-box {
        background:rgba(255,255,255,.96);
        border:1px solid #DDE8F7;
        border-radius:26px;
        box-shadow:0 16px 44px rgba(21,54,108,.09);
    }
    .capital-side-panel {
        padding:1.8rem;
        min-height:300px;
    }
    .capital-side-label,
    .capital-form-label,
    .capital-preview-label {
        color:#2F7CFF;
        text-transform:uppercase;
        letter-spacing:.08em;
        font-weight:900;
        font-size:.84rem;
    }
    .capital-side-amount,
    .capital-preview-value {
        color:#10233F;
        font-size:2.35rem;
        font-weight:900;
        margin:.45rem 0;
    }
    .capital-side-subtitle,
    .capital-form-text,
    .capital-preview-text,
    .capital-feature-text {
        color:#64748B;
        line-height:1.6;
    }
    .capital-side-mini-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:.8rem;
        margin-top:1rem;
    }
    .capital-side-mini-card {
        background:#F6FAFF;
        border:1px solid #E0EAF8;
        border-radius:16px;
        padding:.9rem;
    }
    .capital-side-mini-title {
        color:#7890AD;
        font-size:.78rem;
        font-weight:900;
        text-transform:uppercase;
    }
    .capital-side-mini-value {
        color:#10233F;
        font-weight:900;
        margin-top:.25rem;
    }
    .capital-feature-card {
        padding:1.3rem;
        height:100%;
        border-top:5px solid #2F7CFF;
    }
    .capital-feature-number {
        width:42px;
        height:42px;
        border-radius:50%;
        display:flex;
        align-items:center;
        justify-content:center;
        background:linear-gradient(135deg,#2F7CFF,#31E6A8);
        color:white;
        font-weight:900;
        margin-bottom:.85rem;
    }
    .capital-feature-title,
    .capital-form-title {
        color:#10233F;
        font-weight:900;
        letter-spacing:-.035em;
    }
    .capital-feature-title { font-size:1.25rem; }
    .capital-form-card {
        padding:1.55rem 1.65rem;
        margin-bottom:1rem;
    }
    .capital-form-title { font-size:1.8rem; margin:.35rem 0; }
    .capital-preview-box {
        padding:1.2rem;
        min-height:128px;
        background:linear-gradient(135deg,rgba(47,124,255,.10),rgba(122,60,255,.10));
    }
    .capital-note {
        background:linear-gradient(135deg,rgba(47,124,255,.10),rgba(49,230,168,.10));
        border:1px solid #D9E8F7;
        border-radius:18px;
        padding:1rem;
        color:#47607E;
        margin-top:.85rem;
    }
    div[data-testid="stRadio"] {
        background:rgba(255,255,255,.75);
        border:1px solid #DCE6F4;
        padding:.8rem 1rem;
        border-radius:18px;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        min-height:58px;
        border-radius:18px;
        border:none;
        font-weight:900;
        background:linear-gradient(90deg,#2F7CFF,#6C63FF) !important;
        box-shadow:0 12px 26px rgba(47,124,255,.24);
    }
    </style>
    """)

    hero_left, hero_right = st.columns([1.45, 0.95], gap="large")

    with hero_left:
        html("""
        <div class="capital-hero-card">
            <div class="capital-hero-label">Configuration initiale</div>
            <div class="capital-hero-title">Activez votre espace d’investissement</div>
            <div class="capital-hero-text">
                Choisissez le capital de simulation avec lequel vous souhaitez commencer.
                Ce montant devient votre cash initial pour vos achats, vos ventes
                et le suivi de votre portefeuille.
            </div>
            <div class="capital-chip-row">
                <div class="capital-chip">Aucun capital imposé</div>
                <div class="capital-chip">Configuration de départ</div>
                <div class="capital-chip">Portefeuille propre</div>
            </div>
        </div>
        """)

    with hero_right:
        current_preview = float(st.session_state.capital_form_value)
        html(f"""
        <div class="capital-side-panel">
            <div class="capital-side-label">Aperçu du départ</div>
            <div class="capital-side-amount">{money_dollar(current_preview)}</div>
            <div class="capital-side-subtitle">Cash initial disponible</div>
            <div class="capital-side-mini-grid">
                <div class="capital-side-mini-card">
                    <div class="capital-side-mini-title">Mode</div>
                    <div class="capital-side-mini-value">Simulation réaliste</div>
                </div>
                <div class="capital-side-mini-card">
                    <div class="capital-side-mini-title">Départ</div>
                    <div class="capital-side-mini-value">Sans positions</div>
                </div>
                <div class="capital-side-mini-card">
                    <div class="capital-side-mini-title">Objectif</div>
                    <div class="capital-side-mini-value">Construire votre portefeuille</div>
                </div>
                <div class="capital-side-mini-card">
                    <div class="capital-side-mini-title">Règle</div>
                    <div class="capital-side-mini-value">1 client = 1 capital</div>
                </div>
            </div>
        </div>
        """)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")
    cards = [
        ("01", "Capital personnel", "Chaque utilisateur démarre avec son propre montant, selon son budget ou sa stratégie."),
        ("02", "Cash initial", "Le montant choisi devient immédiatement le cash disponible pour vos futures opérations."),
        ("03", "Réinitialisation propre", "Les anciennes positions et les anciens ordres sont supprimés pour repartir correctement."),
    ]

    for col, (num, title, text) in zip([c1, c2, c3], cards):
        with col:
            html(f"""
            <div class="capital-feature-card">
                <div class="capital-feature-number">{num}</div>
                <div class="capital-feature-title">{title}</div>
                <div class="capital-feature-text">{text}</div>
            </div>
            """)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    outer_left, outer_center, outer_right = st.columns([0.18, 1, 0.18])

    with outer_center:
        html("""
        <div class="capital-form-card">
            <div class="capital-form-label">Étape finale</div>
            <div class="capital-form-title">Choisissez votre capital de départ</div>
            <div class="capital-form-text">
                Sélectionnez un montant rapide ou saisissez une valeur personnalisée.
                Cette configuration sera utilisée pour initialiser votre portefeuille.
            </div>
        </div>
        """)

        options = ["1 000 $", "5 000 $", "10 000 $", "25 000 $", "50 000 $", "100 000 $", "Personnalisé"]

        choice = st.radio(
            "Montants rapides",
            options,
            horizontal=True,
            key="capital_quick_choice",
            label_visibility="collapsed",
        )

        if choice != st.session_state.capital_last_choice:
            if choice != "Personnalisé":
                st.session_state.capital_form_value = preset_values[choice]
            st.session_state.capital_last_choice = choice

        box1, box2 = st.columns([1.1, 0.9], gap="large")

        with box1:
            st.number_input(
                "Capital initial ($)",
                min_value=100.0,
                max_value=10000000.0,
                step=100.0,
                key="capital_form_value",
                help="Montant utilisé comme cash de départ.",
            )

        with box2:
            html(f"""
            <div class="capital-preview-box">
                <div class="capital-preview-label">Aperçu immédiat</div>
                <div class="capital-preview-value">{money_dollar(float(st.session_state.capital_form_value))}</div>
                <div class="capital-preview-text">
                    Ce montant sera visible comme cash disponible après validation.
                </div>
            </div>
            """)

        confirmation = st.checkbox(
            "Je confirme que ce montant sera utilisé comme capital initial de mon portefeuille.",
            key="capital_confirmation",
        )

        if st.button("Initialiser mon portefeuille", use_container_width=True, type="primary", key="init_portfolio"):
            if not confirmation:
                st.error("Veuillez confirmer le capital choisi avant de continuer.")
            else:
                try:
                    capital = float(st.session_state.capital_form_value)
                    set_user_initial_capital(user_id, capital, reset_portfolio=True)
                    st.success(f"Votre portefeuille a été initialisé avec {money_dollar(capital)}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Impossible d'enregistrer le capital : {e}")

        html("""
        <div class="capital-note">
            Cette action initialise votre portefeuille et supprime les anciennes données
            de démonstration pour repartir sur une base propre.
        </div>
        """)


# ============================================================
# STYLE ACCUEIL PREMIUM
# ============================================================

def inject_dashboard_style():
    html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --navy:#061633;
        --navy2:#092552;
        --blue:#2F7CFF;
        --purple:#7A3CFF;
        --cyan:#25D9F2;
        --green:#31D79B;
        --orange:#FF9B16;
        --text:#10233F;
        --muted:#64748B;
        --line:#DDE8F7;
    }

    html, body, .stApp {
        font-family:'Inter', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 6% 2%, rgba(47,124,255,.11), transparent 28%),
            radial-gradient(circle at 98% 4%, rgba(48,225,176,.14), transparent 30%),
            linear-gradient(135deg,#F8FBFF 0%,#EEF4FF 48%,#F8FFFD 100%) !important;
    }

    #MainMenu, footer, header, [data-testid="stSidebarNav"] {
        visibility:hidden !important;
        display:none !important;
    }

    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#061633 0%,#092552 48%,#061833 100%) !important;
        box-shadow:16px 0 60px rgba(6,22,51,.18);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top:2rem !important;
    }

    .main .block-container {
        max-width:1460px !important;
        padding:0rem 1.45rem 2rem 1.45rem !important;
    }

    .sidebar-brand-wrap {
        display:flex;
        align-items:center;
        gap:.9rem;
        margin:.6rem 0 1.9rem 0;
    }

    .fp-logo-symbol {
        width:48px;
        height:48px;
        border-radius:15px;
        background:linear-gradient(135deg,#2F7CFF,#27E0B3);
        position:relative;
        box-shadow:0 12px 28px rgba(47,124,255,.30);
    }

    .fp-logo-symbol::before {
        content:"";
        position:absolute;
        width:13px;
        height:36px;
        left:17.5px;
        top:6px;
        border-radius:999px;
        background:rgba(255,255,255,.25);
    }

    .fp-logo-symbol::after {
        content:"";
        position:absolute;
        width:36px;
        height:13px;
        left:6px;
        top:17.5px;
        border-radius:999px;
        background:rgba(255,255,255,.25);
    }

    .sidebar-logo-name {
        color:white;
        font-size:1.7rem;
        font-weight:900;
        letter-spacing:-.04em;
        line-height:1;
    }

    .sidebar-logo-sub {
        color:rgba(255,255,255,.78);
        font-size:.92rem;
        margin-top:.25rem;
    }

    div[data-testid="stSidebar"] .stButton > button {
        height:58px !important;
        border-radius:14px !important;
        font-weight:800 !important;
        font-size:1rem !important;
        border:1px solid rgba(255,255,255,.08) !important;
        background:rgba(255,255,255,.08) !important;
        color:white !important;
        justify-content:flex-start !important;
        padding-left:1rem !important;
        box-shadow:none !important;
    }

    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background:linear-gradient(90deg,#2F7CFF,#7A3CFF) !important;
        color:white !important;
        box-shadow:0 16px 34px rgba(47,124,255,.28) !important;
    }

    .premium-box {
        margin-top:2rem;
        padding:1.25rem 1.35rem;
        border-radius:18px;
        border:1px solid rgba(87,160,255,.32);
        background:rgba(255,255,255,.045);
        color:white;
    }

    .premium-title {
        display:flex;
        justify-content:space-between;
        font-size:1.05rem;
        font-weight:900;
        margin-bottom:.7rem;
    }

    .premium-text {
        color:rgba(255,255,255,.78);
        line-height:1.55;
        font-size:.92rem;
    }

    .premium-cash {
        margin-top:1.1rem;
        color:#6FFFE0;
        font-weight:900;
    }


    [data-testid="stAppViewContainer"] > .main {
        padding-top:0 !important;
    }

    section.main > div {
        padding-top:0 !important;
    }

    div.block-container {
        padding-top:0 !important;
    }

    .element-container:has(.hero-premium) {
        margin-top:0 !important;
    }


    .hero-premium {
        position:relative;
        overflow:hidden;
        min-height:245px;
        width:100%;
        border-radius:0 0 28px 28px;
        padding:2.7rem 3.3rem 2.15rem 3.3rem;
        margin:0 0 1.15rem 0;
        background:
            radial-gradient(circle at 95% 28%, rgba(122,60,255,.72), transparent 22%),
            radial-gradient(circle at 87% 45%, rgba(47,124,255,.50), transparent 34%),
            linear-gradient(135deg,#05122D 0%,#09286C 43%,#176BFF 100%);
        color:white;
        box-shadow:0 26px 75px rgba(14,56,150,.20);
        border:1px solid rgba(255,255,255,.12);
    }

    .hero-premium::after {
        content:"";
        position:absolute;
        width:430px;
        height:430px;
        border:7px solid rgba(47,124,255,.20);
        border-radius:50%;
        right:-92px;
        top:-172px;
        animation:heroPulse 6s ease-in-out infinite;
    }

    .hero-premium::before {
        content:"";
        position:absolute;
        width:92px;
        height:92px;
        background:linear-gradient(135deg,#2F7CFF,#7A3CFF);
        border-radius:50%;
        right:115px;
        top:78px;
        opacity:.88;
        box-shadow:0 0 48px rgba(101,240,255,.28);
        animation:heroOrb 5.5s ease-in-out infinite;
    }

    @keyframes heroPulse {
        0%,100% { transform:scale(1); opacity:.55; }
        50% { transform:scale(1.08); opacity:.85; }
    }

    @keyframes heroOrb {
        0%,100% { transform:translateY(0); }
        50% { transform:translateY(-10px); }
    }

    .hero-premium h1 {
        position:relative;
        z-index:4;
        font-size:2.15rem;
        letter-spacing:-.045em;
        margin:0 0 .75rem 0;
        font-weight:900;
    }

    .hero-premium p {
        position:relative;
        z-index:4;
        max-width:670px;
        font-size:1.02rem;
        line-height:1.55;
        margin:0;
        color:rgba(255,255,255,.93);
        font-weight:650;
    }

    .hero-badges {
        position:relative;
        z-index:4;
        display:flex;
        gap:1rem;
        flex-wrap:wrap;
        margin-top:1.25rem;
    }

    .hero-badge {
        padding:.58rem 1.08rem;
        background:rgba(255,255,255,.13);
        border:1px solid rgba(255,255,255,.16);
        border-radius:999px;
        font-weight:900;
        color:white;
        box-shadow:inset 0 1px 0 rgba(255,255,255,.10);
    }

    .hero-schema {
        position:absolute;
        right:0;
        top:0;
        bottom:0;
        width:54%;
        z-index:2;
        pointer-events:none;
        overflow:hidden;
        opacity:.98;
    }

    .schema-grid {
        position:absolute;
        inset:0;
        background:
            linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.038) 1px, transparent 1px);
        background-size:42px 42px;
        mask-image:linear-gradient(90deg, transparent 0%, black 20%, black 100%);
    }

    .schema-bars {
        position:absolute;
        right:155px;
        bottom:34px;
        display:flex;
        align-items:flex-end;
        gap:10px;
        height:150px;
        opacity:.55;
    }

    .schema-bar {
        width:13px;
        border-radius:10px 10px 0 0;
        background:linear-gradient(180deg, rgba(85,223,255,.95), rgba(47,124,255,.10));
        box-shadow:0 0 18px rgba(85,223,255,.16);
        animation:barMove 2.8s ease-in-out infinite alternate;
    }

    .schema-bar:nth-child(1){height:34px;animation-delay:.05s}
    .schema-bar:nth-child(2){height:52px;animation-delay:.15s}
    .schema-bar:nth-child(3){height:69px;animation-delay:.25s}
    .schema-bar:nth-child(4){height:92px;animation-delay:.35s}
    .schema-bar:nth-child(5){height:116px;animation-delay:.45s}
    .schema-bar:nth-child(6){height:86px;animation-delay:.55s}
    .schema-bar:nth-child(7){height:132px;animation-delay:.65s}
    .schema-bar:nth-child(8){height:108px;animation-delay:.75s}
    .schema-bar:nth-child(9){height:146px;animation-delay:.85s}

    @keyframes barMove {
        from { transform:scaleY(.82); opacity:.42; }
        to { transform:scaleY(1.06); opacity:.88; }
    }

    .schema-line {
        position:absolute;
        right:38px;
        top:22px;
        width:650px;
        height:210px;
    }

    .schema-line svg {
        width:100%;
        height:100%;
        overflow:visible;
    }

    .schema-line .glow-path {
        fill:none;
        stroke:#52E7FF;
        stroke-width:12;
        stroke-linecap:round;
        stroke-linejoin:round;
        opacity:.12;
    }

    .schema-line .main-path {
        fill:none;
        stroke:url(#heroLineGradient);
        stroke-width:3.8;
        stroke-linecap:round;
        stroke-linejoin:round;
        stroke-dasharray:900;
        stroke-dashoffset:900;
        animation:drawHeroLine 3.8s ease-in-out infinite;
        filter:drop-shadow(0 0 10px rgba(82,231,255,.45));
    }

    @keyframes drawHeroLine {
        0% { stroke-dashoffset:900; opacity:.45; }
        45% { stroke-dashoffset:0; opacity:1; }
        100% { stroke-dashoffset:0; opacity:1; }
    }

    .schema-node {
        fill:#8CF6FF;
        stroke:rgba(255,255,255,.85);
        stroke-width:2;
        filter:drop-shadow(0 0 8px rgba(140,246,255,.75));
        animation:nodeBlink 2.4s ease-in-out infinite;
    }

    .schema-node:nth-of-type(2){animation-delay:.15s}
    .schema-node:nth-of-type(3){animation-delay:.3s}
    .schema-node:nth-of-type(4){animation-delay:.45s}
    .schema-node:nth-of-type(5){animation-delay:.6s}

    @keyframes nodeBlink {
        0%,100% { opacity:.55; transform:scale(.92); }
        50% { opacity:1; transform:scale(1.12); }
    }

    .schema-radar {
        position:absolute;
        right:62px;
        top:34px;
        width:165px;
        height:165px;
        border-radius:50%;
        border:1px solid rgba(93,232,255,.26);
        box-shadow:0 0 34px rgba(93,232,255,.12);
        animation:radarRotate 8s linear infinite;
    }

    .schema-radar::before,
    .schema-radar::after {
        content:"";
        position:absolute;
        border-radius:50%;
        inset:26px;
        border:1px solid rgba(93,232,255,.25);
    }

    .schema-radar::after {
        inset:54px;
        background:radial-gradient(circle, rgba(101,240,255,.95), rgba(122,60,255,.50) 42%, transparent 68%);
        box-shadow:0 0 34px rgba(101,240,255,.65);
    }

    .schema-wave {
        position:absolute;
        right:0;
        bottom:8px;
        width:650px;
        height:96px;
        opacity:.58;
        background:
            radial-gradient(circle at 70% 55%, rgba(85,223,255,.30), transparent 22%),
            linear-gradient(90deg, transparent, rgba(47,124,255,.16), transparent);
        border-radius:50%;
        transform:skewX(-18deg);
        animation:waveFloat 5.8s ease-in-out infinite;
    }

    @keyframes waveFloat {
        0%,100% { transform:skewX(-18deg) translateY(0); opacity:.45; }
        50% { transform:skewX(-18deg) translateY(-9px); opacity:.7; }
    }


    .metric-grid {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:1.15rem;
        margin:1rem 0;
    }

    .metric-card {
        position:relative;
        overflow:hidden;
        border-radius:18px;
        min-height:116px;
        color:white;
        padding:1.15rem 1.2rem;
        box-shadow:0 18px 44px rgba(26,62,137,.14);
    }

    .metric-card::after {
        content:"";
        position:absolute;
        right:-27px;
        bottom:-36px;
        width:120px;
        height:120px;
        border-radius:999px;
        background:rgba(255,255,255,.18);
    }

    .metric-card.blue { background:linear-gradient(135deg,#1F6DFF,#318BFF); }
    .metric-card.orange { background:linear-gradient(135deg,#FF8A00,#FFB223); }
    .metric-card.green { background:linear-gradient(135deg,#08A96B,#35D89F); }
    .metric-card.purple { background:linear-gradient(135deg,#713BFF,#A66BFF); }

    .metric-label {
        font-size:.82rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.04em;
        color:rgba(255,255,255,.92);
        position:relative;
        z-index:2;
    }

    .metric-value {
        font-size:1.75rem;
        font-weight:900;
        letter-spacing:-.04em;
        margin-top:.35rem;
        position:relative;
        z-index:2;
    }

    .metric-sub {
        font-size:.88rem;
        color:rgba(255,255,255,.90);
        font-weight:700;
        margin-top:.28rem;
        position:relative;
        z-index:2;
    }

    .section-card {
        background:rgba(255,255,255,.94);
        border:1px solid #E2EAF7;
        border-radius:20px;
        box-shadow:0 14px 36px rgba(21,54,108,.08);
        padding:1.25rem;
        margin-bottom:1rem;
    }

    .section-title {
        display:flex;
        align-items:center;
        gap:.8rem;
        color:#0D2A61;
        font-size:1.02rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.035em;
        margin-bottom:1rem;
    }

    .title-icon {
        width:24px;
        height:24px;
        border-radius:8px;
        background:linear-gradient(135deg,#2F7CFF,#20D8C5);
        position:relative;
        flex-shrink:0;
    }

    .reco-card {
        display:grid;
        grid-template-columns:110px 1fr;
        gap:1.35rem;
        align-items:center;
    }

    .robot {
        width:104px;
        height:104px;
        border-radius:24px;
        background:
            radial-gradient(circle at 50% 50%, rgba(117,244,255,.80), transparent 16%),
            radial-gradient(circle at 35% 34%, rgba(122,60,255,.75), transparent 28%),
            linear-gradient(135deg,#0E3B94,#001F69 50%,#02C6D8);
        position:relative;
        box-shadow:0 20px 40px rgba(47,124,255,.18);
    }

    .robot::before {
        content:"";
        position:absolute;
        width:58px;
        height:40px;
        border-radius:18px;
        background:rgba(255,255,255,.22);
        border:2px solid rgba(143,244,255,.65);
        left:23px;
        top:30px;
    }

    .robot::after {
        content:"";
        position:absolute;
        width:8px;
        height:8px;
        border-radius:999px;
        background:#73F5FF;
        left:39px;
        top:47px;
        box-shadow:28px 0 0 #73F5FF;
    }

    .kicker {
        color:#286EFF;
        font-size:.82rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.09em;
    }

    .reco-title {
        color:#0C2446;
        font-size:1.55rem;
        line-height:1.08;
        font-weight:900;
        letter-spacing:-.035em;
        margin:.3rem 0 .55rem;
    }

    .reco-text {
        color:#596982;
        line-height:1.5;
        font-size:.95rem;
    }

    .status-grid {
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:.85rem;
    }

    .status-box {
        border:1px solid #E1EAF6;
        background:linear-gradient(180deg,#FFFFFF,#FAFCFF);
        border-radius:15px;
        padding:1rem;
    }

    .status-label {
        color:#52657F;
        font-size:.9rem;
        font-weight:800;
    }

    .status-value {
        color:#236FFF;
        font-size:1.45rem;
        font-weight:900;
        margin:.25rem 0;
    }

    .status-text {
        color:#697A91;
        font-size:.82rem;
    }

    .progress {
        height:7px;
        border-radius:999px;
        background:#E6EDF8;
        overflow:hidden;
        margin-top:.75rem;
    }

    .progress-fill {
        height:100%;
        border-radius:999px;
        background:linear-gradient(90deg,#2F7CFF,#20D8C5);
    }

    .quick-text {
        color:#52657F;
        font-size:.92rem;
        line-height:1.45;
        padding:.55rem 0 .1rem;
    }

    .donut {
        width:160px;
        height:160px;
        border-radius:50%;
        background:conic-gradient(#35DD9A 0deg 360deg);
        margin:.6rem auto;
        position:relative;
    }

    .donut::before {
        content:"";
        position:absolute;
        inset:32px;
        border-radius:50%;
        background:white;
        box-shadow:inset 0 0 0 1px #ECF2FA;
    }

    .donut-center {
        position:absolute;
        inset:0;
        display:flex;
        flex-direction:column;
        gap:.12rem;
        align-items:center;
        justify-content:center;
        color:#172C58;
        font-weight:900;
        font-size:1.35rem;
    }

    .donut-center span {
        font-size:.84rem;
        color:#33445E;
        font-weight:800;
    }

    .summary-line {
        display:grid;
        grid-template-columns:1fr auto;
        gap:.7rem;
        align-items:center;
        color:#536782;
        font-size:.9rem;
        margin:.48rem 0;
    }

    .summary-line span {
        color:#536782;
    }

    .summary-line b {
        color:#0C2446;
        font-weight:900;
    }

    .quick-actions {
        display:grid;
        gap:.75rem;
    }

    .quick-action-primary,
    .quick-action-secondary {
        height:44px;
        border-radius:10px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:900;
    }

    .quick-action-primary {
        color:white;
        background:linear-gradient(90deg,#2F7CFF,#8D35FF);
    }

    .quick-action-secondary {
        color:#38506E;
        background:white;
        border:1px solid #D3E0F2;
    }

    [data-testid="stButton"] > button {
        border-radius:14px !important;
        min-height:52px !important;
        font-weight:900 !important;
        border:1px solid #D9E5F4 !important;
    }


/* =========================
   ICONES PREMIUM DESSINEES
========================= */

.metric-icon-wrap {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:.8rem;
    margin-bottom:.55rem;
    position:relative;
    z-index:2;
}

.metric-icon-mini {
    width:58px;
    height:58px;
    border-radius:17px;
    background:rgba(255,255,255,.18);
    backdrop-filter:blur(5px);
    position:relative;
    overflow:hidden;
    flex-shrink:0;
    border:1px solid rgba(255,255,255,.16);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.15);
}

.metric-icon-mini.wallet::before {
    content:"";
    position:absolute;
    width:30px;
    height:21px;
    border-radius:8px;
    background:#fff;
    left:11px;
    top:17px;
    box-shadow:0 4px 10px rgba(0,0,0,.10);
}
.metric-icon-mini.wallet::after {
    content:"";
    position:absolute;
    width:13px;
    height:10px;
    border-radius:6px;
    background:#72B7FF;
    top:22px;
    right:10px;
    box-shadow:inset 0 0 0 2px rgba(255,255,255,.92);
}

.metric-icon-mini.shield::before {
    content:"";
    position:absolute;
    width:25px;
    height:29px;
    background:#fff;
    clip-path:polygon(50% 0%, 88% 18%, 88% 52%, 50% 100%, 12% 52%, 12% 18%);
    top:11px;
    left:13.5px;
    box-shadow:0 5px 12px rgba(0,0,0,.12);
}
.metric-icon-mini.shield::after {
    content:"";
    position:absolute;
    width:9px;
    height:14px;
    border:3px solid #FF9B16;
    border-top:none;
    border-left:none;
    transform:rotate(45deg);
    top:17px;
    left:21px;
}

.metric-icon-mini.growth::before {
    content:"";
    position:absolute;
    width:25px;
    height:22px;
    border-left:4px solid #fff;
    border-bottom:4px solid #fff;
    left:12px;
    bottom:12px;
    border-radius:0 0 0 4px;
}
.metric-icon-mini.growth::after {
    content:"";
    position:absolute;
    width:23px;
    height:23px;
    border-top:4px solid #fff;
    border-right:4px solid #fff;
    transform:rotate(45deg);
    right:12px;
    top:14px;
    border-radius:0 5px 0 0;
}

.metric-icon-mini.brain::before {
    content:"";
    position:absolute;
    width:25px;
    height:25px;
    border-radius:50%;
    background:rgba(255,255,255,.21);
    top:13.5px;
    left:13.5px;
    box-shadow:
        -7px 0 0 rgba(255,255,255,.21),
        7px 0 0 rgba(255,255,255,.21),
        0 -7px 0 rgba(255,255,255,.21),
        0 7px 0 rgba(255,255,255,.21);
}
.metric-icon-mini.brain::after {
    content:"";
    position:absolute;
    width:14px;
    height:22px;
    border-left:3px solid #fff;
    border-right:3px solid #fff;
    border-radius:12px;
    top:15px;
    left:19px;
}

/* Robot premium du bloc recommandation */
.robot-premium {
    width:112px;
    height:112px;
    border-radius:30px;
    position:relative;
    overflow:hidden;
    background:
        radial-gradient(circle at 30% 28%, rgba(134,92,255,.85), transparent 28%),
        radial-gradient(circle at 78% 76%, rgba(35,224,255,.50), transparent 34%),
        linear-gradient(135deg,#0A2F7E 0%, #172E88 42%, #061B5A 100%);
    box-shadow:0 22px 44px rgba(47,124,255,.22);
    border:1px solid rgba(255,255,255,.14);
}
.robot-premium::before {
    content:"";
    position:absolute;
    inset:0;
    background:
        radial-gradient(circle at 50% 50%, rgba(255,255,255,.10), transparent 52%),
        linear-gradient(120deg, transparent 0%, rgba(255,255,255,.12) 46%, transparent 58%);
}
.robot-antenna {
    position:absolute;
    width:4px;
    height:15px;
    background:#9AF6FF;
    top:19px;
    left:54px;
    border-radius:999px;
    box-shadow:0 0 9px rgba(154,246,255,.65);
}
.robot-antenna::after {
    content:"";
    position:absolute;
    width:11px;
    height:11px;
    border-radius:50%;
    background:#7CF2FF;
    left:-3.5px;
    top:-7px;
    box-shadow:0 0 13px rgba(124,242,255,.75);
}
.robot-head {
    position:absolute;
    width:60px;
    height:41px;
    left:26px;
    top:33px;
    border-radius:17px;
    background:linear-gradient(135deg,#88F3FF,#B7FFFF);
    box-shadow:0 0 22px rgba(117,245,255,.45);
    border:2px solid rgba(255,255,255,.55);
}
.robot-head::before,
.robot-head::after {
    content:"";
    position:absolute;
    top:15px;
    width:8px;
    height:8px;
    border-radius:50%;
    background:#315DFF;
    box-shadow:0 0 6px rgba(49,93,255,.35);
}
.robot-head::before { left:16px; }
.robot-head::after { right:16px; }
.robot-mouth {
    position:absolute;
    width:20px;
    height:4px;
    border-radius:999px;
    background:rgba(49,93,255,.45);
    top:59px;
    left:46px;
    z-index:3;
}
.robot-ear-left,
.robot-ear-right {
    position:absolute;
    width:10px;
    height:22px;
    border-radius:999px;
    background:rgba(135,243,255,.75);
    top:43px;
    z-index:2;
}
.robot-ear-left { left:18px; }
.robot-ear-right { right:18px; }
.robot-body {
    position:absolute;
    width:44px;
    height:22px;
    left:34px;
    top:76px;
    border-radius:13px;
    background:rgba(255,255,255,.20);
    border:1px solid rgba(255,255,255,.22);
}
.robot-body::before {
    content:"";
    position:absolute;
    width:8px;
    height:8px;
    border-radius:50%;
    background:#72F3FF;
    left:18px;
    top:7px;
}

/* Icones de sections */
.section-icon {
    width:28px;
    height:28px;
    border-radius:9px;
    position:relative;
    flex-shrink:0;
    background:linear-gradient(135deg,#2F7CFF,#20D8C5);
    box-shadow:0 7px 16px rgba(47,124,255,.18);
}

.section-icon.wallet::before {
    content:"";
    position:absolute;
    width:16px;
    height:11px;
    border-radius:4px;
    background:white;
    top:9px;
    left:6px;
}
.section-icon.wallet::after {
    content:"";
    position:absolute;
    width:6px;
    height:5px;
    border-radius:3px;
    background:#2F7CFF;
    top:12px;
    right:6px;
}

.section-icon.pie::before {
    content:"";
    position:absolute;
    width:16px;
    height:16px;
    border-radius:50%;
    background:white;
    top:6px;
    left:6px;
}
.section-icon.pie::after {
    content:"";
    position:absolute;
    width:16px;
    height:16px;
    top:6px;
    left:13px;
    background:linear-gradient(135deg,#2F7CFF,#20D8C5);
    clip-path:polygon(0 0,100% 0,100% 100%,0 50%);
    border-top-right-radius:8px;
    border-bottom-right-radius:8px;
}

.section-icon.list::before {
    content:"";
    position:absolute;
    width:15px;
    height:3px;
    background:white;
    left:7px;
    top:8px;
    box-shadow:0 6px 0 white, 0 12px 0 white;
    border-radius:999px;
}

.section-icon.bolt::before {
    content:"";
    position:absolute;
    width:13px;
    height:19px;
    background:white;
    clip-path:polygon(55% 0,100% 0,65% 42%,100% 42%,35% 100%,48% 58%,15% 58%);
    top:5px;
    left:8px;
}

.section-icon.spark::before {
    content:"";
    position:absolute;
    width:16px;
    height:16px;
    background:white;
    clip-path:polygon(50% 0,60% 36%,100% 50%,60% 64%,50% 100%,40% 64%,0 50%,40% 36%);
    left:6px;
    top:6px;
}

.reco-card {
    grid-template-columns:122px 1fr !important;
}

    
    .metric-icon-mini {
        width:58px !important;
        height:58px !important;
        border-radius:20px !important;
    }

    .metric-card {
        min-height:126px !important;
        padding:1.25rem 1.32rem !important;
    }

    .metric-value {
        font-size:1.95rem !important;
    }

@media (max-width:1200px) {
        .metric-grid, .status-grid { grid-template-columns:1fr; }
        .reco-card { grid-template-columns:1fr; }
    }
    </style>
    """)


# ============================================================
# HELPERS DONNÉES
# ============================================================

DEFAULT_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "GOOG": "Alphabet",
    "META": "Meta",
    "JNJ": "Johnson & Johnson",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "KO": "Coca-Cola",
    "PG": "Procter & Gamble",
    "WMT": "Walmart",
    "SPY": "SPDR S&P 500 ETF",
    "VTI": "Vanguard Total Market ETF",
}

DEFAULT_SECTORS = {
    "AAPL": "Technologie",
    "MSFT": "Technologie",
    "NVDA": "Technologie",
    "AMZN": "Consommation discrétionnaire",
    "GOOGL": "Communication",
    "GOOG": "Communication",
    "META": "Communication",
    "JNJ": "Santé",
    "JPM": "Finance",
    "V": "Finance",
    "KO": "Consommation de base",
    "PG": "Consommation de base",
    "WMT": "Consommation de base",
    "SPY": "ETF diversifié",
    "VTI": "ETF diversifié",
}


@st.cache_data(show_spinner=False, ttl=900)
def get_latest_price(ticker):
    try:
        import yfinance as yf
        ticker = str(ticker).upper().strip()
        data = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=False)
        if data is None or data.empty or "Close" not in data.columns:
            return None
        close = data["Close"].dropna()
        if close.empty:
            return None
        value = close.iloc[-1]
        if hasattr(value, "iloc"):
            value = value.iloc[0]
        return float(value)
    except Exception:
        return None


def build_position_rows(positions):
    rows = []
    invested_value = 0.0
    invested_cost = 0.0
    real_prices = 0

    for position in positions:
        try:
            ticker, company_name, qty, avg_buy_price = position
        except Exception:
            continue

        try:
            qty = float(qty)
            avg_buy_price = float(avg_buy_price)
        except Exception:
            continue

        if qty <= 0:
            continue

        ticker = str(ticker).upper().strip()
        company_name = company_name or DEFAULT_NAMES.get(ticker, ticker)
        latest_price = get_latest_price(ticker)

        if latest_price is not None and latest_price > 0:
            current_price = latest_price
            source = "Marché"
            real_prices += 1
        else:
            current_price = avg_buy_price * 1.04
            source = "Estimé"

        value = qty * current_price
        cost = qty * avg_buy_price
        pnl_value = value - cost
        pnl_pct = (pnl_value / cost * 100) if cost > 0 else 0

        invested_value += value
        invested_cost += cost

        rows.append({
            "ticker": ticker,
            "name": company_name,
            "qty": qty,
            "avg": avg_buy_price,
            "current": current_price,
            "value": value,
            "cost": cost,
            "pnl_value": pnl_value,
            "pnl_pct": pnl_pct,
            "sector": DEFAULT_SECTORS.get(ticker, "Autre"),
            "source": source,
        })

    return rows, invested_value, invested_cost, real_prices


def try_get_orders(user_id):
    try:
        from database import get_user_orders
        return get_user_orders(user_id)
    except Exception:
        return []


def get_next_action(position_rows, cash_balance, total_portfolio, profil, nb_analyses, nb_recommended):
    cash_weight = (cash_balance / total_portfolio * 100) if total_portfolio else 0

    if nb_analyses == 0:
        return (
            "Compléter votre profil investisseur",
            "Commencez par répondre au questionnaire IA pour que FinPilot adapte les recommandations à votre tolérance au risque.",
            "pages/analyse.py",
            "Analyser mon profil",
        )

    if nb_recommended == 0:
        return (
            "Générer des recommandations IA",
            "Votre profil est connu, mais aucune recommandation n’est sauvegardée. Lancez le calcul financier pour obtenir un Top 5 exploitable.",
            "pages/analyse.py",
            "Voir les recommandations",
        )

    if not position_rows:
        return (
            "Construire un premier portefeuille",
            "Vous avez du cash disponible mais aucune position ouverte. Passez par les recommandations IA puis simulez un premier achat.",
            "pages/analyse.py",
            "Choisir une action",
        )

    if len(position_rows) == 1:
        return (
            "Réduire la concentration",
            "Votre portefeuille contient une seule ligne. Ajouter une deuxième position ou un ETF peut réduire le risque spécifique.",
            "pages/portefeuille.py",
            "Gérer le portefeuille",
        )

    if cash_weight > 70:
        return (
            "Utiliser une partie du cash",
            f"Votre portefeuille reste très liquide avec {cash_weight:.1f}% de cash. Une allocation progressive peut améliorer le potentiel de rendement.",
            "pages/analyse.py",
            "Identifier des opportunités",
        )

    return (
        "Suivre et ajuster le portefeuille",
        f"Votre profil dominant est {profil}. Continuez à suivre les positions et à comparer les recommandations IA avant tout nouvel arbitrage.",
        "pages/portefeuille.py",
        "Voir le portefeuille",
    )


def portfolio_health(position_rows, cash_balance, total_portfolio):
    cash_weight = cash_balance / total_portfolio * 100 if total_portfolio > 0 else 0

    if not position_rows:
        diversification = 0
        status = "À construire"
        text = "Aucune position ouverte. Le portefeuille est essentiellement liquide."
    elif len(position_rows) == 1:
        diversification = 25
        status = "Concentré"
        text = "Une seule position ouverte. Le risque spécifique est élevé."
    elif len(position_rows) < 4:
        diversification = 55
        status = "En construction"
        text = "Quelques positions sont ouvertes. La diversification peut encore être renforcée."
    else:
        diversification = 80
        status = "Diversifié"
        text = "Plusieurs positions sont ouvertes. Le portefeuille est plus équilibré."

    if cash_weight > 70:
        liquidity_status = "Très liquide"
    elif cash_weight > 35:
        liquidity_status = "Équilibré"
    else:
        liquidity_status = "Investi"

    return cash_weight, diversification, status, liquidity_status, text


def extract_recent_recommendations(recommended_rows, limit=4):
    items = []

    for row in recommended_rows[:limit]:
        try:
            if isinstance(row, dict):
                ticker = row.get("ticker") or row.get("symbol") or ""
                name = row.get("name") or row.get("company_name") or DEFAULT_NAMES.get(str(ticker).upper(), str(ticker).upper())
                score = row.get("score")
            else:
                ticker = str(row[0]).upper().strip()
                name = DEFAULT_NAMES.get(ticker, ticker)
                score = row[1] if len(row) > 1 and isinstance(row[1], (int, float)) else None

            if ticker:
                items.append((str(ticker).upper(), name, score))
        except Exception:
            continue

    return items


# ============================================================
# DONNÉES UTILISATEUR
# ============================================================

user_id = st.session_state.user_id
username = safe_username()

if not has_user_capital_configured(user_id):
    render_capital_setup(user_id)
    st.stop()

cash_balance = float(get_user_cash_balance(user_id) or 0)
history_rows = load_user_history(user_id)
recommended_rows = load_user_recommended_actions(user_id)
positions = get_portfolio_positions(user_id)
orders = try_get_orders(user_id)

insights = get_history_summary(history_rows, recommended_rows)
profil = insights.get("profil_dominant") or "Prudent"
risk_score = get_risk_score(profil)

position_rows, invested_value, invested_cost, real_prices = build_position_rows(positions)

total_portfolio = cash_balance + invested_value
pnl = invested_value - invested_cost
pnl_pct = (pnl / invested_cost * 100) if invested_cost > 0 else 0
pnl_sign = "+" if pnl >= 0 else ""
pnl_bg_class = "green" if pnl >= 0 else "orange"

nb_positions = len(position_rows)
nb_analyses = insights.get("nb_analyses", 0)
nb_recommended = insights.get("nb_recommended", len(recommended_rows))
nb_orders = len(orders)

next_title, next_text, next_page, next_button = get_next_action(
    position_rows,
    cash_balance,
    total_portfolio,
    profil,
    nb_analyses,
    nb_recommended,
)

cash_weight, diversification_score, diversification_status, liquidity_status, health_text = portfolio_health(
    position_rows,
    cash_balance,
    total_portfolio,
)

recent_recos = extract_recent_recommendations(recommended_rows, limit=4)

inject_dashboard_style()


# ============================================================
# SIDEBAR PREMIUM COMMUNE
# ============================================================

render_sidebar(
    active_page="dashboard",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# HERO
# ============================================================

html(f"""
<div class="hero-premium">
    <div class="hero-schema">
        <div class="schema-grid"></div>
        <div class="schema-bars">
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
            <div class="schema-bar"></div>
        </div>
        <div class="schema-line">
            <svg viewBox="0 0 650 210" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="heroLineGradient" x1="0" x2="1">
                        <stop offset="0%" stop-color="#1ED9FF"/>
                        <stop offset="48%" stop-color="#77F7FF"/>
                        <stop offset="100%" stop-color="#FFFFFF"/>
                    </linearGradient>
                </defs>
                <path class="glow-path" d="M10,145 C55,122 78,86 120,106 C158,124 176,164 214,128 C249,94 278,102 310,72 C354,31 383,93 414,78 C461,54 472,18 516,34 C548,46 570,22 635,14"/>
                <path class="main-path" d="M10,145 C55,122 78,86 120,106 C158,124 176,164 214,128 C249,94 278,102 310,72 C354,31 383,93 414,78 C461,54 472,18 516,34 C548,46 570,22 635,14"/>
                <circle class="schema-node" cx="120" cy="106" r="5"/>
                <circle class="schema-node" cx="214" cy="128" r="5"/>
                <circle class="schema-node" cx="310" cy="72" r="5"/>
                <circle class="schema-node" cx="414" cy="78" r="5"/>
                <circle class="schema-node" cx="516" cy="34" r="5"/>
            </svg>
        </div>
        <div class="schema-radar"></div>
        <div class="schema-wave"></div>
    </div>

    <h1>Accueil FinPilot</h1>
    <p>
        FinPilot est un copilote intelligent d’aide à la décision financière.
        Cette page d’accueil résume votre profil, votre portefeuille simulé et les prochaines actions à réaliser.
    </p>
    <div class="hero-badges">
        <div class="hero-badge">Profil : {profil}</div>
        <div class="hero-badge">Capital : {money_dollar(total_portfolio)}</div>
        <div class="hero-badge">Positions : {nb_positions}</div>
        <div class="hero-badge">Analyses IA : {nb_analyses}</div>
    </div>
</div>
""")



# ============================================================
# INTRO ACCUEIL
# ============================================================

html("""
<div class="section-card" style="margin-top:.2rem;">
    <div class="section-title">
        <span class="section-icon spark"></span>
        <span>Bienvenue dans votre espace de simulation</span>
    </div>
    <div class="quick-text">
        FinPilot combine un questionnaire investisseur, une analyse multicritère MCDA
        et une simulation de portefeuille. Aucune transaction réelle n’est effectuée :
        l’objectif est d’aider l’utilisateur à comprendre avant d’investir.
    </div>
</div>
""")

# ============================================================
# KPI
# ============================================================

html(f"""
<div class="metric-grid">
    <div class="metric-card blue">
        <div class="metric-icon-wrap">
            <div class="metric-label">Valeur totale</div>
            <div class="metric-icon-mini wallet"></div>
        </div>
        <div class="metric-value">{money_dollar(total_portfolio)}</div>
        <div class="metric-sub">Portefeuille + cash</div>
    </div>

    <div class="metric-card orange">
        <div class="metric-icon-wrap">
            <div class="metric-label">Profil investisseur</div>
            <div class="metric-icon-mini shield"></div>
        </div>
        <div class="metric-value">{profil}</div>
        <div class="metric-sub">Score risque : {risk_score}/100</div>
    </div>

    <div class="metric-card {pnl_bg_class}">
        <div class="metric-icon-wrap">
            <div class="metric-label">Gain latent</div>
            <div class="metric-icon-mini growth"></div>
        </div>
        <div class="metric-value">{pnl_sign}{money_dollar(pnl)}</div>
        <div class="metric-sub">{pnl_sign}{pnl_pct:.2f}% sur positions</div>
    </div>

    <div class="metric-card purple">
        <div class="metric-icon-wrap">
            <div class="metric-label">Activité IA</div>
            <div class="metric-icon-mini brain"></div>
        </div>
        <div class="metric-value">{nb_analyses}</div>
        <div class="metric-sub">Analyse(s) de profil</div>
    </div>
</div>
""")


# ============================================================
# MAIN
# ============================================================

left, right = st.columns([1.65, 1], gap="medium")

with left:
    html(f"""
    <div class="section-card">
        <div class="reco-card">
            <div class="robot-premium">
                <div class="robot-antenna"></div>
                <div class="robot-ear-left"></div>
                <div class="robot-ear-right"></div>
                <div class="robot-head"></div>
                <div class="robot-mouth"></div>
                <div class="robot-body"></div>
            </div>
            <div>
                <div class="kicker">Prochaine action recommandée</div>
                <div class="reco-title">{next_title}</div>
                <div class="reco-text">{next_text}</div>
            </div>
        </div>
    </div>
    """)

    b1, b2 = st.columns(2, gap="medium")
    with b1:
        if st.button(next_button, use_container_width=True, type="primary", key="step_next_app"):
            st.switch_page(next_page)
    with b2:
        if st.button("Voir mon portefeuille", use_container_width=True, key="voir_portefeuille_app"):
            st.switch_page("pages/portefeuille.py")

    html(f"""
    <div class="section-card">
        <div class="section-title">
            <span class="section-icon wallet"></span>
            <span>État global du portefeuille simulé</span>
        </div>

        <div class="status-grid">
            <div class="status-box">
                <div class="status-label">Liquidité</div>
                <div class="status-value">{cash_weight:.1f} %</div>
                <div class="status-text">{liquidity_status}</div>
                <div class="progress"><div class="progress-fill" style="width:{min(cash_weight, 100)}%;"></div></div>
            </div>

            <div class="status-box">
                <div class="status-label">Diversification</div>
                <div class="status-value">{diversification_score}/100</div>
                <div class="status-text">{diversification_status}</div>
                <div class="progress"><div class="progress-fill" style="width:{diversification_score}%;"></div></div>
            </div>

            <div class="status-box">
                <div class="status-label">Positions</div>
                <div class="status-value">{nb_positions}</div>
                <div class="status-text">Ligne(s) actuellement suivie(s)</div>
                <div class="progress"><div class="progress-fill" style="width:{min(nb_positions * 18, 100)}%;"></div></div>
            </div>
        </div>

        <div class="quick-text">
            <b>Lecture rapide</b><br>
            {health_text}
        </div>
    </div>
    """)

    secteur_txt = ", ".join(insights.get("secteurs_favoris", [])) if insights.get("secteurs_favoris") else "Aucune préférence sectorielle dominante"
    action_txt = ", ".join(insights.get("actions_recurrentes", [])[:4]) if insights.get("actions_recurrentes") else "Aucune action récurrente"

    html(f"""
    <div class="section-card">
        <div class="section-title">
            <span class="section-icon spark"></span>
            <span>Dernière activité IA</span>
        </div>

        <div class="quick-text">
            <b>Profil dominant :</b> {profil}<br>
            <b>Secteurs fréquents :</b> {secteur_txt}<br>
            <b>Actions analysées :</b> {action_txt}
        </div>
    </div>
    """)

    if recent_recos:
        for ticker, name, score in recent_recos:
            score_txt = f"Score : {score:.1f}" if isinstance(score, (int, float)) else "Recommandation IA"
            html(f"""
            <div class="section-card" style="padding:1rem 1.2rem;">
                <b style="color:#0C2446;">{name} ({ticker})</b>
                <div style="color:#64748B;margin-top:.25rem;">{score_txt}</div>
            </div>
            """)
    else:
        html("""
        <div class="section-card" style="padding:1rem 1.2rem;">
            <b style="color:#0C2446;">Aucune recommandation sauvegardée</b>
            <div style="color:#64748B;margin-top:.25rem;">Lancez une analyse IA pour alimenter cette section.</div>
        </div>
        """)

with right:
    actions_value = sum(row["value"] for row in position_rows)
    labels = []
    values = []

    if cash_balance > 0:
        labels.append("Cash")
        values.append(cash_balance)

    if actions_value > 0:
        labels.append("Positions")
        values.append(actions_value)

    if not values:
        labels = ["Cash"]
        values = [1]

    total_alloc = sum(values)
    cash_pct = 100 if total_alloc <= 0 else (cash_balance / total_alloc * 100)

    html(f"""
    <div class="section-card">
        <div class="section-title">
            <span class="section-icon pie"></span>
            <span>Répartition simplifiée</span>
        </div>
        <div style="color:#667995;font-size:.88rem;margin-top:-.65rem;margin-left:2.1rem;">
            Vue synthétique, sans détails réservés à la page Portefeuille.
        </div>

        <div style="display:grid;grid-template-columns:1fr 120px;align-items:center;gap:.8rem;">
            <div style="position:relative;">
                <div class="donut">
                    <div class="donut-center">{cash_pct:.0f} %<span>Cash</span></div>
                </div>
            </div>
            <div style="color:#0C2446;font-weight:800;font-size:.9rem;">
                <div><span style="display:inline-block;width:11px;height:11px;border-radius:999px;background:#35DD9A;margin-right:.5rem;"></span>Cash</div>
                <div style="margin-left:1.65rem;margin-top:.35rem;">{cash_pct:.0f} %</div>
            </div>
        </div>
    </div>
    """)

    html(f"""
    <div class="section-card">
        <div class="section-title">
            <span class="section-icon list"></span>
            <span>Résumé chiffré</span>
        </div>

        <div class="summary-line"><span>Valeur totale</span><b>{money_dollar(total_portfolio)}</b></div>
        <div class="summary-line"><span>Cash</span><b>{money_dollar(cash_balance)}</b></div>
        <div class="summary-line"><span>Positions</span><b>{nb_positions}</b></div>
        <div class="summary-line"><span>Ordres simulés</span><b>{nb_orders}</b></div>
    </div>
    """)

    html("""
    <div class="section-card">
        <div class="section-title">
            <span class="section-icon bolt"></span>
            <span>Actions rapides</span>
        </div>
    </div>
    """)

    if st.button("Commencer l’analyse IA", use_container_width=True, type="primary", key="analyser_profil_app"):
        st.switch_page("pages/analyse.py")

    if st.button("Voir le portefeuille", use_container_width=True, key="gerer_portefeuille_app"):
        st.switch_page("pages/portefeuille.py")

    if st.button("Consulter l’historique", use_container_width=True, key="voir_historique_app"):
        st.switch_page("pages/historique.py")

    html("""
    <div class="section-card">
        <div style="color:#0C2446;font-weight:900;margin-bottom:.35rem;">Rôle de l’accueil</div>
        <div style="color:#64748B;line-height:1.55;font-size:.92rem;">
            Cette page sert de point d’entrée : elle présente l’état global du compte,
            oriente l’utilisateur vers l’analyse IA et rappelle que les opérations restent simulées.
        </div>
    </div>
    """)