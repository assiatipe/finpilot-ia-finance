import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import (
    init_db,
    save_analysis,
    get_user_cash_balance,
    update_cash_balance,
    upsert_portfolio_position,
    add_order,
    get_portfolio_positions,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Analyse IA",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Compatibilité avec la nouvelle navigation horizontale */
    .main .block-container {
        padding-top: 0 !important;
        max-width: 1500px !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if not st.session_state.logged_in:
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.user_id
cash_balance = get_user_cash_balance(user_id)



# ============================================================
# ACHAT RÉEL VIA COURTIER OFFICIEL
# ============================================================

BROKER_LINKS = {
    "Interactive Brokers": "https://www.interactivebrokers.com",
    "Trading 212": "https://www.trading212.com",
    "DEGIRO": "https://www.degiro.fr",
    "eToro": "https://www.etoro.com",
    "Bourse Direct": "https://www.boursedirect.fr",
}

DEFAULT_BROKER = "Interactive Brokers"


def get_real_buy_url(broker_name: str, ticker: str) -> str:
    """
    Retourne le lien officiel du courtier.
    Important : FinPilot ne passe pas l'ordre réel. Il redirige seulement l'utilisateur
    vers un courtier réglementé où il pourra rechercher le ticker et décider lui-même.
    """
    return BROKER_LINKS.get(broker_name, BROKER_LINKS[DEFAULT_BROKER])


def render_real_buy_button(ticker: str, broker_name: str):
    url = get_real_buy_url(broker_name, ticker)
    st.markdown(
        f"""
        <a class="real-buy-button" href="{url}" target="_blank" rel="noopener noreferrer">
            <span class="real-buy-button-icon"></span>
            <span>Acheter réellement {ticker} via {broker_name}</span>
        </a>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {
            --navy: #061633;
            --blue: #2F7CFF;
            --cyan: #23D8F0;
            --green: #24C98B;
            --purple: #7A5CFF;
            --red: #D44D61;
            --text: #10233F;
            --muted: #607088;
            --line: #DCE7F8;
        }

        html, body, .stApp {
            font-family: 'Inter', sans-serif !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 7% 0%, rgba(47,124,255,.13), transparent 28%),
                radial-gradient(circle at 94% 4%, rgba(35,216,240,.16), transparent 26%),
                linear-gradient(135deg, #F8FBFF 0%, #EDF4FF 48%, #F9FFFD 100%) !important;
            color: var(--text) !important;
        }

        header, footer, #MainMenu, [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
        }

        .block-container {
            max-width: 1500px !important;
            padding-top: 0rem !important;
            padding-bottom: 3rem !important;
        }

        [data-testid="stAppViewContainer"] > .main,
        section.main > div,
        div.block-container {
            padding-top: 0 !important;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 30% 12%, rgba(47,124,255,.18), transparent 32%),
                linear-gradient(180deg, #061633 0%, #09224A 52%, #071831 100%) !important;
            box-shadow: 18px 0 58px rgba(7,24,49,.18);
        }

        section[data-testid="stSidebar"] * {
            color: #F5F8FF !important;
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            height: 56px !important;
            border-radius: 14px !important;
            font-weight: 800 !important;
            font-size: .98rem !important;
            border: 1px solid rgba(255,255,255,.09) !important;
            background: rgba(255,255,255,.075) !important;
            color: white !important;
            justify-content: flex-start !important;
            padding-left: 1rem !important;
            box-shadow: none !important;
            transition: .18s ease !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            transform: translateX(2px);
            background: rgba(255,255,255,.115) !important;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #2F7CFF, #7A5CFF) !important;
            box-shadow: 0 16px 32px rgba(47,124,255,.24) !important;
            border: 1px solid rgba(255,255,255,.16) !important;
        }

        .fp-label {
            color: #2F7CFF;
            font-size: 0.84rem;
            font-weight: 900;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.55rem;
        }

        .fp-title {
            font-family: 'Sora', sans-serif;
            font-size: 3.05rem;
            font-weight: 900;
            color: #10233F;
            margin-bottom: 0.45rem;
            line-height: 1.05;
            letter-spacing: -0.055em;
        }

        .fp-subtitle {
            color: #566B88;
            font-size: 1.08rem;
            line-height: 1.75;
            margin-bottom: 1.35rem;
            max-width: 920px;
        }

        .fp-card,
        .fp-soft-card,
        .chart-shell,
        .fp-action-card,
        .help-box,
        .top5-mini-card {
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .fp-card {
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(249,252,255,.94));
            border: 1px solid rgba(220,231,248,.95);
            border-radius: 26px;
            padding: 1.55rem;
            box-shadow: 0 18px 48px rgba(21,54,108,.085), inset 0 1px 0 rgba(255,255,255,.82);
            margin-bottom: 0.3rem;
            position: relative;
            overflow: hidden;
        }

        .fp-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 18px;
            right: 18px;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(47,124,255,.25), transparent);
        }

        .fp-soft-card {
            background:
                radial-gradient(circle at 92% 10%, rgba(47,124,255,.08), transparent 30%),
                linear-gradient(135deg, rgba(255,255,255,.98), rgba(244,248,255,.94));
            border: 1px solid rgba(215,227,248,.95);
            border-radius: 26px;
            padding: 1.55rem;
            box-shadow: 0 18px 48px rgba(21,54,108,.08), inset 0 1px 0 rgba(255,255,255,.85);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }

        .fp-card-title {
            color: #10233F;
            font-size: 1.48rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.35;
            letter-spacing: -0.035em;
        }

        .fp-card-sub {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.75;
            margin-top: 0.45rem;
        }

        .fp-question {
            color: #10233F;
            font-size: 2.18rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.18;
            letter-spacing: -0.055em;
            margin-bottom: 0.75rem;
        }

        .fp-help {
            color: #58708E;
            font-size: 1.04rem;
            line-height: 1.82;
        }

        .fp-progress-wrap {
            height: 12px;
            background: #E6EEF9;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 1rem;
            box-shadow: inset 0 1px 3px rgba(16,35,63,.08);
        }

        .fp-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #2F7CFF, #23D8F0, #24C98B);
            border-radius: 999px;
            box-shadow: 0 0 18px rgba(35,216,240,.35);
        }

        .fp-result-name {
            font-size: 2.5rem;
            font-family: 'Sora', sans-serif;
            font-weight: 900;
            margin: 0.2rem 0 0.5rem 0;
            letter-spacing: -0.055em;
        }

        .fp-pill {
            display: inline-block;
            padding: 0.56rem 0.95rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(47,124,255,.10), rgba(35,216,240,.10));
            border: 1px solid rgba(47,124,255,.18);
            color: #244D84;
            font-size: 0.9rem;
            font-weight: 900;
            margin: 0 0.45rem 0.45rem 0;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.80);
        }

        .fp-green { color: #1C9C73 !important; }
        .fp-red { color: #D44D61 !important; }
        .fp-blue { color: #2F7CFF !important; }

        .fp-badge {
            display: inline-block;
            padding: 0.46rem 0.88rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .fp-badge-green {
            background: #EAFBF4;
            color: #1C9C73;
            border: 1px solid #C5F3E1;
        }

        .fp-badge-red {
            background: #FFECEF;
            color: #D44D61;
            border: 1px solid #F5CCD4;
        }

        .stRadio > label,
        .stMultiSelect > label,
        .stSelectbox > label,
        .stNumberInput > label {
            color: #10233F !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            font-family: 'Sora', sans-serif !important;
        }

        div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 1rem !important;
            margin-top: 0.7rem !important;
            width: 100% !important;
        }

        div[role="radiogroup"] > label {
            position: relative;
            overflow: hidden;
            background: linear-gradient(145deg, #FFFFFF 0%, #F8FBFF 100%) !important;
            border: 1.7px solid #DCE7F8 !important;
            border-radius: 22px !important;
            padding: 1.1rem 1.15rem !important;
            min-height: 94px !important;
            box-shadow: 0 12px 28px rgba(22,46,90,.06), inset 0 1px 0 rgba(255,255,255,.9) !important;
            transition: .18s ease !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }

        div[role="radiogroup"] > label::after {
            content: "";
            position: absolute;
            width: 78px;
            height: 78px;
            border-radius: 50%;
            right: -30px;
            bottom: -34px;
            background: radial-gradient(circle, rgba(47,124,255,.12), transparent 65%);
        }

        div[role="radiogroup"] > label:hover {
            transform: translateY(-2px);
            border-color: #2F7CFF !important;
            box-shadow: 0 18px 34px rgba(47,124,255,.13) !important;
        }

        div[role="radiogroup"] label p {
            color: #18304C !important;
            font-size: 1.06rem !important;
            font-weight: 800 !important;
            line-height: 1.45 !important;
        }

        div[role="radiogroup"] label[data-checked="true"],
        div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg, rgba(47,124,255,.12), rgba(122,92,255,.08)) !important;
            border-color: #2F7CFF !important;
            box-shadow: 0 18px 36px rgba(47,124,255,.16), inset 0 1px 0 rgba(255,255,255,.92) !important;
        }

        div[role="radiogroup"] label[data-checked="true"] p,
        div[role="radiogroup"] > label:has(input:checked) p {
            color: #165BFF !important;
            font-weight: 900 !important;
        }

        .stMultiSelect [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] {
            background: rgba(255,255,255,.98) !important;
            border-radius: 18px !important;
            min-height: 58px !important;
            border: 1px solid #DCE7F8 !important;
            box-shadow: 0 10px 26px rgba(22,46,90,.045);
        }

        .stMultiSelect [data-baseweb="tag"] {
            border-radius: 999px !important;
            background: linear-gradient(90deg, #EAF2FF, #E9FAF7) !important;
            color: #1B4F86 !important;
            font-weight: 800 !important;
        }

        .stButton > button {
            height: 58px !important;
            border-radius: 16px !important;
            font-size: 1.02rem !important;
            font-weight: 900 !important;
            border: 1px solid #DCE7F8 !important;
            box-shadow: 0 12px 26px rgba(22,46,90,.06) !important;
            transition: .18s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2F7CFF, #7A5CFF) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 16px 30px rgba(47,124,255,.22) !important;
        }

        .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #F4F8FF, #EAF2FF) !important;
            color: #204A7A !important;
        }

        .metric-vivid {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            padding: 1.25rem 1.2rem;
            color: white;
            box-shadow: 0 18px 38px rgba(22,46,90,.16);
            min-height: 132px;
            border: 1px solid rgba(255,255,255,.18);
        }

        .metric-vivid::after {
            content: "";
            position: absolute;
            width: 112px;
            height: 112px;
            border-radius: 50%;
            right: -40px;
            bottom: -44px;
            background: rgba(255,255,255,.20);
        }

        .metric-vivid-label {
            position: relative;
            z-index: 2;
            font-size: 0.82rem;
            font-weight: 900;
            opacity: 0.92;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.65rem;
            font-family: 'Sora', sans-serif;
        }

        .metric-vivid-value {
            position: relative;
            z-index: 2;
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.1;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.35rem;
            letter-spacing: -0.04em;
        }

        .metric-vivid-sub {
            position: relative;
            z-index: 2;
            font-size: 0.92rem;
            line-height: 1.55;
            opacity: 0.96;
        }

        .top5-mini-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(145deg, #FFFFFF 0%, #F6FAFF 100%);
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.12rem;
            box-shadow: 0 14px 32px rgba(22,46,90,.07);
            min-height: 178px;
        }

        .top5-mini-card::after {
            content: "";
            position: absolute;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            right: -35px;
            bottom: -35px;
            background: linear-gradient(135deg, rgba(47,124,255,.12), rgba(35,216,240,.12));
        }

        .top5-rank {
            width: 38px;
            height: 38px;
            border-radius: 14px;
            background: linear-gradient(135deg, #2F7CFF, #7A5CFF);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            margin-bottom: 0.85rem;
            font-family: 'Sora', sans-serif;
            box-shadow: 0 10px 20px rgba(47,124,255,.22);
        }

        .top5-name {
            color: #10233F;
            font-size: .98rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.35;
            min-height: 48px;
            position: relative;
            z-index: 2;
        }

        .top5-score {
            color: #2F7CFF;
            font-size: 1.35rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-top: 0.65rem;
            position: relative;
            z-index: 2;
        }

        .chart-shell {
            background:
                radial-gradient(circle at 90% 10%, rgba(47,124,255,.06), transparent 25%),
                linear-gradient(180deg, rgba(255,255,255,.98), rgba(250,252,255,.96));
            border: 1px solid #DCE7F8;
            border-radius: 28px;
            padding: 1.2rem;
            box-shadow: 0 18px 48px rgba(22,46,90,.08), inset 0 1px 0 rgba(255,255,255,.9);
            margin-bottom: 1.3rem;
            overflow: hidden;
        }

        div[data-testid="stPlotlyChart"] {
            border-radius: 22px !important;
            overflow: hidden !important;
            border: 1px solid #EEF3FA !important;
            background: linear-gradient(180deg, #FFFFFF, #FAFCFF) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.95);
        }

        .fp-action-card {
            background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(249,252,255,.96));
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.25rem;
            box-shadow: 0 14px 36px rgba(22,46,90,.07);
            margin-bottom: 0.9rem;
            position: relative;
            overflow: hidden;
        }

        .fp-action-card::after {
            content: "";
            position: absolute;
            width: 92px;
            height: 92px;
            border-radius: 50%;
            right: -35px;
            top: -40px;
            background: linear-gradient(135deg, rgba(47,124,255,.10), rgba(35,216,240,.08));
        }

        .fp-action-title {
            color: #10233F;
            font-size: 1.15rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            letter-spacing: -0.025em;
        }

        .fp-action-text {
            color: #607088;
            font-size: .96rem;
            line-height: 1.75;
            margin-top: 0.45rem;
        }

        .add-portfolio-box {
            background: linear-gradient(135deg, #F8FBFF, #FFFFFF);
            border: 1px solid #DCE7F8;
            border-radius: 18px;
            padding: 1rem;
            margin-top: 0.9rem;
            box-shadow: 0 8px 22px rgba(22,46,90,.05);
        }

        .add-portfolio-title {
            color: #10233F;
            font-size: 1rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.35rem;
        }

        .add-portfolio-text {
            color: #64748B;
            font-size: 0.92rem;
            line-height: 1.55;
            margin-bottom: 0.65rem;
        }

        .price-badge-market,
        .price-badge-estimated {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 900;
        }

        .price-badge-market {
            background: #EAFBF4;
            color: #1C9C73;
            border: 1px solid #C5F3E1;
        }

        .price-badge-estimated {
            background: #FFF7E6;
            color: #A56A00;
            border: 1px solid #F4D49A;
        }

        .order-choice-note {
            color: #64748B;
            font-size: 0.88rem;
            line-height: 1.55;
            margin-top: 0.45rem;
        }

        .fixed-price-box {
            background: linear-gradient(135deg, #F4F8FF, #FFFFFF);
            border: 1px solid #DCE7F8;
            border-radius: 16px;
            padding: 0.85rem 0.95rem;
            min-height: 58px;
            box-shadow: 0 8px 22px rgba(22,46,90,.045);
        }

        .fixed-price-label {
            color: #64748B;
            font-size: 0.78rem;
            font-weight: 900;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: .06em;
        }

        .fixed-price-value {
            color: #10233F;
            font-size: 1.12rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
        }

        .help-box {
            background: linear-gradient(145deg, #FFFFFF, #F8FBFF);
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.15rem;
            box-shadow: 0 14px 32px rgba(22,46,90,.06);
            height: 100%;
        }

        .help-title {
            color: #10233F;
            font-size: 1.06rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: 0.45rem;
        }

        .help-text {
            color: #607088;
            font-size: .94rem;
            line-height: 1.7;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.6rem;
            flex-wrap: wrap;
            border-bottom: 1px solid #DCE7F8;
            padding-bottom: .45rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: white;
            border: 1px solid #DCE7F8;
            border-radius: 14px;
            color: #415875;
            font-weight: 900;
            padding: 0.75rem 1rem;
            font-size: .96rem;
            box-shadow: 0 8px 20px rgba(22,46,90,.04);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #EAF2FF, #F0FFFB) !important;
            color: #2F7CFF !important;
            border-color: #CFE0FF !important;
        }

        [data-testid="stDataFrame"] {
            background: white !important;
            border-radius: 20px !important;
            border: 1px solid #DCE7F8 !important;
            overflow: hidden !important;
            box-shadow: 0 14px 34px rgba(22,46,90,.06);
        }


        .real-buy-card {
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 90% 18%, rgba(36,201,139,.16), transparent 28%),
                linear-gradient(135deg, #FFFFFF 0%, #F4FFF9 100%);
            border: 1px solid rgba(36,201,139,.28);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            margin-top: .9rem;
            box-shadow: 0 12px 30px rgba(36,201,139,.09);
        }

        .real-buy-card::after {
            content: "";
            position: absolute;
            width: 90px;
            height: 90px;
            border-radius: 50%;
            right: -34px;
            bottom: -38px;
            background: linear-gradient(135deg, rgba(36,201,139,.18), rgba(35,216,240,.12));
        }

        .real-buy-title {
            position: relative;
            z-index: 2;
            color: #0F5132;
            font-size: 1.02rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: .35rem;
        }

        .real-buy-text {
            position: relative;
            z-index: 2;
            color: #4B6B5C;
            font-size: .91rem;
            line-height: 1.55;
        }

        .real-buy-warning {
            position: relative;
            z-index: 2;
            margin-top: .65rem;
            padding: .62rem .72rem;
            border-radius: 14px;
            background: rgba(255,255,255,.70);
            border: 1px solid rgba(36,201,139,.16);
            color: #587066;
            font-size: .82rem;
            line-height: 1.45;
            font-weight: 700;
        }

        .real-buy-button {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: .65rem;
            width: 100%;
            min-height: 58px;
            margin-top: .7rem;
            border-radius: 17px;
            text-decoration: none !important;
            background: linear-gradient(135deg, #14B86F 0%, #23D8A7 52%, #2F7CFF 100%);
            color: white !important;
            font-size: 1rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            box-shadow: 0 16px 34px rgba(20,184,111,.22);
            border: 1px solid rgba(255,255,255,.18);
            transition: all .18s ease;
        }

        .real-buy-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 42px rgba(20,184,111,.30);
            filter: brightness(1.03);
        }

        .real-buy-button-icon {
            width: 23px;
            height: 23px;
            border-radius: 9px;
            background: rgba(255,255,255,.22);
            position: relative;
            flex-shrink: 0;
        }

        .real-buy-button-icon::before {
            content: "";
            position: absolute;
            left: 6px;
            top: 6px;
            width: 10px;
            height: 10px;
            border-right: 3px solid white;
            border-top: 3px solid white;
            transform: rotate(45deg);
            border-radius: 1px;
        }

        .real-buy-button-icon::after {
            content: "";
            position: absolute;
            left: 6px;
            top: 10px;
            width: 12px;
            height: 3px;
            border-radius: 99px;
            background: white;
        }

        @media (max-width: 1200px) {
            div[role="radiogroup"] {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            }
            .fp-title {
                font-size: 2.4rem;
            }
        }

        @media (max-width: 800px) {
            div[role="radiogroup"] {
                grid-template-columns: 1fr !important;
            }
        }
    
        .main .block-container {
            padding-top: 0 !important;
        }
        </style>
    """,
    unsafe_allow_html=True,
)




# ============================================================
# TOP PREMIUM BLUE BAR
# ============================================================


# ============================================================
# TOP PREMIUM BLUE BAR
# ============================================================

def render_top_blue_bar(cash_available=None, universe_count=30, sector_count=6):
    if cash_available is None:
        cash_text = "5 100.00 $"
    else:
        try:
            cash_text = f"{float(cash_available):,.2f}".replace(",", " ") + " $"
        except Exception:
            cash_text = "5 100.00 $"

    topbar_html = f"""
<style>
.fp-top-hero {{
    position: relative;
    width: 100%;
    min-height: 205px;
    border-radius: 0 0 30px 30px;
    background:
        radial-gradient(circle at 88% 18%, rgba(122,92,255,0.42), transparent 20%),
        radial-gradient(circle at 74% 72%, rgba(35,216,240,0.13), transparent 20%),
        linear-gradient(100deg, #051633 0%, #0A2D78 48%, #2563EB 100%);
    overflow: hidden;
    box-shadow: 0 20px 55px rgba(8, 25, 70, 0.24);
    padding: 32px 38px 28px 38px;
    margin: 0 0 1.45rem 0;
    border: 1px solid rgba(255,255,255,0.10);
}}

.fp-top-hero::before {{
    content: "";
    position: absolute;
    width: 430px;
    height: 430px;
    border-radius: 50%;
    right: -125px;
    top: -190px;
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: inset 0 0 45px rgba(47,124,255,.13);
    z-index: 0;
    animation: fpHaloPulse 6s ease-in-out infinite;
}}

.fp-top-hero::after {{
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    right: 18px;
    top: -75px;
    border: 1px solid rgba(255,255,255,0.07);
    z-index: 0;
}}

@keyframes fpHaloPulse {{
    0%, 100% {{ transform: scale(1); opacity: .75; }}
    50% {{ transform: scale(1.06); opacity: 1; }}
}}

.fp-top-glow-circle {{
    position: absolute;
    width: 270px;
    height: 270px;
    right: -35px;
    top: -90px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(147,51,234,0.34) 0%, rgba(59,130,246,0.12) 45%, transparent 72%);
    z-index: 1;
}}

.fp-top-grid {{
    position: relative;
    z-index: 3;
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(340px, .75fr);
    gap: 28px;
    align-items: center;
}}

.fp-top-kicker {{
    color: #76F4FF;
    font-size: 0.86rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: .13em;
    margin-bottom: 10px;
    font-family: 'Sora', sans-serif;
}}

.fp-top-title {{
    color: white;
    font-size: 2.35rem;
    font-family: 'Sora', sans-serif;
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -0.055em;
    margin-bottom: 12px;
    max-width: 900px;
}}

.fp-top-text {{
    color: rgba(255,255,255,0.88);
    font-size: 1.02rem;
    line-height: 1.68;
    max-width: 840px;
    margin-bottom: 18px;
    font-weight: 600;
}}

.fp-top-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}}

.fp-top-badge {{
    background: rgba(255,255,255,0.105);
    border: 1px solid rgba(255,255,255,0.16);
    color: #ffffff;
    padding: 10px 14px;
    border-radius: 16px;
    min-width: 132px;
    backdrop-filter: blur(10px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.10);
}}

.fp-top-badge-label {{
    font-size: 0.72rem;
    color: rgba(255,255,255,0.72);
    margin-bottom: 3px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .06em;
}}

.fp-top-badge-value {{
    font-size: 0.95rem;
    font-weight: 900;
    color: #ffffff;
}}

.fp-top-right {{
    position: relative;
    height: 158px;
    min-width: 340px;
}}

.fp-chart-box {{
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 24px;
    background: rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.13);
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 16px 40px rgba(0,0,0,.12);
}}

.fp-grid-lines {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.07) 1px, transparent 1px);
    background-size: 100% 29px, 38px 100%;
    opacity: 0.42;
}}

.fp-bars {{
    position: absolute;
    right: 24px;
    bottom: 18px;
    display: flex;
    align-items: flex-end;
    gap: 10px;
    height: 94px;
}}

.fp-bar {{
    width: 16px;
    border-radius: 10px 10px 0 0;
    background: linear-gradient(180deg, rgba(94,234,212,0.98), rgba(37,99,235,0.18));
    animation: fpBarMove 2.8s ease-in-out infinite alternate;
    box-shadow: 0 0 16px rgba(94,234,212,0.25);
}}

.fp-bar:nth-child(1){{height:30px; animation-delay:0s;}}
.fp-bar:nth-child(2){{height:45px; animation-delay:.2s;}}
.fp-bar:nth-child(3){{height:62px; animation-delay:.4s;}}
.fp-bar:nth-child(4){{height:82px; animation-delay:.6s;}}
.fp-bar:nth-child(5){{height:56px; animation-delay:.8s;}}
.fp-bar:nth-child(6){{height:92px; animation-delay:1s;}}

@keyframes fpBarMove {{
    0% {{transform: scaleY(0.90); opacity:.68;}}
    100% {{transform: scaleY(1.08); opacity:1;}}
}}

.fp-line-wrap {{
    position: absolute;
    inset: 0;
}}

.fp-line-svg {{
    width: 100%;
    height: 100%;
}}

.fp-line-path-bg {{
    fill: none;
    stroke: rgba(103, 232, 249, 0.12);
    stroke-width: 9;
    stroke-linecap: round;
}}

.fp-line-path {{
    fill: none;
    stroke: #67E8F9;
    stroke-width: 3.6;
    stroke-linecap: round;
    filter: drop-shadow(0 0 9px rgba(103,232,249,0.48));
    stroke-dasharray: 520;
    stroke-dashoffset: 520;
    animation: fpDrawLine 4.2s ease-in-out infinite;
}}

@keyframes fpDrawLine {{
    0% {{stroke-dashoffset: 520; opacity:.65;}}
    48% {{stroke-dashoffset: 0; opacity:1;}}
    100% {{stroke-dashoffset: 0; opacity:1;}}
}}

.fp-dot {{
    fill: #A5F3FC;
    filter: drop-shadow(0 0 10px rgba(165,243,252,0.82));
    animation: fpDotPulse 1.8s ease-in-out infinite;
}}

@keyframes fpDotPulse {{
    0%,100% {{r: 4; opacity:.75;}}
    50% {{r: 6.4; opacity:1;}}
}}

.fp-chart-card {{
    position: absolute;
    top: 18px;
    right: 20px;
    background: rgba(10, 20, 70, 0.58);
    border: 1px solid rgba(255,255,255,0.13);
    color: white;
    border-radius: 18px;
    padding: 10px 14px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.16);
}}

.fp-chart-card small {{
    display: block;
    color: rgba(255,255,255,0.72);
    font-size: 0.72rem;
    margin-bottom: 2px;
    font-weight: 700;
}}

.fp-chart-card strong {{
    color: #4ADE80;
    font-size: 1.35rem;
    font-weight: 900;
}}

@media (max-width: 1100px) {{
    .fp-top-grid {{
        grid-template-columns: 1fr;
    }}
    .fp-top-right {{
        min-width: 100%;
    }}
}}
</style>

<div class="fp-top-hero">
    <div class="fp-top-glow-circle"></div>

    <div class="fp-top-grid">
        <div>
            <div class="fp-top-kicker">Analyse investisseur</div>
            <div class="fp-top-title">Profil et recommandations personnalisées</div>
            <div class="fp-top-text">
                Répondez au questionnaire, choisissez vos secteurs préférés et obtenez
                une sélection d’actifs expliquée avec score MCDA, rendement, volatilité,
                bêta et ratio de Sharpe.
            </div>

            <div class="fp-top-badges">
                <div class="fp-top-badge">
                    <div class="fp-top-badge-label">Cash disponible</div>
                    <div class="fp-top-badge-value">{cash_text}</div>
                </div>
                <div class="fp-top-badge">
                    <div class="fp-top-badge-label">Univers</div>
                    <div class="fp-top-badge-value">{universe_count} actifs</div>
                </div>
                <div class="fp-top-badge">
                    <div class="fp-top-badge-label">Secteurs</div>
                    <div class="fp-top-badge-value">{sector_count}</div>
                </div>
                <div class="fp-top-badge">
                    <div class="fp-top-badge-label">Top 5 généré</div>
                    <div class="fp-top-badge-value">Automatiquement</div>
                </div>
            </div>
        </div>

        <div class="fp-top-right">
            <div class="fp-chart-box">
                <div class="fp-grid-lines"></div>

                <div class="fp-line-wrap">
                    <svg class="fp-line-svg" viewBox="0 0 360 150" preserveAspectRatio="none">
                        <path class="fp-line-path-bg"
                              d="M8,112 C35,102 45,55 76,66 C104,77 118,118 145,98 C170,79 187,38 218,47 C245,56 266,18 352,26" />
                        <path class="fp-line-path"
                              d="M8,112 C35,102 45,55 76,66 C104,77 118,118 145,98 C170,79 187,38 218,47 C245,56 266,18 352,26" />
                        <circle class="fp-dot" cx="352" cy="26" r="4"></circle>
                    </svg>
                </div>

                <div class="fp-bars">
                    <div class="fp-bar"></div>
                    <div class="fp-bar"></div>
                    <div class="fp-bar"></div>
                    <div class="fp-bar"></div>
                    <div class="fp-bar"></div>
                    <div class="fp-bar"></div>
                </div>

                <div class="fp-chart-card">
                    <small>Portefeuille simulé</small>
                    <strong>+12.4%</strong>
                </div>
            </div>
        </div>
    </div>
</div>
"""

    # Important : on supprime l'indentation ligne par ligne pour éviter que Markdown
    # transforme le HTML en bloc de code.
    topbar_html = "\n".join(line.strip() for line in topbar_html.strip().splitlines())
    st.markdown(topbar_html, unsafe_allow_html=True)


# ============================================================
# QUESTIONNAIRE DATA
# ============================================================

QUESTIONS = [
    {
        "key": "experience",
        "title": "Quel est votre niveau d’expérience en investissement ?",
        "help": "On adapte les recommandations à votre niveau et à votre capacité de compréhension des marchés.",
        "options": [
            ("Débutant", 1),
            ("Quelques notions", 2),
            ("Déjà investi", 3),
            ("Investisseur régulier", 4),
            ("Très à l’aise", 5),
        ],
    },
    {
        "key": "objectif",
        "title": "Quel est votre objectif principal ?",
        "help": "Cette question permet d’orienter entre sécurité, équilibre et croissance.",
        "options": [
            ("Préserver mon capital", 1),
            ("Faire progresser mon épargne prudemment", 2),
            ("Construire un portefeuille équilibré", 3),
            ("Chercher une croissance importante", 4),
            ("Maximiser la performance", 5),
        ],
    },
    {
        "key": "horizon",
        "title": "Quel est votre horizon d’investissement ?",
        "help": "Plus l’horizon est long, plus on peut supporter les fluctuations.",
        "options": [
            ("Moins de 1 an", 1),
            ("1 à 3 ans", 2),
            ("3 à 5 ans", 3),
            ("5 à 10 ans", 4),
            ("Plus de 10 ans", 5),
        ],
    },
    {
        "key": "perte",
        "title": "Quelle baisse temporaire pouvez-vous accepter ?",
        "help": "Cela mesure directement votre tolérance au risque.",
        "options": [
            ("Presque aucune perte", 1),
            ("Moins de 5 %", 2),
            ("5 % à 15 %", 3),
            ("15 % à 30 %", 4),
            ("Plus de 30 %", 5),
        ],
    },
    {
        "key": "reaction",
        "title": "Si votre portefeuille baisse fortement, que faites-vous ?",
        "help": "Votre réaction face aux pertes est un bon indicateur de profil.",
        "options": [
            ("Je vends rapidement", 1),
            ("Je réduis mes positions", 2),
            ("J’attends", 3),
            ("Je garde ma stratégie", 4),
            ("J’achète davantage", 5),
        ],
    },
    {
        "key": "revenu",
        "title": "Vos revenus sont-ils stables ?",
        "help": "Des revenus plus stables permettent généralement d’investir plus sereinement.",
        "options": [
            ("Très instables", 1),
            ("Plutôt irréguliers", 2),
            ("Moyennement stables", 3),
            ("Stables", 4),
            ("Très stables", 5),
        ],
    },
    {
        "key": "epargne",
        "title": "Quelle part de votre épargne voulez-vous investir ?",
        "help": "On évite d’exposer une part trop importante de votre épargne si votre profil est prudent.",
        "options": [
            ("Moins de 10 %", 1),
            ("10 % à 25 %", 2),
            ("25 % à 40 %", 3),
            ("40 % à 60 %", 4),
            ("Plus de 60 %", 5),
        ],
    },
    {
        "key": "liquidite",
        "title": "Avez-vous besoin de récupérer rapidement votre argent ?",
        "help": "Le besoin de liquidité pousse souvent vers des choix plus prudents.",
        "options": [
            ("Oui, à tout moment", 1),
            ("Dans moins d’un an", 2),
            ("Dans 1 à 3 ans", 3),
            ("Pas avant plusieurs années", 4),
            ("Non, long terme", 5),
        ],
    },
    {
        "key": "connaissance",
        "title": "Quels produits comprenez-vous le mieux ?",
        "help": "Cette question aide à éviter des actifs trop complexes pour votre niveau actuel.",
        "options": [
            ("Épargne simple", 1),
            ("Actions simples", 2),
            ("Actions et ETF", 3),
            ("Actions, ETF et ratios", 4),
            ("Produits plus complexes", 5),
        ],
    },
    {
        "key": "diversification",
        "title": "Quelle importance donnez-vous à la diversification ?",
        "help": "La diversification réduit le risque lié à un seul actif ou à un seul secteur.",
        "options": [
            ("Faible", 1),
            ("Plutôt faible", 2),
            ("Moyenne", 3),
            ("Importante", 4),
            ("Très importante", 5),
        ],
    },
    {
        "key": "style",
        "title": "Quel style d’investissement vous attire ?",
        "help": "Votre préférence générale nous aide à construire une recommandation cohérente.",
        "options": [
            ("Défensif", 1),
            ("Dividendes", 2),
            ("Équilibré", 3),
            ("Croissance", 4),
            ("Innovation et technologie", 5),
        ],
    },
    {
        "key": "secteurs",
        "title": "Quels secteurs vous intéressent ?",
        "help": "Vous pouvez sélectionner plusieurs secteurs afin d’affiner la recommandation finale.",
        "type": "sectors",
        "options": [
            "Technologie",
            "Santé",
            "Finance",
            "Industrie",
            "Énergie",
            "Consommation de base",
            "Consommation discrétionnaire",
            "Télécommunications",
            "Matériaux",
            "ETF diversifiés",
        ],
    },
]


# ============================================================
# SESSION STATE
# ============================================================

if "question_step" not in st.session_state:
    st.session_state.question_step = 0

if "investor_answers" not in st.session_state:
    st.session_state.investor_answers = {}

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "show_mcda" not in st.session_state:
    st.session_state.show_mcda = False

if "show_indicator_help" not in st.session_state:
    st.session_state.show_indicator_help = False

if "last_saved_analysis_signature" not in st.session_state:
    st.session_state.last_saved_analysis_signature = None


# ============================================================
# FUNCTIONS
# ============================================================

@st.cache_data(show_spinner=False, ttl=3600)
def load_mcda_analysis(profile: str):
    from data_loader import charger_donnees
    from indicators import calculer_indicateurs
    from scoring import calculer_score
    from config import NOMS, SECTEURS
    from explanations import generer_justification

    df_prix, df_indice, rf_annuel, rapport = charger_donnees()
    df_indicateurs = calculer_indicateurs(df_prix, df_indice, rf_annuel)
    df_scores = calculer_score(df_indicateurs, profile)

    df_scores["nom"] = df_scores.index.map(NOMS)
    df_scores["secteur"] = df_scores.index.map(SECTEURS)

    top5 = df_scores.head(5).copy()

    justifications = {}
    for ticker, row in top5.iterrows():
        justifications[ticker] = generer_justification(ticker, row, profile)

    return df_prix, df_indicateurs, df_scores, top5, justifications, rapport, rf_annuel


def classify_profile(score: int):
    if score <= 24:
        return "Prudent", "#1C9C73", "Priorité à la stabilité et à la protection du capital."
    if score <= 42:
        return "Modéré", "#2F7CFF", "Équilibre entre rendement potentiel et maîtrise du risque."
    return "Dynamique", "#A56A00", "Recherche de croissance avec une tolérance au risque plus élevée."


def make_top5_score_chart(top5):
    df_plot = top5.sort_values("score", ascending=True)

    fig = go.Figure()
    
    # 1. La barre fine (Lollipop stick)
    fig.add_trace(
        go.Bar(
            x=df_plot["score"],
            y=[f"{idx} - {row['nom']}" for idx, row in df_plot.iterrows()],
            orientation="h",
            width=0.06,
            marker=dict(color="#E2E8F0"),
            hoverinfo="skip",
            showlegend=False
        )
    )
    
    # 2. Le point lumineux (Lollipop candy)
    fig.add_trace(
        go.Scatter(
            x=df_plot["score"],
            y=[f"{idx} - {row['nom']}" for idx, row in df_plot.iterrows()],
            mode="markers",
            marker=dict(
                size=26,
                color=df_plot["score"],
                colorscale="Blues",
                line=dict(color="white", width=4),
            ),
            hovertemplate="<b>%{y}</b><br>Score : %{x:.2f}/100<extra></extra>",
            showlegend=False
        )
    )

    fig.update_layout(
        title=dict(
            text="Top 5 des actions recommandées",
            font=dict(size=22, color="#0F172A", family="Outfit"),
            x=0.03,
        ),
        height=500,
        margin=dict(l=40, r=40, t=85, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", size=14, family="Inter"),
        xaxis=dict(
            range=[0, 100],
            gridcolor="rgba(226, 232, 240, 0.5)",
            zeroline=False,
            title=dict(
                text="Score MCDA Global",
                font=dict(color="#64748B", size=12)
            ),
            tickfont=dict(color="#64748B"),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=14)),
        showlegend=False,
        bargap=0.4,
    )

    return fig


def make_financial_radar_chart(top5):
    categories = ["Rendement", "Volatilité maîtrisée", "Bêta maîtrisé", "Sharpe"]
    # Couleurs avec rgba pour bordure et fond transparent (glow)
    colors = [
        ("rgba(47, 124, 255, 1)", "rgba(47, 124, 255, 0.15)"),
        ("rgba(28, 156, 115, 1)", "rgba(28, 156, 115, 0.15)"),
        ("rgba(122, 92, 255, 1)", "rgba(122, 92, 255, 0.15)"),
        ("rgba(243, 201, 105, 1)", "rgba(243, 201, 105, 0.15)"),
        ("rgba(212, 77, 97, 1)", "rgba(212, 77, 97, 0.15)")
    ]

    fig = go.Figure()

    for i, (ticker, row) in enumerate(top5.iterrows()):
        values = [
            row["rendement_norm"],
            row["sigma_norm"],
            row["beta_norm"],
            row["sharpe_norm"],
        ]
        values = values + [values[0]]
        cats = categories + [categories[0]]
        
        solid_color, fill_color = colors[i % len(colors)]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=cats,
                fill="toself",
                fillcolor=fill_color,
                name=f"{row['nom']} ({ticker})",
                line=dict(color=solid_color, width=3, shape="spline"),
                marker=dict(size=8, color=solid_color, line=dict(color="white", width=2)),
                hovertemplate="<b>%{theta}</b>: %{r:.2f}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(
            text="Radar comparatif du Top 5",
            font=dict(size=22, color="#0F172A", family="Outfit"),
            x=0.03,
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False,
                showline=False,
                gridcolor="rgba(226, 232, 240, 0.6)",
            ),
            angularaxis=dict(
                gridcolor="rgba(226, 232, 240, 0.6)",
                linecolor="rgba(0,0,0,0)",
                tickfont=dict(size=14, color="#334155", family="Inter"),
            )
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=600,
        margin=dict(l=10, r=10, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter", size=13, color="#334155"),
        ),
    )

    return fig


def format_percent(x):
    return f"{x * 100:.2f}%"




@st.cache_data(show_spinner=False, ttl=900)
def get_latest_price_for_buy(ticker):
    """
    Récupère le dernier prix de marché avec yfinance.
    Si le prix n'est pas disponible, retourne None.
    """
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


def get_position_quantity(user_id, ticker):
    """
    Retourne la quantité détenue pour un ticker.
    """
    ticker = str(ticker).upper().strip()

    try:
        positions = get_portfolio_positions(user_id)
    except Exception:
        positions = []

    for pos_ticker, _, qty, _ in positions:
        if str(pos_ticker).upper().strip() == ticker:
            return float(qty)

    return 0.0


def execute_recommendation_order(user_id, ticker, company_name, order_type, quantity, price):
    """
    Exécute un ordre depuis une recommandation IA.
    - Achat : bloque si cash insuffisant.
    - Vente : bloque si la position n'existe pas ou si la quantité est insuffisante.
    """
    ticker = str(ticker).upper().strip()
    company_name = company_name or ticker
    order_type = str(order_type).upper().strip()

    cash_balance = get_user_cash_balance(user_id)
    total = quantity * price

    if total <= 0:
        return False, "Montant invalide."

    if order_type == "BUY":
        if total > cash_balance:
            return False, f"Cash insuffisant. Solde disponible : ${cash_balance:,.2f}"

        new_cash = cash_balance - total

        update_cash_balance(user_id, new_cash)
        upsert_portfolio_position(user_id, ticker, company_name, quantity, price)
        add_order(user_id, ticker, "BUY", quantity, price, total, new_cash)

        return True, f"Achat enregistré : {quantity:.2f} action(s) {ticker}."

    if order_type == "SELL":
        owned_qty = get_position_quantity(user_id, ticker)

        if owned_qty <= 0:
            return False, f"Vente impossible : vous ne détenez aucune position {ticker}."

        if quantity > owned_qty:
            return False, f"Vente impossible : vous détenez seulement {owned_qty:.2f} action(s) {ticker}."

        new_cash = cash_balance + total

        update_cash_balance(user_id, new_cash)
        upsert_portfolio_position(user_id, ticker, company_name, -quantity, price)
        add_order(user_id, ticker, "SELL", quantity, price, total, new_cash)

        return True, f"Vente enregistrée : {quantity:.2f} action(s) {ticker}."

    return False, "Type d’ordre invalide."


def indicator_status(row):
    rendement_ok = row["rendement_annuel"] > 0
    vol_ok = row["volatilite_annuelle"] < 0.30
    beta_ok = row["beta"] < 1.10
    sharpe_ok = row["sharpe"] > 0
    return rendement_ok, vol_ok, beta_ok, sharpe_ok


def reset_analysis():
    st.session_state.question_step = 0
    st.session_state.investor_answers = {}
    st.session_state.analysis_done = False
    st.session_state.show_mcda = False
    st.session_state.show_indicator_help = False
    st.session_state.last_saved_analysis_signature = None

    for key in list(st.session_state.keys()):
        if key.startswith("answer_"):
            del st.session_state[key]


# ============================================================
# SIDEBAR PREMIUM COMMUNE
# ============================================================

render_sidebar(
    active_page="analyse",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# HEADER
# ============================================================


# Barre premium bleu sombre en haut
try:
    render_top_blue_bar(
        cash_available=cash_balance,
        universe_count=len(actions_df) if "actions_df" in globals() else 30,
        sector_count=len(sectors) if "sectors" in globals() else 6,
    )
except Exception:
    render_top_blue_bar(cash_available=cash_balance)

st.markdown(
    """
    <div class="fp-label">Analyse investisseur</div>
    <div class="fp-title">Profil et recommandations</div>
    <div class="fp-subtitle">
        Répondez au questionnaire, puis lancez l’analyse financière pour afficher le Top 5 et les graphes comparatifs.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# QUESTIONNAIRE
# ============================================================

if not st.session_state.analysis_done:
    total_questions = len(QUESTIONS)
    step = st.session_state.question_step
    current_question = QUESTIONS[step]
    progress_pct = int(((step + 1) / total_questions) * 100)

    left_top, right_top = st.columns([2.2, 1], gap="large")

    with left_top:
        st.markdown(
            f"""
            <div class="fp-soft-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div class="fp-label">Questionnaire investisseur</div>
                        <div class="fp-card-title">Question {step + 1} sur {total_questions}</div>
                    </div>
                    <div style="font-size:1.35rem;font-weight:900;color:#2F7CFF;font-family:'Sora',sans-serif;">
                        {progress_pct}%
                    </div>
                </div>
                <div class="fp-progress-wrap">
                    <div class="fp-progress-bar" style="width:{progress_pct}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_top:
        st.markdown(
            """
            <div class="fp-soft-card" style="background:linear-gradient(135deg,#EAF2FF,#F8FBFF);">
                <div style="display:flex;align-items:flex-start;gap:.85rem;">
                    <div style="flex-shrink:0;width:42px;height:42px;border-radius:12px;background:#EEF4FF;border:1px solid #DBEAFE;display:flex;align-items:center;justify-content:center;">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="11" cy="11" r="9" stroke="#3B82F6" stroke-width="1.8"/>
                            <circle cx="11" cy="11" r="4.5" stroke="#3B82F6" stroke-width="1.8"/>
                            <circle cx="11" cy="11" r="1.5" fill="#3B82F6"/>
                            <line x1="11" y1="2" x2="11" y2="4.5" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round"/>
                            <line x1="11" y1="17.5" x2="11" y2="20" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round"/>
                            <line x1="2" y1="11" x2="4.5" y2="11" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round"/>
                            <line x1="17.5" y1="11" x2="20" y2="11" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div>
                        <div class="fp-card-title" style="font-size:1.05rem;">Objectif</div>
                        <div class="fp-card-sub" style="margin-top:.25rem;">
                            Construire un profil investisseur vraiment exploitable et simple à comprendre.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    qcol, infocol = st.columns([2.2, 1], gap="large")

    with qcol:
        st.markdown(
            f"""
            <div class="fp-card" style="background:linear-gradient(135deg,#FFFFFF,#F7FBFF);">
                <div class="fp-question">{current_question["title"]}</div>
                <div class="fp-help">{current_question["help"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with infocol:
        st.markdown(
            """
            <div class="fp-soft-card">
                <div style="display:flex;align-items:flex-start;gap:.85rem;">
                    <div style="flex-shrink:0;width:42px;height:42px;border-radius:12px;background:#EEF4FF;border:1px solid #DBEAFE;display:flex;align-items:center;justify-content:center;">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="11" cy="8" r="3.5" stroke="#3B82F6" stroke-width="1.8"/>
                            <path d="M5 19c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div>
                        <div class="fp-card-title" style="font-size:1.05rem;">Pourquoi cette question ?</div>
                        <div class="fp-card-sub" style="margin-top:.25rem;">
                            Elle permet à FinPilot d'adapter le niveau de risque, le type d'actifs et la logique de recommandation à votre situation réelle.
                        </div>
                    </div>
                </div>
            </div>
            <div class="fp-soft-card" style="background:linear-gradient(135deg,#F7FBFF,#EDF6FF);">
                <div style="display:flex;align-items:flex-start;gap:.85rem;">
                    <div style="flex-shrink:0;width:42px;height:42px;border-radius:12px;background:#EEF4FF;border:1px solid #DBEAFE;display:flex;align-items:center;justify-content:center;">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="3" y="3" width="16" height="16" rx="3" stroke="#3B82F6" stroke-width="1.8"/>
                            <path d="M7 11.5L10 14.5L15 8.5" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div>
                        <div class="fp-card-title" style="font-size:1.05rem;">Résultat attendu</div>
                        <div class="fp-card-sub" style="margin-top:.25rem;">
                            À la fin, vous obtenez un profil clair, des secteurs choisis et des recommandations d'actions adaptées.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    answer_key = f"answer_{current_question['key']}"

    if current_question.get("type") == "sectors":
        selected_answer = st.multiselect(
            "Sélectionnez les secteurs qui vous intéressent",
            options=current_question["options"],
            default=st.session_state.investor_answers.get(current_question["key"], []),
            key=answer_key,
        )
    else:
        labels = [opt[0] for opt in current_question["options"]]
        previous = st.session_state.investor_answers.get(current_question["key"])
        index = labels.index(previous) if previous in labels else 0

        selected_answer = st.radio(
            "Votre réponse",
            options=labels,
            index=index,
            key=answer_key,
            label_visibility="collapsed",
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Précédent", use_container_width=True, disabled=step == 0, key="step_prev"):
            st.session_state.investor_answers[current_question["key"]] = selected_answer
            st.session_state.question_step -= 1
            st.rerun()

    with c2:
        if st.button("Recommencer", use_container_width=True, key="step_reset"):
            reset_analysis()
            st.rerun()

    with c3:
        if step < total_questions - 1:
            if st.button("Suivant", use_container_width=True, type="primary", key="step_next"):
                st.session_state.investor_answers[current_question["key"]] = selected_answer
                st.session_state.question_step += 1
                st.rerun()
        else:
            if st.button("Afficher mon profil", use_container_width=True, type="primary", key="step_show_profil"):
                st.session_state.investor_answers[current_question["key"]] = selected_answer

                score = 0
                for q in QUESTIONS:
                    if q.get("type") == "sectors":
                        continue
                    answer = st.session_state.investor_answers.get(q["key"])
                    for label, value in q["options"]:
                        if answer == label:
                            score += value
                            break

                profile, color, description = classify_profile(score)
                selected_sectors = st.session_state.investor_answers.get("secteurs", [])

                # Important :
                # On ne sauvegarde pas encore l'analyse ici, car le Top 5 n'est pas encore calculé.
                # La sauvegarde complète se fait après le calcul MCDA pour éviter :
                # - NameError: recommendations is not defined
                # - "Aucune recommandation enregistrée" dans l'historique.

                st.session_state.analysis_done = True
                st.session_state.last_profile = profile
                st.session_state.last_color = color
                st.session_state.last_score = score
                st.session_state.last_description = description
                st.session_state.last_sectors = selected_sectors
                st.rerun()


# ============================================================
# RESULTAT PROFIL
# ============================================================

if st.session_state.analysis_done:
    profile = st.session_state.last_profile
    color = st.session_state.last_color
    score = st.session_state.last_score
    description = st.session_state.last_description
    selected_sectors = st.session_state.last_sectors

    st.markdown(
        f"""
        <div class="fp-card" style="border-left:6px solid {color}; background:linear-gradient(135deg,#FFFFFF,#F8FBFF);">
            <div class="fp-label">Profil détecté</div>
            <div class="fp-result-name" style="color:{color};">{profile}</div>
            <div class="fp-card-sub">{description}</div>
            <div class="fp-card-sub"><b>Score :</b> {score}/55</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected_sectors:
        pills = "".join([f'<span class="fp-pill">{s}</span>' for s in selected_sectors])
        st.markdown(
            f"""
            <div class="fp-card">
                <div class="fp-card-title">Secteurs sélectionnés</div>
                <div style="margin-top:0.8rem;">{pills}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    b1, b2 = st.columns(2)

    with b1:
        if st.button("Calculer les recommandations financières", use_container_width=True, type="primary", key="calc_reco"):
            st.session_state.show_mcda = True
            st.rerun()

    with b2:
        if st.button("Recommencer le questionnaire", use_container_width=True, key="reset_questionnaire"):
            reset_analysis()
            st.rerun()


# ============================================================
# RESULTAT MCDA
# ============================================================

if st.session_state.analysis_done and st.session_state.show_mcda:
    with st.spinner("Calcul des indicateurs financiers en cours..."):
        try:
            df_prix, df_indicateurs, df_scores, top5, justifications, rapport, rf_annuel = load_mcda_analysis(profile)
        except Exception as e:
            st.error(f"Erreur lors du calcul : {e}")
            st.stop()

    # ========================================================
    # SAUVEGARDE DE L'ANALYSE AVEC LES RECOMMANDATIONS
    # ========================================================
    # Le Top 5 est maintenant disponible. On peut donc enregistrer
    # l'analyse complète dans l'historique.
    recommendations_text = ", ".join([str(ticker) for ticker in top5.index.tolist()])
    selected_sectors_text = ", ".join(selected_sectors) if selected_sectors else "Aucune préférence"
    analysis_notes = (
        f"Score: {score}/55 | "
        f"Secteurs: {selected_sectors_text} | "
        f"Top 5: {recommendations_text}"
    )

    current_signature = f"{user_id}|{profile}|{score}|{recommendations_text}|{selected_sectors_text}"

    if st.session_state.last_saved_analysis_signature != current_signature:
        try:
            save_analysis(
                user_id,
                profile,
                score,
                recommendations_text,
                analysis_notes,
            )
            st.session_state.last_saved_analysis_signature = current_signature
        except Exception as e:
            st.warning(f"Analyse calculée, mais sauvegarde dans l'historique impossible : {e}")

    st.markdown(
        """
        <div class="fp-card" style="padding-bottom:1.2rem; background:linear-gradient(135deg,#FFFFFF,#F6FAFF);">
            <div class="fp-card-title" style="font-size:1.75rem;">Résultat du calcul financier</div>
            <div class="fp-card-sub" style="font-size:1.12rem;">
                Voici un résumé clair des paramètres utilisés dans l’analyse.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3, gap="medium")

    with m1:
        st.markdown(
            f"""
            <div class="metric-vivid" style="background:linear-gradient(135deg,#19B87B,#14A06A);">
                <div class="metric-vivid-label">Profil utilisé</div>
                <div class="metric-vivid-value">{profile}</div>
                <div class="metric-vivid-sub">Profil détecté après le questionnaire investisseur.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-vivid" style="background:linear-gradient(135deg,#2F7CFF,#56A7FF);">
                <div class="metric-vivid-label">Taux sans risque</div>
                <div class="metric-vivid-value">{rf_annuel * 100:.2f}%</div>
                <div class="metric-vivid-sub">Utilisé dans le calcul du ratio de Sharpe.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-vivid" style="background:linear-gradient(135deg,#7A5CFF,#9F82FF);">
                <div class="metric-vivid-label">Actions retenues</div>
                <div class="metric-vivid-value">{len(df_scores)}</div>
                <div class="metric-vivid-sub">Nombre total d’actions conservées après nettoyage des données.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    tab_top5, tab_radar, tab_table, tab_help = st.tabs(
        ["Top 5", "Radar comparatif", "Tableau financier", "Aide à la lecture"]
    )

    with tab_top5:
        st.markdown(
            """
            <div class="fp-card" style="background:linear-gradient(135deg,#FFFFFF,#F7FBFF);">
                <div class="fp-card-title">Classement des 5 meilleures actions</div>
                <div class="fp-card-sub">
                    Ces actions sont classées selon le score MCDA calculé à partir du rendement,
                    de la volatilité, du bêta et du ratio de Sharpe.
                    Vous pouvez ensuite passer un ordre d’achat ou de vente depuis une recommandation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        top_cols = st.columns(5, gap="medium")

        for i, ((ticker, row), col) in enumerate(zip(top5.iterrows(), top_cols), start=1):
            with col:
                st.markdown(
                    f"""
                    <div class="top5-mini-card">
                        <div class="top5-rank">{i}</div>
                        <div class="top5-name">
                            {row["nom"]}<br>
                            <span style="color:#64748B;font-size:0.9rem;">{ticker}</span>
                        </div>
                        <div class="top5-score">{row["score"]:.1f}</div>
                        <div style="color:#64748B;font-size:0.9rem;margin-top:0.25rem;">Score MCDA</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.plotly_chart(
            make_top5_score_chart(top5),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="fp-card" style="background:linear-gradient(135deg,#FFFFFF,#F8FBFF);">
                <div class="fp-card-title">Lecture rapide des actions</div>
                <div class="fp-card-sub">
                    Les indicateurs en vert sont favorables. Les indicateurs en rouge signalent un point de risque à surveiller.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for ticker, row in top5.iterrows():
            rendement_ok, vol_ok, beta_ok, sharpe_ok = indicator_status(row)

            risk_label = "Profil favorable"
            badge_class = "fp-badge-green"

            if not vol_ok or not beta_ok:
                risk_label = "Risque à surveiller"
                badge_class = "fp-badge-red"

            latest_price = get_latest_price_for_buy(ticker)

            if latest_price is not None and latest_price > 0:
                buy_price = latest_price
                price_badge = '<span class="price-badge-market">Prix marché</span>'
            else:
                buy_price = 100.0
                price_badge = '<span class="price-badge-estimated">Prix estimé à modifier</span>'

            st.markdown(
                f"""
                <div class="fp-action-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;">
                        <div class="fp-action-title">{row["nom"]} ({ticker})</div>
                        <div class="fp-badge {badge_class}">{risk_label}</div>
                    </div>
                    <div class="fp-action-text">
                        Score MCDA : <b>{row["score"]:.2f}/100</b> ·
                        Rendement : <span class="{'fp-green' if rendement_ok else 'fp-red'}">{format_percent(row["rendement_annuel"])}</span> ·
                        Volatilité : <span class="{'fp-green' if vol_ok else 'fp-red'}">{format_percent(row["volatilite_annuelle"])}</span> ·
                        Bêta : <span class="{'fp-green' if beta_ok else 'fp-red'}">{row["beta"]:.2f}</span> ·
                        Sharpe : <span class="{'fp-green' if sharpe_ok else 'fp-red'}">{row["sharpe"]:.2f}</span>
                    </div>
                    <div class="add-portfolio-box">
                        <div class="add-portfolio-title">Passer un ordre depuis cette recommandation</div>
                        <div class="add-portfolio-text">
                            Prix utilisé : <b>${buy_price:,.2f}</b> &nbsp; {price_badge}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            type_col, q_col, price_col, b_col = st.columns([1, 1, 1, 1.25], gap="medium")

            with type_col:
                order_label = st.selectbox(
                    f"Type {ticker}",
                    options=["Achat", "Vente"],
                    key=f"order_type_{ticker}",
                )

            with q_col:
                quantity_to_trade = st.number_input(
                    f"Quantité {ticker}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qty_trade_{ticker}",
                )

            with price_col:
                st.markdown(
                    f"""
                    <div class="fixed-price-box">
                        <div class="fixed-price-label">Prix utilisé</div>
                        <div class="fixed-price-value">${buy_price:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with b_col:
                st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)

                order_type = "BUY" if order_label == "Achat" else "SELL"
                button_label = f"{order_label} {ticker}"

                if st.button(
                    button_label,
                    key=f"execute_order_{ticker}",
                    use_container_width=True,
                    type="primary",
                ):
                    ok, msg = execute_recommendation_order(
                        user_id=user_id,
                        ticker=ticker,
                        company_name=row["nom"],
                        order_type=order_type,
                        quantity=float(quantity_to_trade),
                        price=float(buy_price),
                    )

                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            if order_label == "Achat":
                st.markdown(
                    f"""
                    <div class="real-buy-card">
                        <div class="real-buy-title">Achat réel via un courtier officiel</div>
                        <div class="real-buy-text">
                            Vous pouvez aussi ouvrir une plateforme de courtage réglementée pour acheter réellement
                            <b>{ticker}</b>. FinPilot ne transmet aucun ordre réel : l’achat final se fait uniquement
                            sur le site du courtier choisi.
                        </div>
                        <div class="real-buy-warning">
                            Vérifiez toujours les frais, les risques, la disponibilité de l’action et les conditions
                            du courtier avant toute décision réelle.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                broker_col, real_buy_col = st.columns([1, 1.35], gap="medium")

                with broker_col:
                    selected_broker = st.selectbox(
                        f"Courtier pour {ticker}",
                        list(BROKER_LINKS.keys()),
                        key=f"real_broker_{ticker}",
                    )

                with real_buy_col:
                    st.markdown("<div style='height:1.78rem;'></div>", unsafe_allow_html=True)
                    render_real_buy_button(ticker, selected_broker)

            else:
                st.markdown(
                    """
                    <div class="order-choice-note">
                        La vente réelle doit être effectuée depuis votre propre courtier, uniquement si vous détenez
                        déjà l’action dans votre portefeuille réel.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div class="order-choice-note">
                    Le prix est récupéré automatiquement. Pour modifier manuellement un prix,
                    utilisez la page Portefeuille dans la simulation d’ordre.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    with tab_radar:
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.plotly_chart(make_financial_radar_chart(top5), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_table:
        table = top5[
            [
                "nom",
                "secteur",
                "rendement_annuel",
                "volatilite_annuelle",
                "beta",
                "sharpe",
                "score",
                "rang",
            ]
        ].copy()

        table = table.rename(
            columns={
                "nom": "Entreprise",
                "secteur": "Secteur",
                "rendement_annuel": "Rendement annuel",
                "volatilite_annuelle": "Volatilité annuelle",
                "beta": "Bêta",
                "sharpe": "Sharpe",
                "score": "Score MCDA",
                "rang": "Rang",
            }
        )

        table["Rendement annuel"] = table["Rendement annuel"].apply(format_percent)
        table["Volatilité annuelle"] = table["Volatilité annuelle"].apply(format_percent)
        table["Bêta"] = table["Bêta"].apply(lambda x: f"{x:.2f}")
        table["Sharpe"] = table["Sharpe"].apply(lambda x: f"{x:.2f}")
        table["Score MCDA"] = table["Score MCDA"].apply(lambda x: f"{x:.2f}/100")

        st.dataframe(table, use_container_width=True)

    with tab_help:
        if st.button("Afficher / masquer l'aide de lecture", use_container_width=True, key="toggle_aide"):
            st.session_state.show_indicator_help = not st.session_state.show_indicator_help

        if st.session_state.show_indicator_help:
            h1, h2, h3, h4 = st.columns(4, gap="medium")

            with h1:
                st.markdown(
                    """
                    <div class="help-box">
                        <div class="help-title">Rendement</div>
                        <div class="help-text">
                            <span class="fp-green"><b>Vert</b></span> : performance positive.<br>
                            <span class="fp-red"><b>Rouge</b></span> : performance faible ou négative.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with h2:
                st.markdown(
                    """
                    <div class="help-box">
                        <div class="help-title">Volatilité</div>
                        <div class="help-text">
                            <span class="fp-green"><b>Vert</b></span> : variations maîtrisées.<br>
                            <span class="fp-red"><b>Rouge</b></span> : action plus risquée.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with h3:
                st.markdown(
                    """
                    <div class="help-box">
                        <div class="help-title">Bêta</div>
                        <div class="help-text">
                            <span class="fp-green"><b>Vert</b></span> : sensibilité modérée au marché.<br>
                            <span class="fp-red"><b>Rouge</b></span> : forte réaction au marché.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with h4:
                st.markdown(
                    """
                    <div class="help-box">
                        <div class="help-title">Sharpe</div>
                        <div class="help-text">
                            <span class="fp-green"><b>Vert</b></span> : bon rendement par unité de risque.<br>
                            <span class="fp-red"><b>Rouge</b></span> : risque peu rémunéré.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )