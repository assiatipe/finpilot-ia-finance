import streamlit as st
import sys
import os
from textwrap import dedent
from collections import Counter
from datetime import datetime, timedelta

import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import init_db, load_user_history, get_user_orders, get_user_cash_balance
from styles import load_global_styles
from sidebar_ui import render_sidebar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Historique",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.switch_page("app.py")
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def html(content: str):
    cleaned = "\n".join(line.strip() for line in dedent(content).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def get_value(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except Exception:
        return default


def parse_date(value):
    if not value:
        return None

    value = str(value).replace("T", " ").strip()

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value[:19], fmt)
        except Exception:
            pass

    return None


def format_date(value):
    dt = parse_date(value)
    if not dt:
        return "Date indisponible"
    return dt.strftime("%d/%m/%Y · %H:%M")


def profile_badge_class(profile):
    if profile == "Prudent":
        return "fp-pill-green"
    if profile == "Modéré":
        return "fp-pill-blue"
    if profile == "Dynamique":
        return "fp-pill-gold"
    return "fp-pill-blue"


def score_color(score):
    try:
        score = float(score)
    except Exception:
        score = 0

    if score <= 20:
        return "#31B889"
    if score <= 40:
        return "#2F7CFF"
    return "#D99A18"


def clean_recommendations(tickers):
    tickers = str(tickers or "").strip()

    if not tickers:
        return "Aucune recommandation enregistrée"

    values = [x.strip() for x in tickers.split(",") if x.strip()]

    if not values:
        return "Aucune recommandation enregistrée"

    return " · ".join(values)


def filter_by_period(rows, period, date_key="created_at"):
    if period == "Tout":
        return rows

    now = datetime.now()

    if period == "Aujourd’hui":
        start = datetime(now.year, now.month, now.day)
    elif period == "7 derniers jours":
        start = now - timedelta(days=7)
    elif period == "30 derniers jours":
        start = now - timedelta(days=30)
    else:
        return rows

    filtered = []

    for row in rows:
        dt = parse_date(get_value(row, date_key, ""))
        if dt and dt >= start:
            filtered.append(row)

    return filtered


def build_timeline(history_rows, orders, limit=10):
    items = []

    for row in history_rows:
        dt_raw = get_value(row, "created_at", "")
        dt = parse_date(dt_raw)

        items.append(
            {
                "date_raw": dt_raw,
                "date_obj": dt,
                "type": "Analyse IA",
                "title": f"Profil {get_value(row, 'profil', 'N/A')}",
                "subtitle": f"Score {get_value(row, 'score', 0)}/55",
                "extra": clean_recommendations(get_value(row, "recommended_tickers", "")),
                "color": "#2F7CFF",
            }
        )

    for order in orders:
        dt_raw = get_value(order, "created_at", "")
        dt = parse_date(dt_raw)
        otype = str(get_value(order, "order_type", "BUY")).upper()
        label = "Achat" if otype == "BUY" else "Vente"
        ticker = get_value(order, "ticker", "")

        try:
            qty = float(get_value(order, "quantity", 0))
            total = float(get_value(order, "total", 0))
        except Exception:
            qty = 0
            total = 0

        items.append(
            {
                "date_raw": dt_raw,
                "date_obj": dt,
                "type": "Ordre simulé",
                "title": f"{label} {ticker}",
                "subtitle": f"Quantité {qty:.0f} · Total ${total:,.2f}",
                "extra": "Transaction enregistrée dans le portefeuille",
                "color": "#31B889" if otype == "BUY" else "#D44D61",
            }
        )

    items = sorted(
        items,
        key=lambda x: x["date_obj"] if x["date_obj"] else datetime.min,
        reverse=True,
    )

    return items[:limit]


def history_reading(history_rows, orders):
    if not history_rows and not orders:
        return "Aucune activité n’est encore enregistrée. Lancez une analyse IA ou simulez un ordre pour commencer à construire votre historique."

    profiles = [get_value(row, "profil", "") for row in history_rows if get_value(row, "profil", "")]
    profile_counts = Counter(profiles)

    if profile_counts:
        dominant = profile_counts.most_common(1)[0][0]
        total = sum(profile_counts.values())

        if dominant == "Prudent":
            msg = "Votre historique montre surtout un profil prudent : priorité à la stabilité, à la protection du capital et aux actifs moins volatils."
        elif dominant == "Modéré":
            msg = "Votre historique indique un profil équilibré : combinaison possible entre actifs solides et potentiel de croissance."
        else:
            msg = "Votre historique montre une orientation dynamique : potentiel de rendement plus élevé, mais volatilité à surveiller."

        msg += f" Profil dominant : {dominant} sur {total} analyse(s)."
    else:
        msg = "Aucune analyse de profil n’est encore disponible."

    if orders:
        msg += f" Vous avez aussi {len(orders)} ordre(s) simulé(s), utile(s) pour suivre vos décisions concrètes."

    return msg


def render_profile_distribution_card(profile_counts):
    total = sum(profile_counts.values())

    profiles = [
        ("Prudent", "#31B889"),
        ("Modéré", "#2F7CFF"),
        ("Dynamique", "#D99A18"),
    ]

    rows_html = ""

    for label, color in profiles:
        count = int(profile_counts.get(label, 0))
        pct = (count / total * 100) if total > 0 else 0

        rows_html += f"""
        <div class="profile-stat-row">
            <div class="profile-stat-label">{label}</div>
            <div class="profile-stat-track">
                <div class="profile-stat-fill" style="width:{pct:.1f}%;background:{color};"></div>
            </div>
            <div class="profile-stat-value">{count}</div>
        </div>
        """

    return f"""
    <div class="profile-distribution-card">
        <div class="profile-distribution-title">Répartition des profils</div>
        {rows_html}
    </div>
    """


def scores_over_time(history_rows):
    rows = []

    for row in history_rows:
        dt = parse_date(get_value(row, "created_at", ""))
        score = get_value(row, "score", 0)

        try:
            score = float(score)
        except Exception:
            score = 0

        if dt:
            rows.append((dt, score, get_value(row, "profil", "N/A")))

    rows = sorted(rows, key=lambda x: x[0])
    return rows


# ============================================================
# LOCAL STYLE
# ============================================================

html(
    """
    <style>
        .block-container {
            padding-top: 1.2rem !important;
        }

        .history-hero {
            background:
                linear-gradient(135deg, rgba(11,39,84,0.98), rgba(43,121,226,0.95)),
                radial-gradient(circle at 92% 10%, rgba(49,230,168,0.22), transparent 30%);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 30px;
            padding: 1.85rem 2.15rem;
            color: white;
            box-shadow: 0 22px 55px rgba(15, 52, 110, 0.22);
            margin-bottom: 0.85rem;
            position: relative;
            overflow: hidden;
        }

        .history-hero::after {
            content: "";
            position: absolute;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            right: -80px;
            top: -90px;
            background: rgba(255,255,255,0.10);
        }

        .history-label {
            color: #8DEBFF;
            font-size: 0.88rem;
            font-weight: 900;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.55rem;
            position: relative;
            z-index: 2;
        }

        .history-title {
            color: white;
            font-size: 2.75rem;
            line-height: 1.05;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.65rem;
            position: relative;
            z-index: 2;
        }

        .history-subtitle {
            color: rgba(255,255,255,0.90);
            font-size: 1.02rem;
            line-height: 1.65;
            max-width: 920px;
            position: relative;
            z-index: 2;
        }

        .history-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 0.95rem;
            position: relative;
            z-index: 2;
        }

        .history-chip {
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            padding: 0.5rem 0.85rem;
            border-radius: 999px;
            font-size: 0.86rem;
            font-weight: 800;
            color: white;
        }

        .history-kpi {
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            min-height: 126px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 14px 30px rgba(30, 64, 140, 0.14);
            border: 1px solid rgba(255,255,255,0.14);
            margin-bottom: 0.65rem;
        }

        .history-kpi::after {
            content: "";
            position: absolute;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            right: -42px;
            bottom: -48px;
            background: rgba(255,255,255,0.18);
        }

        .history-kpi-label {
            color: rgba(255,255,255,0.93);
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.45rem;
            position: relative;
            z-index: 2;
        }

        .history-kpi-value {
            color: white;
            font-size: 1.85rem;
            line-height: 1.05;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            position: relative;
            z-index: 2;
        }

        .history-kpi-sub {
            color: rgba(255,255,255,0.90);
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.45rem;
            position: relative;
            z-index: 2;
        }

        .history-section {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid #D7E3F8;
            border-radius: 24px;
            padding: 1.05rem 1.15rem;
            box-shadow: 0 12px 28px rgba(28, 64, 132, 0.07);
            margin-bottom: 0.65rem;
        }

        .section-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .section-icon {
            min-width: 38px;
            width: 38px;
            height: 38px;
            border-radius: 13px;
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
            font-size: 1.28rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.25;
        }

        .section-sub {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.55;
            margin-top: 0.2rem;
        }

        .reading-card {
            background: linear-gradient(135deg, rgba(47,124,255,0.09), rgba(49,230,168,0.10));
            border: 1px solid #D9E8F7;
            border-radius: 20px;
            padding: 1rem 1.15rem;
            color: #405A78;
            font-size: 0.98rem;
            line-height: 1.62;
            margin-bottom: 0.65rem;
        }

        .profile-distribution-card {
            background: #FFFFFF;
            border: 1px solid #D7E3F8;
            border-radius: 20px;
            padding: 1rem 1.15rem;
            box-shadow: 0 12px 28px rgba(28, 64, 132, 0.07);
            margin-bottom: 0.65rem;
        }

        .profile-distribution-title {
            color: #10233F;
            font-size: 1.08rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.8rem;
        }

        .profile-stat-row {
            display: grid;
            grid-template-columns: 96px 1fr 48px;
            gap: 0.7rem;
            align-items: center;
            margin-bottom: 0.7rem;
        }

        .profile-stat-row:last-child {
            margin-bottom: 0;
        }

        .profile-stat-label {
            color: #10233F;
            font-size: 0.92rem;
            font-weight: 900;
        }

        .profile-stat-track {
            height: 9px;
            background: #E7EEF9;
            border-radius: 999px;
            overflow: hidden;
        }

        .profile-stat-fill {
            height: 100%;
            border-radius: 999px;
        }

        .profile-stat-value {
            color: #64748B;
            font-size: 0.88rem;
            font-weight: 900;
            text-align: right;
        }

        .compact-chart-card {
            background: #FFFFFF;
            border: 1px solid #D7E3F8;
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(28, 64, 132, 0.07);
            padding: 0.35rem 0.55rem 0.2rem 0.55rem;
            margin-bottom: 0.65rem;
        }

        .timeline-item {
            background: #FFFFFF;
            border: 1px solid #DDE7F6;
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 8px 22px rgba(22, 46, 90, 0.05);
            position: relative;
        }

        .timeline-top {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-start;
        }

        .timeline-type {
            display: inline-block;
            padding: 0.35rem 0.72rem;
            border-radius: 999px;
            color: white;
            font-size: 0.78rem;
            font-weight: 900;
            margin-bottom: 0.55rem;
        }

        .timeline-title {
            color: #10233F;
            font-size: 1.05rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.25rem;
        }

        .timeline-subtitle {
            color: #64748B;
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .timeline-date {
            color: #2F7CFF;
            font-size: 0.86rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .score-bar-wrap {
            height: 9px;
            background: #E7EEF9;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 0.55rem;
            max-width: 150px;
        }

        .score-bar {
            height: 100%;
            border-radius: 999px;
        }

        .history-table-card {
            background: #FFFFFF;
            border: 1px solid #D7E3F8;
            border-radius: 24px;
            box-shadow: 0 14px 34px rgba(28, 64, 132, 0.08);
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .history-table-title {
            color: #10233F;
            font-size: 1.28rem;
            font-weight: 900;
            padding: 1.05rem 1.25rem;
            border-bottom: 1px solid #DDE7F6;
            font-family: 'Sora', sans-serif;
        }

        .history-row {
            display: grid;
            align-items: center;
            padding: 0.92rem 1.25rem;
            border-bottom: 1px solid #DDE7F6;
            gap: 0.9rem;
        }

        .history-row:last-child {
            border-bottom: none;
        }

        .history-row-head {
            background: #F4F8FF;
            color: #617693;
            font-size: 0.76rem;
            font-weight: 900;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .history-main {
            color: #10233F;
            font-size: 0.94rem;
            font-weight: 900;
            line-height: 1.35;
        }

        .history-sub {
            color: #64748B;
            font-size: 0.86rem;
            line-height: 1.45;
            margin-top: 0.18rem;
        }

        .filters-card {
            background: rgba(255,255,255,0.72);
            border: 1px solid #D7E3F8;
            border-radius: 20px;
            padding: 0.8rem 1rem;
            box-shadow: 0 10px 24px rgba(28,64,132,0.05);
            margin-bottom: 0.65rem;
        }

        div[data-testid="stSelectbox"] label {
            color: #10233F !important;
            font-weight: 800 !important;
            font-size: 0.9rem !important;
        }
    
        .element-container:has(.filters-card) {
            margin-top: -0.25rem !important;
        }

    </style>
    """
)


# ============================================================
# DATA
# ============================================================

user_id = st.session_state.user_id
history_rows = load_user_history(user_id)
orders = get_user_orders(user_id)

last_profile = get_value(history_rows[0], "profil", "Non disponible") if history_rows else "Non disponible"
profile_counts = Counter([get_value(row, "profil", "") for row in history_rows if get_value(row, "profil", "")])
dominant_profile = profile_counts.most_common(1)[0][0] if profile_counts else "Non disponible"

all_activity_dates = []

for row in history_rows:
    dt = parse_date(get_value(row, "created_at", ""))
    if dt:
        all_activity_dates.append(dt)

for row in orders:
    dt = parse_date(get_value(row, "created_at", ""))
    if dt:
        all_activity_dates.append(dt)

last_activity = max(all_activity_dates).strftime("%d/%m/%Y · %H:%M") if all_activity_dates else "Aucune activité"


try:
    cash_balance = get_user_cash_balance(user_id)
except Exception:
    cash_balance = 5100.0

# ============================================================
# SIDEBAR PREMIUM COMMUNE
# ============================================================

render_sidebar(
    active_page="historique",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# HERO
# ============================================================

html(
    f"""
    <div class="history-hero">
        <div class="history-label">Historique</div>
        <div class="history-title">Vos analyses et transactions</div>
        <div class="history-subtitle">
            Suivez l’évolution de vos profils, vos recommandations et vos ordres simulés.
            Cette page permet de comprendre vos décisions dans le temps.
        </div>
        <div class="history-chip-row">
            <div class="history-chip">Analyses : {len(history_rows)}</div>
            <div class="history-chip">Ordres : {len(orders)}</div>
            <div class="history-chip">Profil dominant : {dominant_profile}</div>
            <div class="history-chip">Dernière activité : {last_activity}</div>
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
        <div class="history-kpi" style="background:linear-gradient(135deg,#2F7CFF,#1E5FE6);">
            <div class="history-kpi-label">Analyses</div>
            <div class="history-kpi-value">{len(history_rows)}</div>
            <div class="history-kpi-sub">Profils investisseur enregistrés</div>
        </div>
        """
    )

with k2:
    html(
        f"""
        <div class="history-kpi" style="background:linear-gradient(135deg,#31C48D,#149D72);">
            <div class="history-kpi-label">Ordres</div>
            <div class="history-kpi-value">{len(orders)}</div>
            <div class="history-kpi-sub">Transactions simulées</div>
        </div>
        """
    )

with k3:
    html(
        f"""
        <div class="history-kpi" style="background:linear-gradient(135deg,#7A5CFF,#5E3EEA);">
            <div class="history-kpi-label">Profil dominant</div>
            <div class="history-kpi-value">{dominant_profile}</div>
            <div class="history-kpi-sub">Profil le plus fréquent</div>
        </div>
        """
    )

with k4:
    html(
        f"""
        <div class="history-kpi" style="background:linear-gradient(135deg,#FFAE36,#F18A00);">
            <div class="history-kpi-label">Dernier profil</div>
            <div class="history-kpi-value">{last_profile}</div>
            <div class="history-kpi-sub">Dernière analyse enregistrée</div>
        </div>
        """
    )


# ============================================================
# READING + CHART - COMPACT
# ============================================================

left, right = st.columns([1.05, 1], gap="large")

with left:
    html(
        f"""
        <div class="history-section">
            <div class="section-row">
                <div class="section-icon">L</div>
                <div>
                    <div class="section-title">Lecture rapide</div>
                    <div class="section-sub">Résumé automatique de votre historique.</div>
                </div>
            </div>
        </div>
        <div class="reading-card">{history_reading(history_rows, orders)}</div>
        {render_profile_distribution_card(profile_counts)}
        """
    )

with right:
    html(
        """
        <div class="history-section">
            <div class="section-row">
                <div class="section-icon">S</div>
                <div>
                    <div class="section-title">Évolution du score</div>
                    <div class="section-sub">Progression des scores investisseur au fil des analyses.</div>
                </div>
            </div>
        </div>
        """
    )

    score_rows = scores_over_time(history_rows)

    if score_rows:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=[x[0].strftime("%d/%m %H:%M") for x in score_rows],
                y=[x[1] for x in score_rows],
                mode="lines+markers",
                line=dict(width=4, color="#2F7CFF", shape="spline"),
                marker=dict(size=8, color="#31E6A8"),
                fill="tozeroy",
                fillcolor="rgba(47,124,255,0.12)",
                hovertemplate="<b>Score</b> : %{y}/55<br>%{x}<extra></extra>",
            )
        )

        fig.update_layout(
            height=245,
            margin=dict(l=14, r=14, t=12, b=24),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#10233F", size=12),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#DDE7F6", zeroline=False, range=[0, 55]),
            showlegend=False,
        )

        html('<div class="compact-chart-card">')
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        html("</div>")
    else:
        html(
            """
            <div class="history-section">
                <div class="section-title">Aucun score disponible</div>
                <div class="section-sub">Complétez le questionnaire dans Analyses IA pour afficher l’évolution.</div>
            </div>
            """
        )


# ============================================================
# FILTERS
# ============================================================

html('<div class="filters-card">')
f1, f2, f3 = st.columns([1, 1, 2], gap="medium")

with f1:
    selected_profile = st.selectbox(
        "Filtrer les analyses",
        ["Tous", "Prudent", "Modéré", "Dynamique"],
        key="history_profile_filter",
    )

with f2:
    selected_period = st.selectbox(
        "Période",
        ["Tout", "Aujourd’hui", "7 derniers jours", "30 derniers jours"],
        key="history_period_filter",
    )

with f3:
    html(
        """
        <div style="padding-top:1.68rem;color:#64748B;font-size:0.95rem;line-height:1.5;">
            Les filtres s’appliquent aux analyses, aux ordres et à la chronologie.
        </div>
        """
    )
html("</div>")

filtered_history = filter_by_period(history_rows, selected_period)

if selected_profile != "Tous":
    filtered_history = [
        row for row in filtered_history
        if get_value(row, "profil", "") == selected_profile
    ]

filtered_orders = filter_by_period(orders, selected_period)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(["Analyses de profil", "Ordres simulés", "Chronologie"])


with tab1:
    if filtered_history:
        html(
            """
            <div class="history-table-card">
                <div class="history-table-title">Historique des analyses</div>
                <div class="history-row history-row-head" style="grid-template-columns:1.1fr 1fr 2fr 1fr;">
                    <div>Profil</div>
                    <div>Score</div>
                    <div>Recommandations</div>
                    <div>Date</div>
                </div>
            """
        )

        for row in filtered_history:
            profil = get_value(row, "profil", "N/A")
            score = get_value(row, "score", 0)
            tickers = get_value(row, "recommended_tickers", "")
            date = format_date(get_value(row, "created_at", ""))

            try:
                score_float = float(score)
            except Exception:
                score_float = 0

            pct = min(max(score_float / 55 * 100, 0), 100)
            bar_color = score_color(score_float)

            html(
                f"""
                <div class="history-row" style="grid-template-columns:1.1fr 1fr 2fr 1fr;">
                    <div><span class="fp-pill {profile_badge_class(profil)}">{profil}</span></div>
                    <div>
                        <div class="history-main">{score}/55</div>
                        <div class="score-bar-wrap">
                            <div class="score-bar" style="width:{pct:.1f}%;background:{bar_color};"></div>
                        </div>
                    </div>
                    <div>
                        <div class="history-main">{clean_recommendations(tickers)}</div>
                        <div class="history-sub">Actifs proposés lors de l’analyse</div>
                    </div>
                    <div class="history-sub">{date}</div>
                </div>
                """
            )

        html("</div>")

    else:
        html(
            """
            <div class="history-section">
                <div class="section-title">Aucune analyse trouvée</div>
                <div class="section-sub">
                    Modifiez les filtres ou rendez-vous dans la page Analyses IA pour compléter le questionnaire investisseur.
                </div>
            </div>
            """
        )


with tab2:
    if filtered_orders:
        html(
            """
            <div class="history-table-card">
                <div class="history-table-title">Historique des ordres simulés</div>
                <div class="history-row history-row-head" style="grid-template-columns:1fr 0.8fr 1.2fr 1fr 1fr 1fr;">
                    <div>Ticker</div>
                    <div>Type</div>
                    <div>Quantité et prix</div>
                    <div>Total</div>
                    <div>Cash après</div>
                    <div>Date</div>
                </div>
            """
        )

        for order in filtered_orders:
            otype = str(get_value(order, "order_type", "BUY")).upper()
            ticker = get_value(order, "ticker", "")
            qty = float(get_value(order, "quantity", 0) or 0)
            price = float(get_value(order, "price", 0) or 0)
            total = float(get_value(order, "total", 0) or 0)
            cash_after = float(get_value(order, "cash_after", 0) or 0)
            date = format_date(get_value(order, "created_at", ""))

            pill_class = "fp-pill-green" if otype == "BUY" else "fp-pill-red"
            label = "Achat" if otype == "BUY" else "Vente"

            html(
                f"""
                <div class="history-row" style="grid-template-columns:1fr 0.8fr 1.2fr 1fr 1fr 1fr;">
                    <div class="history-main">{ticker}</div>
                    <div><span class="fp-pill {pill_class}">{label}</span></div>
                    <div>
                        <div class="history-main">{qty:.0f} × ${price:,.2f}</div>
                        <div class="history-sub">Quantité × prix</div>
                    </div>
                    <div class="history-main">${total:,.2f}</div>
                    <div class="history-main">${cash_after:,.2f}</div>
                    <div class="history-sub">{date}</div>
                </div>
                """
            )

        html("</div>")

    else:
        html(
            """
            <div class="history-section">
                <div class="section-title">Aucun ordre simulé</div>
                <div class="section-sub">
                    Rendez-vous dans la page Portefeuille ou Analyses IA pour simuler un achat ou une vente.
                </div>
            </div>
            """
        )


with tab3:
    items = build_timeline(filtered_history, filtered_orders, limit=12)

    if items:
        for item in items:
            html(
                f"""
                <div class="timeline-item">
                    <div class="timeline-top">
                        <div>
                            <div class="timeline-type" style="background:{item['color']};">{item['type']}</div>
                            <div class="timeline-title">{item['title']}</div>
                            <div class="timeline-subtitle">{item['subtitle']}</div>
                            <div class="history-sub">{item['extra']}</div>
                        </div>
                        <div class="timeline-date">{format_date(item['date_raw'])}</div>
                    </div>
                </div>
                """
            )
    else:
        html(
            """
            <div class="history-section">
                <div class="section-title">Aucune activité à afficher</div>
                <div class="section-sub">
                    La chronologie apparaîtra après une analyse ou une transaction simulée.
                </div>
            </div>
            """
        )
