import streamlit as st
import plotly.graph_objects as go
from textwrap import dedent

from auth import init_auth_state, render_auth_screen, logout
from database import (
    init_db,
    get_user_by_id,
    get_user_cash_balance,
    get_user_initial_capital,
    reset_user_portfolio,
    load_user_history,
    get_user_orders,
    get_portfolio_positions,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar
from utils import get_history_summary, get_risk_score


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Profil",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.logged_in:
    render_auth_screen()
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def html(content: str):
    cleaned = "\n".join(line.strip() for line in dedent(content).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def safe_value(value, default="Non renseigné"):
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def initials_from_user(username, email):
    username = safe_value(username, "")
    email = safe_value(email, "")

    source = username if username else email

    if "@" in source:
        source = source.split("@")[0]

    source = source.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    parts = [p for p in source.split() if p]

    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()

    if len(parts) == 1:
        return parts[0][:2].upper()

    return "FP"


def display_name_from_user(username, email):
    username = safe_value(username, "")

    if username and "@" not in username:
        return username[:1].upper() + username[1:]

    email = safe_value(email, "")

    if "@" in email:
        local = email.split("@")[0]
        local = local.replace(".", " ").replace("_", " ").replace("-", " ")
        return local[:1].upper() + local[1:]

    return "Investisseur"


def profile_distribution(history_rows):
    counts = {"Prudent": 0, "Modéré": 0, "Dynamique": 0}

    for item in history_rows:
        profil = item.get("profil") if isinstance(item, dict) else None

        if profil in counts:
            counts[profil] += 1

    return counts


def get_order_field(order, key, default=None):
    if isinstance(order, dict):
        return order.get(key, default)
    return getattr(order, key, default)


def build_activity_items(history_rows, orders, limit=5):
    items = []

    for order in orders[:limit]:
        order_type = get_order_field(order, "order_type", "")
        ticker = get_order_field(order, "ticker", "")
        qty = get_order_field(order, "quantity", 0)
        total = get_order_field(order, "total", 0)
        created_at = get_order_field(order, "created_at", "")

        label = "Achat" if str(order_type).upper() == "BUY" else "Vente"

        items.append(
            {
                "title": f"{label} · {ticker}",
                "text": f"Quantité {float(qty):.0f} · Montant ${float(total):,.2f}",
                "date": str(created_at)[:16],
                "type": "order",
            }
        )

    for analysis in history_rows[:limit]:
        profil = analysis.get("profil", "Profil") if isinstance(analysis, dict) else "Profil"
        score = analysis.get("score", 0) if isinstance(analysis, dict) else 0
        created_at = analysis.get("created_at", "") if isinstance(analysis, dict) else ""

        items.append(
            {
                "title": f"Analyse IA · {profil}",
                "text": f"Score investisseur : {score}",
                "date": str(created_at)[:16],
                "type": "analysis",
            }
        )

    items = sorted(items, key=lambda x: x["date"], reverse=True)
    return items[:limit]


# ============================================================
# STYLE
# ============================================================

html(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }


        /* Keep Streamlit's native sidebar buttons visible */
        button[data-testid="stSidebarCollapseButton"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }

        [data-testid="collapsedControl"],
        button[data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        button[data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            position: fixed !important;
            top: 86px !important;
            left: 12px !important;
            z-index: 999999 !important;
            background: linear-gradient(135deg, #2F7CFF, #6C63FF) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
            border-radius: 14px !important;
            width: 44px !important;
            height: 44px !important;
            box-shadow: 0 10px 24px rgba(47,124,255,0.28) !important;
        }

        [data-testid="collapsedControl"] svg,
        button[data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        button[data-testid="stSidebarCollapsedControl"] svg {
            color: white !important;
            fill: white !important;
            stroke: white !important;
            width: 22px !important;
            height: 22px !important;
        }

        /* Do not cover the collapsed button with custom elements */
        [data-testid="stAppViewContainer"] {
            overflow-x: hidden !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 4%, rgba(47,124,255,0.13), transparent 30%),
                radial-gradient(circle at 90% 5%, rgba(49,230,168,0.16), transparent 30%),
                linear-gradient(180deg, #F4F8FF 0%, #EAF1FF 54%, #F9FBFF 100%) !important;
        }

        .block-container {
            max-width: 1760px !important;
            padding-top: 1.7rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
        }

        .profile-hero {
            background:
                linear-gradient(135deg, rgba(11,39,84,0.98), rgba(43,121,226,0.95)),
                radial-gradient(circle at 92% 10%, rgba(49,230,168,0.22), transparent 30%);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 30px;
            padding: 2.1rem 2.25rem;
            color: white;
            box-shadow: 0 22px 55px rgba(15, 52, 110, 0.22);
            margin-bottom: 1.15rem;
            position: relative;
            overflow: hidden;
        }

        .profile-hero::after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            border-radius: 50%;
            right: -80px;
            top: -90px;
            background: rgba(255,255,255,0.10);
        }

        .hero-label {
            color: #8DEBFF;
            font-size: 0.92rem;
            font-weight: 900;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.7rem;
            position: relative;
            z-index: 2;
        }

        .hero-title {
            color: white;
            font-size: 3.1rem;
            line-height: 1.05;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.75rem;
            position: relative;
            z-index: 2;
        }

        .hero-text {
            color: rgba(255,255,255,0.90);
            font-size: 1.12rem;
            line-height: 1.75;
            max-width: 980px;
            position: relative;
            z-index: 2;
        }

        .hero-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1.1rem;
            position: relative;
            z-index: 2;
        }

        .hero-chip {
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            padding: 0.55rem 0.95rem;
            border-radius: 999px;
            font-size: 0.94rem;
            font-weight: 800;
            color: white;
        }

        .profile-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid #D7E3F8;
            border-radius: 26px;
            padding: 1.45rem;
            box-shadow: 0 14px 34px rgba(28, 64, 132, 0.08);
            margin-bottom: 1rem;
        }

        .profile-main-card {
            background:
                linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%),
                radial-gradient(circle at 92% 0%, rgba(47,124,255,0.08), transparent 34%);
            border: 1px solid #D7E3F8;
            border-radius: 28px;
            padding: 1.65rem;
            box-shadow: 0 18px 42px rgba(28, 64, 132, 0.10);
            margin-bottom: 1rem;
            min-height: 360px;
            text-align: center;
        }

        .avatar {
            width: 98px;
            height: 98px;
            border-radius: 30px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Sora', sans-serif;
            font-size: 2.05rem;
            font-weight: 900;
            margin: 0 auto 1.1rem auto;
            box-shadow: 0 16px 32px rgba(47,124,255,0.20);
        }

        .profile-name {
            color: #10233F;
            font-size: 1.75rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.25;
            margin-bottom: 0.35rem;
        }

        .profile-email {
            color: #64748B;
            font-size: 1.02rem;
            line-height: 1.55;
            margin-bottom: 1rem;
        }

        .profile-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #EAFBF4;
            color: #1C9C73;
            border: 1px solid #C5F3E1;
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            font-size: 0.95rem;
            font-weight: 900;
            margin-bottom: 1rem;
        }

        .member-since {
            color: #64748B;
            font-size: 0.98rem;
            line-height: 1.6;
            background: #F4F8FF;
            border: 1px solid #E1EAF8;
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }

        .kpi-card {
            border-radius: 24px;
            padding: 1.35rem;
            min-height: 145px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 34px rgba(30, 64, 140, 0.15);
            border: 1px solid rgba(255,255,255,0.14);
            margin-bottom: 1rem;
        }

        .kpi-card::after {
            content: "";
            position: absolute;
            width: 135px;
            height: 135px;
            border-radius: 50%;
            right: -42px;
            bottom: -48px;
            background: rgba(255,255,255,0.18);
        }

        .kpi-label {
            color: rgba(255,255,255,0.93);
            font-size: 0.86rem;
            font-weight: 900;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 2;
        }

        .kpi-value {
            color: white;
            font-size: 2.15rem;
            line-height: 1.05;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            position: relative;
            z-index: 2;
        }

        .kpi-sub {
            color: rgba(255,255,255,0.90);
            font-size: 0.98rem;
            line-height: 1.55;
            margin-top: 0.55rem;
            position: relative;
            z-index: 2;
        }

        .section-row {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .section-icon {
            min-width: 42px;
            width: 42px;
            height: 42px;
            border-radius: 14px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
        }

        .section-title {
            color: #10233F;
            font-size: 1.55rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.25;
        }

        .section-sub {
            color: #64748B;
            font-size: 1.04rem;
            line-height: 1.65;
            margin-top: 0.3rem;
        }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: 1rem;
        }

        .info-box {
            background: #F6FAFF;
            border: 1px solid #E0EAF8;
            border-radius: 18px;
            padding: 1rem;
        }

        .info-label {
            color: #6A7B94;
            font-size: 0.83rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.4rem;
        }

        .info-value {
            color: #10233F;
            font-size: 1.05rem;
            font-weight: 900;
            line-height: 1.45;
            word-break: break-word;
        }

        .risk-panel {
            background: linear-gradient(135deg, #FFFFFF, #F7FBFF);
            border: 1px solid #D7E3F8;
            border-radius: 26px;
            padding: 1.45rem;
            box-shadow: 0 14px 34px rgba(28, 64, 132, 0.08);
            margin-bottom: 1rem;
        }

        .risk-score {
            font-size: 2.7rem;
            line-height: 1;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            color: #2F7CFF;
            margin: 0.6rem 0 0.25rem 0;
        }

        .risk-text {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.65;
        }

        .progress-wrap {
            height: 10px;
            background: #E7EEF9;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 0.9rem;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
        }

        .activity-item {
            background: #FFFFFF;
            border: 1px solid #DDE7F6;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 8px 22px rgba(22, 46, 90, 0.05);
        }

        .activity-title {
            color: #10233F;
            font-size: 1.05rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.25rem;
        }

        .activity-text {
            color: #64748B;
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .activity-date {
            color: #2F7CFF;
            font-size: 0.86rem;
            font-weight: 800;
            margin-top: 0.45rem;
        }

        .reset-card {
            background: linear-gradient(135deg, #FFFFFF, #FFF8F8);
            border: 1px solid #F0D2D8;
            border-radius: 24px;
            padding: 1.4rem;
            box-shadow: 0 12px 30px rgba(116, 20, 45, 0.05);
            margin-top: 1rem;
        }

        .reset-title {
            color: #10233F;
            font-size: 1.35rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.45rem;
        }

        .reset-text {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.65;
        }

        div[data-testid="stNumberInput"] label,
        div[data-testid="stCheckbox"] label {
            color: #10233F !important;
            font-weight: 800 !important;
            font-size: 0.98rem !important;
        }

        div[data-testid="stNumberInput"] input {
            border-radius: 15px !important;
            min-height: 50px !important;
            font-size: 1rem !important;
        }

        div[data-testid="stButton"] button {
            min-height: 54px !important;
            border-radius: 16px !important;
            font-weight: 900 !important;
            font-size: 1rem !important;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(90deg, #2F7CFF, #6C63FF) !important;
            border: none !important;
            color: white !important;
        }
    </style>
    """
)


# ============================================================
# DATA
# ============================================================

user_id = st.session_state.user_id

user = get_user_by_id(user_id) or {}
username = safe_value(user.get("username"), "")
email = safe_value(user.get("email"), "")
created_at = safe_value(user.get("created_at"), "Date indisponible")

display_name = display_name_from_user(username, email)
initials = initials_from_user(username, email)

cash_balance = get_user_cash_balance(user_id)
initial_capital = get_user_initial_capital(user_id)
history_rows = load_user_history(user_id)

try:
    orders = get_user_orders(user_id)
except Exception:
    orders = []

positions = get_portfolio_positions(user_id)

insights = get_history_summary(history_rows, [])
profil = insights.get("profil_dominant") or user.get("profile") or "Modéré"
risk_score = get_risk_score(profil)

nb_analyses = len(history_rows)
nb_orders = len(orders)
nb_positions = len(positions)

capital_used = max(initial_capital - cash_balance, 0)
capital_used_pct = (capital_used / initial_capital * 100) if initial_capital > 0 else 0

dist = profile_distribution(history_rows)
recent_activity = build_activity_items(history_rows, orders, limit=5)


# ============================================================
# SIDEBAR PREMIUM COMMUNE
# ============================================================

render_sidebar(
    active_page="profil",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# HERO
# ============================================================

html(
    f"""
    <div class="profile-hero">
        <div class="hero-label">Compte utilisateur</div>
        <div class="hero-title">Mon profil FinPilot</div>
        <div class="hero-text">
            Consultez votre identité de compte, votre profil investisseur, votre capital de simulation
            et vos statistiques d’utilisation.
        </div>
        <div class="hero-chip-row">
            <div class="hero-chip">Profil : {profil}</div>
            <div class="hero-chip">Capital initial : ${initial_capital:,.2f}</div>
            <div class="hero-chip">Cash : ${cash_balance:,.2f}</div>
            <div class="hero-chip">Analyses IA : {nb_analyses}</div>
        </div>
    </div>
    """
)


# ============================================================
# KPI
# ============================================================

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    html(
        f"""
        <div class="kpi-card" style="background:linear-gradient(135deg,#2F7CFF,#1E5FE6);">
            <div class="kpi-label">Capital initial</div>
            <div class="kpi-value">${initial_capital:,.2f}</div>
            <div class="kpi-sub">Montant choisi au démarrage</div>
        </div>
        """
    )

with k2:
    html(
        f"""
        <div class="kpi-card" style="background:linear-gradient(135deg,#31C48D,#149D72);">
            <div class="kpi-label">Cash disponible</div>
            <div class="kpi-value">${cash_balance:,.2f}</div>
            <div class="kpi-sub">Capital non investi</div>
        </div>
        """
    )

with k3:
    html(
        f"""
        <div class="kpi-card" style="background:linear-gradient(135deg,#7A5CFF,#5E3EEA);">
            <div class="kpi-label">Analyses IA</div>
            <div class="kpi-value">{nb_analyses}</div>
            <div class="kpi-sub">Profils enregistrés</div>
        </div>
        """
    )

with k4:
    html(
        f"""
        <div class="kpi-card" style="background:linear-gradient(135deg,#FFAE36,#F18A00);">
            <div class="kpi-label">Ordres</div>
            <div class="kpi-value">{nb_orders}</div>
            <div class="kpi-sub">Opérations simulées</div>
        </div>
        """
    )

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)


# ============================================================
# MAIN CONTENT
# ============================================================

left, right = st.columns([1.05, 1.65], gap="large")

with left:
    html(
        f"""
        <div class="profile-main-card">
            <div class="avatar">{initials}</div>
            <div class="profile-name">{display_name}</div>
            <div class="profile-email">{email}</div>
            <div class="profile-badge">Profil investisseur : {profil}</div>
            <div class="member-since">
                Membre depuis : <b>{created_at[:10]}</b><br>
                Positions ouvertes : <b>{nb_positions}</b>
            </div>
        </div>
        """
    )

    html(
        f"""
        <div class="risk-panel">
            <div class="section-row">
                <div class="section-icon">R</div>
                <div>
                    <div class="section-title">Score de risque</div>
                    <div class="section-sub">Score estimé à partir du dernier profil investisseur.</div>
                </div>
            </div>
            <div class="risk-score">{risk_score}/100</div>
            <div class="risk-text">
                Plus le score est élevé, plus le profil accepte la volatilité et la recherche de rendement.
            </div>
            <div class="progress-wrap">
                <div class="progress-fill" style="width:{min(risk_score, 100)}%;"></div>
            </div>
        </div>
        """
    )

    html(
        f"""
        <div class="risk-panel">
            <div class="section-row">
                <div class="section-icon">$</div>
                <div>
                    <div class="section-title">Utilisation du capital</div>
                    <div class="section-sub">Part approximative du capital déjà mobilisée.</div>
                </div>
            </div>
            <div class="risk-score">{capital_used_pct:.1f}%</div>
            <div class="risk-text">
                Montant mobilisé : <b>${capital_used:,.2f}</b> sur <b>${initial_capital:,.2f}</b>.
            </div>
            <div class="progress-wrap">
                <div class="progress-fill" style="width:{min(capital_used_pct, 100)}%;"></div>
            </div>
        </div>
        """
    )


with right:
    html(
        """
        <div class="profile-card">
            <div class="section-row">
                <div class="section-icon">ID</div>
                <div>
                    <div class="section-title">Informations du compte</div>
                    <div class="section-sub">Ces informations identifient votre espace FinPilot.</div>
                </div>
            </div>
        """
    )

    html(
        f"""
        <div class="info-grid">
            <div class="info-box">
                <div class="info-label">Nom d’utilisateur</div>
                <div class="info-value">{safe_value(username, email)}</div>
            </div>
            <div class="info-box">
                <div class="info-label">Adresse email</div>
                <div class="info-value">{email}</div>
            </div>
            <div class="info-box">
                <div class="info-label">Profil actuel</div>
                <div class="info-value">{profil}</div>
            </div>
            <div class="info-box">
                <div class="info-label">Capital configuré</div>
                <div class="info-value">${initial_capital:,.2f}</div>
            </div>
        </div>
        </div>
        """
    )

    html(
        """
        <div class="profile-card">
            <div class="section-row">
                <div class="section-icon">P</div>
                <div>
                    <div class="section-title">Répartition des profils détectés</div>
                    <div class="section-sub">Historique des profils obtenus lors des analyses IA.</div>
                </div>
            </div>
        </div>
        """
    )

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(dist.keys()),
                y=list(dist.values()),
                marker=dict(
                    color=["#31C48D", "#2F7CFF", "#F3A712"],
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{x}</b><br>Analyses : %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#10233F", size=13),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#DDE7F6", zeroline=False, rangemode="tozero"),
        showlegend=False,
    )

    html('<div class="profile-card" style="padding:1rem;">')
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    html("</div>")

    html(
        """
        <div class="profile-card">
            <div class="section-row">
                <div class="section-icon">A</div>
                <div>
                    <div class="section-title">Activité récente</div>
                    <div class="section-sub">Dernières analyses et dernières opérations simulées.</div>
                </div>
            </div>
        </div>
        """
    )

    if recent_activity:
        for item in recent_activity:
            html(
                f"""
                <div class="activity-item">
                    <div class="activity-title">{item["title"]}</div>
                    <div class="activity-text">{item["text"]}</div>
                    <div class="activity-date">{item["date"]}</div>
                </div>
                """
            )
    else:
        html(
            """
            <div class="activity-item">
                <div class="activity-title">Aucune activité récente</div>
                <div class="activity-text">Lancez une analyse IA ou simulez un ordre pour alimenter cette section.</div>
            </div>
            """
        )

    html(
        """
        <div class="reset-card">
            <div class="reset-title">Réinitialiser le portefeuille</div>
            <div class="reset-text">
                Cette action supprime les positions et les ordres existants, puis remet le cash au nouveau capital choisi.
                À utiliser seulement si vous voulez recommencer votre simulation.
            </div>
        </div>
        """
    )

    reset_capital = st.number_input(
        "Nouveau capital de simulation ($)",
        min_value=100.0,
        max_value=10000000.0,
        value=float(initial_capital if initial_capital > 0 else 5000.0),
        step=100.0,
        key="reset_capital_input",
    )

    confirm_reset = st.checkbox(
        "Je confirme vouloir supprimer mes positions et mes ordres pour repartir avec ce capital.",
        key="confirm_reset_portfolio",
    )

    if st.button("Réinitialiser mon portefeuille", use_container_width=True, type="primary", key="reset_portfolio"):
        if not confirm_reset:
            st.error("Veuillez confirmer la réinitialisation.")
        else:
            try:
                reset_user_portfolio(user_id, reset_capital)
                st.success(f"Portefeuille réinitialisé avec ${reset_capital:,.2f}.")
                st.rerun()
            except Exception as e:
                st.error(f"Impossible de réinitialiser le portefeuille : {e}")