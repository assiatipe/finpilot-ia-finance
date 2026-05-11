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
    page_title="FinPilot",
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
# HELPERS
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
# STYLE DASHBOARD PREMIUM V2
# ============================================================

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Bricolage+Grotesque:wght@500;600;700;800&display=swap');

html, body, .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: #F7F8FA !important;
}

.main .block-container {
    max-width: 1460px !important;
    padding: 0 1.8rem 2.5rem 1.8rem !important;
}

[data-testid="stAppViewContainer"] > .main,
section.main > div,
div.block-container {
    padding-top: 0 !important;
}

/* ── HERO ─────────────────────────────────────────────────── */
.db-hero {
    position: relative;
    overflow: hidden;
    padding: 2.6rem 3rem 2.2rem 3rem;
    margin: 0 0 1.4rem 0;
    border-radius: 0 0 24px 24px;
    background: #0A0F1E;
    color: white;
    min-height: 220px;
}

.db-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 80% 50%, rgba(26,86,219,0.35) 0%, transparent 55%),
        radial-gradient(ellipse at 20% 80%, rgba(99,102,241,0.15) 0%, transparent 45%);
    pointer-events: none;
}

.db-hero-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: linear-gradient(180deg, transparent 0%, black 30%, black 70%, transparent 100%);
}

.db-hero-content {
    position: relative;
    z-index: 3;
}

.db-hero-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #60A5FA;
    margin-bottom: 0.6rem;
}

.db-hero-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin-bottom: 0.7rem;
    color: #FFFFFF;
}

.db-hero-sub {
    color: rgba(255,255,255,0.65);
    font-size: 0.97rem;
    line-height: 1.65;
    max-width: 600px;
    font-weight: 400;
    margin-bottom: 1.2rem;
}

.db-hero-badges {
    display: flex;
    gap: 0.7rem;
    flex-wrap: wrap;
}

.db-hero-badge {
    padding: 0.42rem 0.85rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
}

/* Graphe décoratif hero */
.db-hero-chart {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 45%;
    z-index: 2;
    pointer-events: none;
    opacity: 0.7;
}

.db-hero-chart svg {
    width: 100%;
    height: 100%;
}

/* ── KPI CARDS ───────────────────────────────────────────── */
.db-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.db-kpi {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.35rem 1.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
}

.db-kpi:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}

.db-kpi::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}

.db-kpi.accent-blue::before  { background: #1A56DB; }
.db-kpi.accent-green::before { background: #059669; }
.db-kpi.accent-red::before   { background: #DC2626; }
.db-kpi.accent-indigo::before{ background: #4F46E5; }

.db-kpi-label {
    font-size: 0.71rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9CA3AF;
    margin-bottom: 0.65rem;
}

.db-kpi-value {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.85rem;
    font-weight: 800;
    color: #0A0F1E;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 0.35rem;
}

.db-kpi-value.positive { color: #059669; }
.db-kpi-value.negative { color: #DC2626; }

.db-kpi-sub {
    font-size: 0.8rem;
    color: #9CA3AF;
    font-weight: 400;
}

/* ── SECTION CARDS ────────────────────────────────────────── */
.db-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease;
}

.db-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
}

.db-card-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #0A0F1E;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.db-card-title::before {
    content: "";
    display: inline-block;
    width: 3px;
    height: 14px;
    background: #1A56DB;
    border-radius: 99px;
    flex-shrink: 0;
}

.db-card-sub {
    color: #6B7280;
    font-size: 0.85rem;
    margin-bottom: 1rem;
    line-height: 1.55;
}

/* ── RECO BLOCK ──────────────────────────────────────────── */
.db-reco {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1.2rem;
    align-items: flex-start;
}

.db-reco-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: #EEF4FF;
    border: 1px solid #DBEAFE;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.db-reco-icon::after {
    content: "AI";
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 0.78rem;
    font-weight: 800;
    color: #1A56DB;
}

.db-reco-kicker {
    font-size: 0.71rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: #1A56DB;
    margin-bottom: 0.3rem;
}

.db-reco-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: #0A0F1E;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.4rem;
}

.db-reco-text {
    color: #6B7280;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── STATUS GRID ─────────────────────────────────────────── */
.db-status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.85rem;
    margin-top: 0.2rem;
}

.db-status-box {
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 12px;
    padding: 1rem 1.1rem;
}

.db-status-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9CA3AF;
    margin-bottom: 0.4rem;
}

.db-status-value {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #1A56DB;
    margin-bottom: 0.2rem;
}

.db-status-text {
    font-size: 0.78rem;
    color: #9CA3AF;
    margin-bottom: 0.6rem;
}

.db-progress {
    height: 4px;
    background: #E5E7EB;
    border-radius: 99px;
    overflow: hidden;
}

.db-progress-fill {
    height: 100%;
    border-radius: 99px;
    background: #1A56DB;
    transition: width 0.8s ease;
}

/* ── SUMMARY TABLE ───────────────────────────────────────── */
.db-summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid #F3F4F6;
    font-size: 0.88rem;
}

.db-summary-row:last-child { border-bottom: none; }

.db-summary-label { color: #6B7280; }
.db-summary-value {
    font-weight: 700;
    color: #0A0F1E;
    font-family: 'Bricolage Grotesque', sans-serif;
}

/* ── DONUT ───────────────────────────────────────────────── */
.db-donut-wrap {
    display: grid;
    grid-template-columns: 160px 1fr;
    align-items: center;
    gap: 1.2rem;
    margin-top: 0.5rem;
}

.db-donut {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: conic-gradient(#1A56DB 0deg 360deg);
    position: relative;
    flex-shrink: 0;
}

.db-donut::before {
    content: "";
    position: absolute;
    inset: 36px;
    border-radius: 50%;
    background: white;
    box-shadow: inset 0 0 0 1px #F3F4F6;
}

.db-donut-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    color: #0A0F1E;
    font-size: 1.25rem;
    line-height: 1.1;
}

.db-donut-center span {
    font-size: 0.72rem;
    color: #9CA3AF;
    font-weight: 500;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.db-legend-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}

.db-legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── QUICK TEXT ──────────────────────────────────────────── */
.db-quick-text {
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    color: #374151;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-top: 0.5rem;
}

/* ── RECO ITEM ───────────────────────────────────────────── */
.db-reco-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 0.85rem;
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    transition: background 0.15s;
}

.db-reco-item:hover { background: #EEF4FF; }

.db-reco-ticker {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    color: #0A0F1E;
    font-size: 0.92rem;
}

.db-reco-name {
    color: #6B7280;
    font-size: 0.8rem;
    margin-top: 0.1rem;
}

.db-reco-score {
    font-size: 0.78rem;
    font-weight: 700;
    color: #1A56DB;
    background: #EEF4FF;
    padding: 0.25rem 0.55rem;
    border-radius: 6px;
    border: 1px solid #DBEAFE;
}
</style>
"""


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
    .block-container { max-width:1200px !important; padding-top:3rem !important; }

    .cap-hero {
        background: #0A0F1E;
        border-radius: 20px;
        padding: 2.5rem 2.8rem;
        color: white;
        position: relative;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    .cap-hero::before {
        content:"";
        position:absolute;
        inset:0;
        background: radial-gradient(ellipse at 85% 50%, rgba(26,86,219,0.4), transparent 55%);
    }
    .cap-hero-label {
        font-size:.72rem;font-weight:700;letter-spacing:.14em;
        text-transform:uppercase;color:#60A5FA;margin-bottom:.6rem;
        position:relative;z-index:2;
    }
    .cap-hero-title {
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:2.6rem;font-weight:800;letter-spacing:-.04em;
        line-height:1.1;margin-bottom:.7rem;
        position:relative;z-index:2;
    }
    .cap-hero-text {
        color:rgba(255,255,255,.70);font-size:.97rem;line-height:1.65;
        max-width:580px;position:relative;z-index:2;
    }
    .cap-panel {
        background:#FFFFFF;border:1px solid #E5E7EB;
        border-radius:16px;padding:1.8rem;
        box-shadow:0 1px 3px rgba(0,0,0,.06);
    }
    .cap-panel-label {
        font-size:.72rem;font-weight:700;letter-spacing:.10em;
        text-transform:uppercase;color:#1A56DB;margin-bottom:.4rem;
    }
    .cap-panel-amount {
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:2.5rem;font-weight:800;color:#0A0F1E;
        letter-spacing:-.04em;margin:.3rem 0;
    }
    .cap-mini-grid {
        display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin-top:1rem;
    }
    .cap-mini-card {
        background:#F9FAFB;border:1px solid #F3F4F6;
        border-radius:10px;padding:.8rem;
    }
    .cap-mini-title {
        font-size:.72rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.06em;color:#9CA3AF;margin-bottom:.2rem;
    }
    .cap-mini-value { color:#0A0F1E;font-weight:700;font-size:.88rem; }
    .cap-feature-card {
        background:#FFFFFF;border:1px solid #E5E7EB;
        border-top:3px solid #1A56DB;border-radius:14px;
        padding:1.3rem;box-shadow:0 1px 3px rgba(0,0,0,.05);
    }
    .cap-feature-num {
        width:36px;height:36px;border-radius:10px;
        background:#EEF4FF;color:#1A56DB;
        font-weight:800;font-size:.88rem;
        display:flex;align-items:center;justify-content:center;
        margin-bottom:.75rem;
    }
    .cap-feature-title { color:#0A0F1E;font-weight:700;font-size:1rem;margin-bottom:.3rem; }
    .cap-feature-text  { color:#6B7280;font-size:.85rem;line-height:1.55; }
    .cap-form-card {
        background:#FFFFFF;border:1px solid #E5E7EB;
        border-radius:16px;padding:1.6rem 1.8rem;
        box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:1rem;
    }
    .cap-form-title {
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:1.6rem;font-weight:800;color:#0A0F1E;
        letter-spacing:-.03em;margin:.3rem 0 .5rem;
    }
    .cap-preview-box {
        background:#EEF4FF;border:1px solid #DBEAFE;
        border-radius:12px;padding:1.2rem;
    }
    .cap-preview-label {
        font-size:.72rem;font-weight:700;letter-spacing:.10em;
        text-transform:uppercase;color:#1A56DB;margin-bottom:.4rem;
    }
    .cap-preview-value {
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:1.8rem;font-weight:800;color:#0A0F1E;letter-spacing:-.03em;
    }
    .cap-note {
        color:#9CA3AF;font-size:.8rem;line-height:1.55;margin-top:1rem;
    }
    </style>
    """)

    hero_left, hero_right = st.columns([1.5, 1], gap="large")

    with hero_left:
        html("""
        <div class="cap-hero">
            <div class="cap-hero-label">✦ Configuration initiale</div>
            <div class="cap-hero-title">Activez votre espace<br>d'investissement</div>
            <div class="cap-hero-text">
                Choisissez le capital de simulation avec lequel vous souhaitez commencer.
                Ce montant devient votre cash initial pour vos achats et votre portefeuille.
            </div>
        </div>
        """)

    with hero_right:
        current_preview = float(st.session_state.capital_form_value)
        html(f"""
        <div class="cap-panel">
            <div class="cap-panel-label">Aperçu du départ</div>
            <div class="cap-panel-amount">{money_dollar(current_preview)}</div>
            <div style="color:#6B7280;font-size:.85rem;">Cash initial disponible</div>
            <div class="cap-mini-grid">
                <div class="cap-mini-card">
                    <div class="cap-mini-title">Mode</div>
                    <div class="cap-mini-value">Simulation réaliste</div>
                </div>
                <div class="cap-mini-card">
                    <div class="cap-mini-title">Départ</div>
                    <div class="cap-mini-value">Sans positions</div>
                </div>
                <div class="cap-mini-card">
                    <div class="cap-mini-title">Objectif</div>
                    <div class="cap-mini-value">Construire un portefeuille</div>
                </div>
                <div class="cap-mini-card">
                    <div class="cap-mini-title">Règle</div>
                    <div class="cap-mini-value">1 client = 1 capital</div>
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
            <div class="cap-feature-card">
                <div class="cap-feature-num">{num}</div>
                <div class="cap-feature-title">{title}</div>
                <div class="cap-feature-text">{text}</div>
            </div>
            """)

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    _, center, _ = st.columns([0.15, 1, 0.15])

    with center:
        html("""
        <div class="cap-form-card">
            <div style="font-size:.72rem;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:#1A56DB;">Étape finale</div>
            <div class="cap-form-title">Choisissez votre capital de départ</div>
            <div style="color:#6B7280;font-size:.88rem;line-height:1.55;">
                Sélectionnez un montant rapide ou saisissez une valeur personnalisée.
            </div>
        </div>
        """)

        options = ["1 000 $", "5 000 $", "10 000 $", "25 000 $", "50 000 $", "100 000 $", "Personnalisé"]
        choice = st.radio("Montants rapides", options, horizontal=True,
                          key="capital_quick_choice", label_visibility="collapsed")

        if choice != st.session_state.capital_last_choice:
            if choice != "Personnalisé":
                st.session_state.capital_form_value = preset_values[choice]
            st.session_state.capital_last_choice = choice

        box1, box2 = st.columns([1.1, 0.9], gap="large")
        with box1:
            st.number_input("Capital initial ($)", min_value=100.0, max_value=10000000.0,
                            step=100.0, key="capital_form_value",
                            help="Montant utilisé comme cash de départ.")
        with box2:
            html(f"""
            <div class="cap-preview-box">
                <div class="cap-preview-label">Aperçu immédiat</div>
                <div class="cap-preview-value">{money_dollar(float(st.session_state.capital_form_value))}</div>
                <div style="color:#1A56DB;font-size:.82rem;margin-top:.35rem;">
                    Ce montant sera votre cash de départ.
                </div>
            </div>
            """)

        confirmation = st.checkbox(
            "Je confirme que ce montant sera utilisé comme capital initial de mon portefeuille.",
            key="capital_confirmation")

        if st.button("Initialiser mon portefeuille", use_container_width=True,
                     type="primary", key="init_portfolio"):
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
        <div class="cap-note">
            Cette action initialise votre portefeuille et supprime les anciennes données
            de démonstration pour repartir sur une base propre.
        </div>
        """)


# ============================================================
# DONNÉES PORTFOLIO
# ============================================================

DEFAULT_NAMES = {
    "AAPL":"Apple Inc.","MSFT":"Microsoft Corp.","NVDA":"NVIDIA Corp.",
    "AMZN":"Amazon.com Inc.","GOOGL":"Alphabet Inc.","META":"Meta Platforms",
    "TSLA":"Tesla Inc.","JPM":"JPMorgan Chase","V":"Visa Inc.",
    "JNJ":"Johnson & Johnson","WMT":"Walmart Inc.","HD":"Home Depot",
    "PG":"Procter & Gamble","KO":"Coca-Cola Co.","MCD":"McDonald's Corp.",
    "BA":"Boeing Co.","GS":"Goldman Sachs","CVX":"Chevron Corp.",
    "IBM":"IBM Corp.","INTC":"Intel Corp.","CSCO":"Cisco Systems",
    "DIS":"Walt Disney Co.","VZ":"Verizon","MRK":"Merck & Co.",
    "UNH":"UnitedHealth Group","AXP":"American Express","CAT":"Caterpillar",
    "HON":"Honeywell","MMM":"3M Co.","TRV":"Travelers Cos.",
    "CRM":"Salesforce","AMGN":"Amgen","DOW":"Dow Inc.","NKE":"Nike",
}

DEFAULT_SECTORS = {
    "AAPL":"Technologie","MSFT":"Technologie","NVDA":"Technologie",
    "INTC":"Technologie","IBM":"Technologie","CSCO":"Technologie","CRM":"Technologie",
    "JPM":"Finance","GS":"Finance","AXP":"Finance","V":"Finance","TRV":"Finance",
    "JNJ":"Santé","MRK":"Santé","AMGN":"Santé","UNH":"Santé",
    "BA":"Industrie","CAT":"Industrie","HON":"Industrie","MMM":"Industrie",
    "WMT":"Consommation de base","KO":"Consommation de base","PG":"Consommation de base",
    "MCD":"Consommation discrétionnaire","HD":"Consommation discrétionnaire",
    "DIS":"Consommation discrétionnaire","NKE":"Consommation discrétionnaire",
    "CVX":"Énergie","DOW":"Matériaux","VZ":"Télécommunications",
}


def get_latest_price(ticker: str):
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None


def build_position_rows(positions):
    rows = []
    invested_value = 0.0
    invested_cost = 0.0
    real_prices = 0

    for pos in positions:
        try:
            if isinstance(pos, dict):
                ticker = str(pos.get("ticker", "")).upper().strip()
                company_name = pos.get("company_name") or pos.get("name") or ""
                qty = float(pos.get("quantity", 0) or 0)
                avg_buy_price = float(pos.get("avg_buy_price", 0) or 0)
            else:
                ticker, company_name, qty, avg_buy_price = pos[0], pos[1], float(pos[2]), float(pos[3])
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
            "ticker": ticker, "name": company_name,
            "qty": qty, "avg": avg_buy_price,
            "current": current_price, "value": value,
            "cost": cost, "pnl_value": pnl_value,
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
        return ("Compléter votre profil investisseur",
                "Commencez par répondre au questionnaire IA pour que FinPilot adapte les recommandations à votre tolérance au risque.",
                "pages/analyse.py", "Analyser mon profil")
    if nb_recommended == 0:
        return ("Générer des recommandations IA",
                "Votre profil est connu, mais aucune recommandation n'est sauvegardée. Lancez le calcul financier pour obtenir un Top 5 exploitable.",
                "pages/analyse.py", "Voir les recommandations")
    if not position_rows:
        return ("Construire un premier portefeuille",
                "Vous avez du cash disponible mais aucune position ouverte. Simulez un premier achat depuis les recommandations IA.",
                "pages/analyse.py", "Choisir une action")
    if len(position_rows) == 1:
        return ("Réduire la concentration",
                "Votre portefeuille contient une seule ligne. Ajouter une deuxième position peut réduire le risque spécifique.",
                "pages/portefeuille.py", "Gérer le portefeuille")
    if cash_weight > 70:
        return ("Utiliser une partie du cash",
                f"Votre portefeuille reste très liquide ({cash_weight:.1f}% de cash). Une allocation progressive peut améliorer le potentiel de rendement.",
                "pages/analyse.py", "Identifier des opportunités")
    return ("Suivre et ajuster le portefeuille",
            f"Profil dominant : {profil}. Continuez à suivre les positions et comparer les recommandations IA avant tout nouvel arbitrage.",
            "pages/portefeuille.py", "Voir le portefeuille")


def portfolio_health(position_rows, cash_balance, total_portfolio):
    cash_weight = cash_balance / total_portfolio * 100 if total_portfolio > 0 else 0
    if not position_rows:
        diversification, status = 0, "À construire"
        text = "Aucune position ouverte. Le portefeuille est essentiellement liquide."
    elif len(position_rows) == 1:
        diversification, status = 25, "Concentré"
        text = "Une seule position ouverte. Le risque spécifique est élevé."
    elif len(position_rows) < 4:
        diversification, status = 55, "En construction"
        text = "Quelques positions ouvertes. La diversification peut encore être renforcée."
    else:
        diversification, status = 80, "Diversifié"
        text = "Plusieurs positions ouvertes. Le portefeuille est plus équilibré."
    liquidity_status = "Très liquide" if cash_weight > 70 else ("Équilibré" if cash_weight > 35 else "Investi")
    return cash_weight, diversification, status, liquidity_status, text


def extract_recent_recommendations(recommended_rows, limit=4):
    items = []
    for row in recommended_rows[:limit]:
        try:
            if isinstance(row, dict):
                ticker = row.get("ticker") or row.get("symbol") or ""
                name = row.get("name") or DEFAULT_NAMES.get(str(ticker).upper(), str(ticker).upper())
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
pnl_css = "positive" if pnl >= 0 else "negative"

nb_positions = len(position_rows)
nb_analyses = insights.get("nb_analyses", 0)
nb_recommended = insights.get("nb_recommended", len(recommended_rows))
nb_orders = len(orders)

next_title, next_text, next_page, next_button = get_next_action(
    position_rows, cash_balance, total_portfolio, profil, nb_analyses, nb_recommended)

cash_weight, diversification_score, diversification_status, liquidity_status, health_text = portfolio_health(
    position_rows, cash_balance, total_portfolio)

recent_recos = extract_recent_recommendations(recommended_rows, limit=4)

# Injecter CSS dashboard
html(DASHBOARD_CSS)

# Sidebar
render_sidebar(active_page="dashboard", cash_balance=cash_balance, logout_callback=logout)


# ============================================================
# HERO
# ============================================================

html(f"""
<div class="db-hero">
    <div class="db-hero-grid"></div>
    <div class="db-hero-chart">
        <svg viewBox="0 0 600 220" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="hg" x1="0" x2="1">
                    <stop offset="0%" stop-color="#1A56DB" stop-opacity="0"/>
                    <stop offset="50%" stop-color="#60A5FA"/>
                    <stop offset="100%" stop-color="#FFFFFF"/>
                </linearGradient>
            </defs>
            <path d="M0,180 C60,160 90,120 140,135 C185,150 200,180 245,145
                     C285,112 310,118 350,88 C400,48 420,105 455,90
                     C500,70 510,30 560,18 C575,14 590,12 600,10"
                  fill="none" stroke="url(#hg)" stroke-width="2.5"
                  stroke-linecap="round" opacity="0.7"/>
            <circle cx="140" cy="135" r="4" fill="#60A5FA" opacity="0.8"/>
            <circle cx="245" cy="145" r="4" fill="#60A5FA" opacity="0.8"/>
            <circle cx="350" cy="88"  r="4" fill="#93C5FD" opacity="0.8"/>
            <circle cx="455" cy="90"  r="4" fill="#93C5FD" opacity="0.8"/>
            <circle cx="560" cy="18"  r="4" fill="#BFDBFE" opacity="0.8"/>
        </svg>
    </div>
    <div class="db-hero-content">
        <div class="db-hero-label">✦ Tableau de bord</div>
        <div class="db-hero-title">Bienvenue, {username}</div>
        <div class="db-hero-sub">
            Votre tableau de bord synthétise votre situation financière et l'activité IA.
            Obtenez une vue d'ensemble claire et des actions recommandées pour avancer.
        </div>
        <div class="db-hero-badges">
            <div class="db-hero-badge">Profil : {profil}</div>
            <div class="db-hero-badge">Capital : {money_dollar(total_portfolio)}</div>
            <div class="db-hero-badge">Positions : {nb_positions}</div>
            <div class="db-hero-badge">Analyses IA : {nb_analyses}</div>
        </div>
    </div>
</div>
""")


# ============================================================
# KPI CARDS
# ============================================================

html(f"""
<div class="db-kpi-grid">
    <div class="db-kpi accent-blue">
        <div class="db-kpi-label">Valeur totale</div>
        <div class="db-kpi-value">{money_dollar(total_portfolio)}</div>
        <div class="db-kpi-sub">Portefeuille + cash</div>
    </div>
    <div class="db-kpi accent-indigo">
        <div class="db-kpi-label">Profil investisseur</div>
        <div class="db-kpi-value">{profil}</div>
        <div class="db-kpi-sub">Score risque : {risk_score}/100</div>
    </div>
    <div class="db-kpi {'accent-green' if pnl >= 0 else 'accent-red'}">
        <div class="db-kpi-label">Gain latent</div>
        <div class="db-kpi-value {pnl_css}">{pnl_sign}{money_dollar(pnl)}</div>
        <div class="db-kpi-sub">{pnl_sign}{pnl_pct:.2f}% sur positions</div>
    </div>
    <div class="db-kpi accent-indigo">
        <div class="db-kpi-label">Activité IA</div>
        <div class="db-kpi-value">{nb_analyses}</div>
        <div class="db-kpi-sub">Analyse(s) de profil</div>
    </div>
</div>
""")


# ============================================================
# MAIN CONTENT
# ============================================================

left, right = st.columns([1.65, 1], gap="medium")

with left:

    # Recommandation IA
    html(f"""
    <div class="db-card">
        <div class="db-reco">
            <div class="db-reco-icon"></div>
            <div>
                <div class="db-reco-kicker">Prochaine action recommandée</div>
                <div class="db-reco-title">{next_title}</div>
                <div class="db-reco-text">{next_text}</div>
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

    st.markdown("<div style='height:.2rem'></div>", unsafe_allow_html=True)

    # État portefeuille
    html(f"""
    <div class="db-card">
        <div class="db-card-title">État global du portefeuille</div>
        <div class="db-status-grid">
            <div class="db-status-box">
                <div class="db-status-label">Liquidité</div>
                <div class="db-status-value">{cash_weight:.1f}%</div>
                <div class="db-status-text">{liquidity_status}</div>
                <div class="db-progress"><div class="db-progress-fill" style="width:{min(cash_weight,100)}%"></div></div>
            </div>
            <div class="db-status-box">
                <div class="db-status-label">Diversification</div>
                <div class="db-status-value">{diversification_score}/100</div>
                <div class="db-status-text">{diversification_status}</div>
                <div class="db-progress"><div class="db-progress-fill" style="width:{diversification_score}%"></div></div>
            </div>
            <div class="db-status-box">
                <div class="db-status-label">Positions</div>
                <div class="db-status-value">{nb_positions}</div>
                <div class="db-status-text">Ligne(s) suivie(s)</div>
                <div class="db-progress"><div class="db-progress-fill" style="width:{min(nb_positions*18,100)}%"></div></div>
            </div>
        </div>
        <div class="db-quick-text"><b>Lecture rapide</b> — {health_text}</div>
    </div>
    """)

    # Activité IA
    secteur_txt = ", ".join(insights.get("secteurs_favoris", [])) if insights.get("secteurs_favoris") else "Aucune préférence sectorielle dominante"
    action_txt = ", ".join(insights.get("actions_recurrentes", [])[:4]) if insights.get("actions_recurrentes") else "Aucune action récurrente"

    html(f"""
    <div class="db-card">
        <div class="db-card-title">Dernière activité IA</div>
        <div class="db-quick-text">
            <b>Profil dominant :</b> {profil}<br>
            <b>Secteurs fréquents :</b> {secteur_txt}<br>
            <b>Actions analysées :</b> {action_txt}
        </div>
    </div>
    """)

    # Recommandations récentes
    if recent_recos:
        reco_items = ""
        for ticker, name, score in recent_recos:
            score_html = f'<span class="db-reco-score">Score {score:.1f}</span>' if isinstance(score, (int, float)) else ""
            reco_items += f"""
            <div class="db-reco-item">
                <div>
                    <div class="db-reco-ticker">{ticker}</div>
                    <div class="db-reco-name">{name}</div>
                </div>
                {score_html}
            </div>"""
        html(f'<div class="db-card"><div class="db-card-title">Recommandations récentes</div>{reco_items}</div>')
    else:
        html("""
        <div class="db-card">
            <div class="db-card-title">Recommandations récentes</div>
            <div class="db-quick-text">Lancez une analyse IA pour alimenter cette section.</div>
        </div>
        """)


with right:

    actions_value = sum(row["value"] for row in position_rows)
    total_alloc = cash_balance + actions_value if (cash_balance + actions_value) > 0 else 1
    cash_pct = round(cash_balance / total_alloc * 100)

    # Répartition
    html(f"""
    <div class="db-card">
        <div class="db-card-title">Répartition simplifiée</div>
        <div class="db-card-sub">Vue synthétique — détails dans la page Portefeuille.</div>
        <div class="db-donut-wrap">
            <div class="db-donut">
                <div class="db-donut-center">
                    {cash_pct}%<span>Cash</span>
                </div>
            </div>
            <div>
                <div class="db-legend-row">
                    <div class="db-legend-dot" style="background:#1A56DB"></div>
                    <span style="color:#374151;font-size:.85rem;font-weight:600;">Cash</span>
                    <span style="color:#9CA3AF;font-size:.82rem;margin-left:auto;">{cash_pct}%</span>
                </div>
                {''.join(f"""<div class="db-legend-row"><div class="db-legend-dot" style="background:#60A5FA"></div><span style="color:#374151;font-size:.85rem;font-weight:600;">{r['ticker']}</span><span style="color:#9CA3AF;font-size:.82rem;margin-left:auto;">{round(r['value']/total_alloc*100)}%</span></div>""" for r in position_rows[:4])}
            </div>
        </div>
    </div>
    """)

    # Résumé chiffré
    html(f"""
    <div class="db-card">
        <div class="db-card-title">Résumé chiffré</div>
        <div class="db-summary-row">
            <span class="db-summary-label">Valeur totale</span>
            <span class="db-summary-value">{money_dollar(total_portfolio)}</span>
        </div>
        <div class="db-summary-row">
            <span class="db-summary-label">Cash</span>
            <span class="db-summary-value">{money_dollar(cash_balance)}</span>
        </div>
        <div class="db-summary-row">
            <span class="db-summary-label">Positions</span>
            <span class="db-summary-value">{nb_positions}</span>
        </div>
        <div class="db-summary-row">
            <span class="db-summary-label">Ordres simulés</span>
            <span class="db-summary-value">{nb_orders}</span>
        </div>
    </div>
    """)

    # Actions rapides
    html("""<div class="db-card"><div class="db-card-title">Actions rapides</div></div>""")

    if st.button("Analyser mon profil", use_container_width=True, type="primary", key="analyser_profil_app"):
        st.switch_page("pages/analyse.py")
    if st.button("Gérer mon portefeuille", use_container_width=True, key="gerer_portefeuille_app"):
        st.switch_page("pages/portefeuille.py")
    if st.button("Voir l'historique", use_container_width=True, key="voir_historique_app"):
        st.switch_page("pages/historique.py")
