import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import (
    init_db,
    get_user_cash_balance,
    get_portfolio_positions,
    get_user_orders,
    add_order,
    upsert_portfolio_position,
    update_cash_balance,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Portefeuille",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.user_id


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {
            --navy: #061633;
            --navy-2: #0A2248;
            --blue: #2F7CFF;
            --blue-2: #176BFF;
            --cyan: #23D8F0;
            --green: #24C98B;
            --purple: #7A5CFF;
            --orange: #FF9B16;
            --red: #D94D63;
            --text: #10233F;
            --muted: #64748B;
            --line: #DCE7F8;
            --soft: #F6FAFF;
        }

        html, body, .stApp {
            font-family: 'Inter', sans-serif !important;
            color: var(--text) !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 3%, rgba(47,124,255,.12), transparent 28%),
                radial-gradient(circle at 94% 4%, rgba(35,216,240,.14), transparent 28%),
                linear-gradient(135deg, #F8FBFF 0%, #EDF4FF 48%, #F8FFFD 100%) !important;
        }

        header,
        footer,
        #MainMenu,
        [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
        }

        .block-container {
            max-width: 100% !important;
            padding-top: 0 !important;
            padding-bottom: 3rem !important;
            padding-left: 2.45rem !important;
            padding-right: 2.45rem !important;
        }

        [data-testid="stAppViewContainer"] > .main,
        section.main > div,
        div.block-container {
            padding-top: 0 !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 25% 10%, rgba(47,124,255,.18), transparent 30%),
                linear-gradient(180deg, #061633 0%, #09224A 52%, #071831 100%) !important;
            box-shadow: 18px 0 58px rgba(7,24,49,.20);
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem !important;
        }

        section[data-testid="stSidebar"] * {
            color: #F7FAFF !important;
        }

        .sidebar-brand-wrap {
            margin-bottom: 2rem;
            padding: 0.2rem 0.25rem 0.8rem 0.25rem;
            border-bottom: 1px solid rgba(255,255,255,.08);
        }

        .fp-logo-box {
            width: 42px;
            height: 42px;
            border-radius: 14px;
            background: linear-gradient(135deg, #2F7CFF, #23D8F0, #24C98B);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: 'Sora', sans-serif;
            font-weight: 900;
            box-shadow: 0 12px 24px rgba(47,124,255,.28);
        }

        .sidebar-logo-name {
            color: white;
            font-size: 1.55rem;
            font-family: 'Sora', sans-serif;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 1;
        }

        .sidebar-logo-sub {
            color: rgba(255,255,255,.72);
            font-size: .86rem;
            margin-top: .25rem;
        }

        section[data-testid="stSidebar"] .stButton > button {
            height: 56px !important;
            border-radius: 15px !important;
            font-weight: 800 !important;
            font-size: .98rem !important;
            border: 1px solid rgba(255,255,255,.08) !important;
            background: rgba(255,255,255,.075) !important;
            color: white !important;
            justify-content: flex-start !important;
            padding-left: 1.05rem !important;
            box-shadow: none !important;
            transition: .18s ease !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            transform: translateX(2px);
            background: rgba(255,255,255,.115) !important;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #2F7CFF, #7A5CFF) !important;
            color: white !important;
            box-shadow: 0 16px 32px rgba(47,124,255,.28) !important;
            border: 1px solid rgba(255,255,255,.14) !important;
        }

        /* HERO PREMIUM */
        .portfolio-hero {
            position: relative;
            overflow: hidden;
            min-height: 255px;
            margin: 0 -0.2rem 1.2rem -0.2rem;
            padding: 2.25rem 2.6rem;
            border-radius: 0 0 34px 34px;
            color: white;
            background:
                radial-gradient(circle at 92% 22%, rgba(122,92,255,.58), transparent 22%),
                radial-gradient(circle at 70% 78%, rgba(35,216,240,.11), transparent 22%),
                linear-gradient(105deg, #051633 0%, #0A2D78 48%, #2563EB 100%);
            box-shadow: 0 24px 66px rgba(8,25,70,.25);
            border: 1px solid rgba(255,255,255,.10);
        }

        .portfolio-hero::before {
            content: "";
            position: absolute;
            width: 470px;
            height: 470px;
            right: -150px;
            top: -215px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,.09);
            box-shadow: inset 0 0 55px rgba(47,124,255,.14);
            animation: heroPulse 6s ease-in-out infinite;
        }

        .portfolio-hero::after {
            content: "";
            position: absolute;
            width: 270px;
            height: 270px;
            right: 15px;
            top: -80px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,.07);
        }

        @keyframes heroPulse {
            0%,100% { transform: scale(1); opacity:.75; }
            50% { transform: scale(1.06); opacity:1; }
        }

        .portfolio-hero-grid {
            position: relative;
            z-index: 3;
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(430px, .85fr);
            align-items: center;
            gap: 2rem;
        }

        .portfolio-hero-label {
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            color: #76F4FF;
            font-size: .88rem;
            font-weight: 900;
            letter-spacing: .12em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: .75rem;
        }

        .portfolio-hero-label::before {
            content: "";
            width: 28px;
            height: 28px;
            border-radius: 10px;
            background: linear-gradient(135deg, #2F7CFF, #23D8F0);
            box-shadow: 0 10px 22px rgba(35,216,240,.22);
        }

        .portfolio-hero-title {
            font-family: 'Sora', sans-serif;
            font-size: 3.15rem;
            font-weight: 900;
            line-height: 1.06;
            letter-spacing: -0.06em;
            color: white;
            margin-bottom: .8rem;
            max-width: 920px;
        }

        .portfolio-hero-subtitle {
            color: rgba(255,255,255,.88);
            font-size: 1.12rem;
            line-height: 1.65;
            max-width: 850px;
            font-weight: 600;
        }

        .portfolio-chip-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: .75rem;
            margin-top: 1.25rem;
        }

        .portfolio-chip {
            background: rgba(255,255,255,.105);
            border: 1px solid rgba(255,255,255,.17);
            color: white;
            border-radius: 999px;
            padding: .66rem 1rem;
            font-size: .95rem;
            font-weight: 900;
            backdrop-filter: blur(10px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.10);
        }

        .hero-visual {
            position: relative;
            height: 185px;
            border-radius: 26px;
            background: rgba(255,255,255,.065);
            border: 1px solid rgba(255,255,255,.13);
            overflow: hidden;
            backdrop-filter: blur(10px);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 16px 42px rgba(0,0,0,.13);
        }

        .hero-grid-lines {
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px);
            background-size: 100% 32px, 40px 100%;
            opacity: .42;
        }

        .hero-line-svg {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
        }

        .hero-line-bg {
            fill: none;
            stroke: rgba(103,232,249,.12);
            stroke-width: 10;
            stroke-linecap: round;
        }

        .hero-line {
            fill: none;
            stroke: #67E8F9;
            stroke-width: 3.7;
            stroke-linecap: round;
            filter: drop-shadow(0 0 9px rgba(103,232,249,.5));
            stroke-dasharray: 620;
            stroke-dashoffset: 620;
            animation: drawHeroLine 4.2s ease-in-out infinite;
        }

        @keyframes drawHeroLine {
            0% { stroke-dashoffset: 620; opacity:.6; }
            48% { stroke-dashoffset: 0; opacity:1; }
            100% { stroke-dashoffset: 0; opacity:1; }
        }

        .hero-dot {
            fill: #A5F3FC;
            filter: drop-shadow(0 0 10px rgba(165,243,252,.82));
            animation: dotPulse 1.8s ease-in-out infinite;
        }

        @keyframes dotPulse {
            0%,100% { r: 4; opacity:.75; }
            50% { r: 6.5; opacity:1; }
        }

        .hero-bars {
            position: absolute;
            right: 26px;
            bottom: 18px;
            height: 110px;
            display: flex;
            align-items: flex-end;
            gap: 10px;
        }

        .hero-bar {
            width: 17px;
            border-radius: 10px 10px 0 0;
            background: linear-gradient(180deg, rgba(94,234,212,.98), rgba(37,99,235,.18));
            animation: barMove 2.8s ease-in-out infinite alternate;
            box-shadow: 0 0 16px rgba(94,234,212,.25);
        }

        .hero-bar:nth-child(1){height:34px;animation-delay:0s}
        .hero-bar:nth-child(2){height:52px;animation-delay:.2s}
        .hero-bar:nth-child(3){height:72px;animation-delay:.4s}
        .hero-bar:nth-child(4){height:94px;animation-delay:.6s}
        .hero-bar:nth-child(5){height:68px;animation-delay:.8s}
        .hero-bar:nth-child(6){height:108px;animation-delay:1s}

        @keyframes barMove {
            from { transform: scaleY(.90); opacity:.68; }
            to { transform: scaleY(1.08); opacity:1; }
        }

        .hero-stat-card {
            position: absolute;
            top: 18px;
            right: 22px;
            background: rgba(10,20,70,.58);
            border: 1px solid rgba(255,255,255,.13);
            border-radius: 18px;
            padding: 10px 14px;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 25px rgba(0,0,0,.16);
        }

        .hero-stat-card small {
            display: block;
            color: rgba(255,255,255,.72);
            font-size: .72rem;
            font-weight: 700;
            margin-bottom: 2px;
        }

        .hero-stat-card strong {
            color: #4ADE80;
            font-size: 1.35rem;
            font-weight: 900;
        }

        /* ALERTS */
        .portfolio-alert,
        .portfolio-good,
        .portfolio-note {
            border-radius: 18px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            font-size: 1rem;
            line-height: 1.65;
            box-shadow: 0 10px 26px rgba(22,46,90,.06);
        }

        .portfolio-alert {
            background: linear-gradient(135deg, #FFF7E6, #FFFFFF);
            border: 1px solid #F4D49A;
            color: #6B4A00;
        }

        .portfolio-good {
            background: linear-gradient(135deg, #EAFBF4, #FFFFFF);
            border: 1px solid #C5F3E1;
            color: #176F53;
        }

        .portfolio-note {
            background: linear-gradient(135deg, #EAF2FF, #FFFFFF);
            border: 1px solid #CFE0FF;
            color: #204A7A;
        }

        /* KPI */
        .vivid-kpi {
            border-radius: 24px;
            padding: 1.45rem 1.35rem;
            min-height: 142px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 18px 36px rgba(30,64,140,.16);
            border: 1px solid rgba(255,255,255,.16);
        }

        .vivid-kpi::after {
            content: "";
            position: absolute;
            width: 130px;
            height: 130px;
            border-radius: 50%;
            right: -42px;
            bottom: -48px;
            background: rgba(255,255,255,.18);
        }

        .vivid-kpi-label {
            position: relative;
            z-index: 2;
            font-size: .82rem;
            font-weight: 900;
            letter-spacing: .08em;
            text-transform: uppercase;
            opacity: .94;
            font-family: 'Sora', sans-serif;
            margin-bottom: .65rem;
        }

        .vivid-kpi-value {
            position: relative;
            z-index: 2;
            font-size: 2.1rem;
            line-height: 1.08;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            color: white;
            letter-spacing: -0.04em;
        }

        .vivid-kpi-sub {
            position: relative;
            z-index: 2;
            font-size: .94rem;
            line-height: 1.5;
            margin-top: .55rem;
            opacity: .94;
            color: rgba(255,255,255,.92);
        }

        /* CARDS */
        .fp-card,
        .chart-shell,
        .portfolio-insight,
        .timeline-card,
        .sim-form-card,
        .sector-row-card,
        .sector-risk-box,
        .mini-order-card {
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .fp-card {
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(249,252,255,.94));
            border: 1px solid #DCE7F8;
            border-radius: 24px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 16px 38px rgba(22,46,90,.075);
            margin-bottom: 1rem;
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

        .fp-card-title {
            color: #10233F;
            font-size: 1.35rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.35;
            letter-spacing: -0.035em;
        }

        .fp-card-sub {
            color: #64748B;
            font-size: .97rem;
            line-height: 1.65;
            margin-top: .35rem;
        }

        .section-title-row {
            display: flex;
            align-items: center;
            gap: .85rem;
        }

        .section-icon {
            min-width: 40px;
            width: 40px;
            height: 40px;
            border-radius: 14px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            box-shadow: 0 10px 20px rgba(47,124,255,.18);
        }

        .chart-shell {
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(250,252,255,.96));
            border: 1px solid #DCE7F8;
            border-radius: 26px;
            padding: 1.1rem;
            box-shadow: 0 16px 40px rgba(22,46,90,.075);
            margin-bottom: 1.2rem;
            overflow: hidden;
        }

        div[data-testid="stPlotlyChart"] {
            border-radius: 20px !important;
            overflow: hidden !important;
            border: 1px solid #EEF3FA !important;
            background: linear-gradient(180deg, #FFFFFF, #FAFCFF) !important;
        }

        .empty-chart-card {
            background: linear-gradient(135deg, #FFFFFF, #F7FBFF);
            border: 1px dashed #BFD1EA;
            border-radius: 22px;
            padding: 2rem 1.5rem;
            min-height: 205px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(22,46,90,.04);
            margin-bottom: 1rem;
        }

        .empty-chart-title {
            color: #10233F;
            font-size: 1.45rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: .45rem;
        }

        .empty-chart-text {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.7;
        }

        .portfolio-insight {
            background: linear-gradient(135deg, #FFFFFF, #F6FAFF);
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 12px 30px rgba(22,46,90,.06);
            margin-bottom: 1rem;
        }

        .portfolio-insight-title {
            color: #10233F;
            font-size: 1.25rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: .35rem;
        }

        .portfolio-insight-text {
            color: #607088;
            font-size: .98rem;
            line-height: 1.65;
        }

        /* TABLE */
        .fp-table {
            background: rgba(255,255,255,.97);
            border: 1px solid #DCE7F8;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 14px 34px rgba(22,46,90,.075);
            margin-bottom: 1.1rem;
        }

        .fp-table-title {
            color: #10233F;
            font-size: 1.45rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            padding: 1.25rem 1.4rem;
            border-bottom: 1px solid #E5EDF8;
        }

        .fp-row {
            display: grid;
            align-items: center;
            gap: 1rem;
            padding: 1.05rem 1.4rem;
            min-height: 78px;
            border-bottom: 1px solid #EEF3FA;
        }

        .fp-row:last-child {
            border-bottom: none;
        }

        .fp-row-header {
            background: #F4F8FF;
            color: #64748B;
            font-size: .82rem;
            font-weight: 900;
            letter-spacing: .07em;
            text-transform: uppercase;
            min-height: auto;
            padding-top: .9rem;
            padding-bottom: .9rem;
        }

        .fp-main-text {
            color: #10233F;
            font-size: 1rem;
            font-weight: 900;
            line-height: 1.35;
        }

        .fp-sub-text {
            color: #64748B;
            font-size: .88rem;
            line-height: 1.45;
            margin-top: .18rem;
        }

        .fp-positive {
            color: #1C9C73 !important;
        }

        .fp-negative {
            color: #D44D61 !important;
        }

        .price-badge {
            display: inline-block;
            margin-top: .25rem;
            padding: .25rem .58rem;
            border-radius: 999px;
            background: #EAF2FF;
            color: #2F7CFF;
            font-size: .76rem;
            font-weight: 900;
        }

        /* FORM */
        .sim-form-card {
            background: linear-gradient(135deg, #FFFFFF, #F7FBFF);
            border: 1px solid #DCE7F8;
            border-radius: 24px;
            padding: 1.25rem;
            box-shadow: 0 14px 34px rgba(22,46,90,.07);
            margin-bottom: 1rem;
        }

        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label {
            font-size: .92rem !important;
            font-weight: 900 !important;
            color: #10233F !important;
            font-family: 'Sora', sans-serif !important;
        }

        .stTextInput input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] > div {
            font-size: 1rem !important;
            min-height: 50px !important;
            border-radius: 14px !important;
            border: 1px solid #DCE7F8 !important;
            box-shadow: 0 8px 20px rgba(22,46,90,.04);
        }

        .stButton > button {
            font-size: 1rem !important;
            height: 58px !important;
            border-radius: 16px !important;
            font-weight: 900 !important;
            border: 1px solid #DCE7F8 !important;
            box-shadow: 0 12px 26px rgba(22,46,90,.055) !important;
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

        /* Timeline */
        .timeline-card {
            background: linear-gradient(135deg, #FFFFFF, #F7FBFF);
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.1rem 1.15rem;
            box-shadow: 0 12px 30px rgba(22,46,90,.065);
            min-height: 128px;
        }

        .timeline-step {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Sora', sans-serif;
            margin-bottom: .65rem;
        }

        .timeline-title {
            color: #10233F;
            font-size: 1rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: .35rem;
        }

        .timeline-value {
            color: #2F7CFF;
            font-size: 1.45rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            line-height: 1.15;
        }

        .timeline-text {
            color: #64748B;
            font-size: .88rem;
            line-height: 1.5;
            margin-top: .35rem;
        }

        /* Sector allocation */
        .sector-row-card {
            background: #FFFFFF;
            border: 1px solid #DCE7F8;
            border-radius: 18px;
            padding: .95rem 1rem;
            box-shadow: 0 9px 22px rgba(22,46,90,.055);
            margin-bottom: .75rem;
        }

        .sector-row-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: .55rem;
        }

        .sector-name {
            color: #10233F;
            font-size: .95rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
        }

        .sector-weight {
            color: #2F7CFF;
            font-size: .95rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
        }

        .sector-bar-wrap {
            height: 9px;
            background: #E7EEF9;
            border-radius: 999px;
            overflow: hidden;
        }

        .sector-bar {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
        }

        .sector-risk-box {
            background: linear-gradient(135deg, #FFFFFF, #F8FBFF);
            border: 1px solid #DCE7F8;
            border-radius: 20px;
            padding: 1.1rem;
            box-shadow: 0 10px 26px rgba(22,46,90,.055);
            margin-bottom: 1rem;
        }

        .sector-risk-title {
            color: #10233F;
            font-size: 1.05rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
            margin-bottom: .35rem;
        }

        .sector-risk-text {
            color: #607088;
            font-size: .92rem;
            line-height: 1.6;
        }

        .mini-order-card {
            background: #FFFFFF;
            border: 1px solid #DCE7F8;
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: .75rem;
            box-shadow: 0 9px 22px rgba(22,46,90,.055);
        }

        .mini-order-title {
            color: #10233F;
            font-size: 1rem;
            font-weight: 900;
            font-family: 'Sora', sans-serif;
        }

        .mini-order-text {
            color: #64748B;
            font-size: .9rem;
            line-height: 1.6;
            margin-top: .35rem;
        }

        .order-buy {
            color: #1C9C73 !important;
            font-weight: 900;
        }

        .order-sell {
            color: #D44D61 !important;
            font-weight: 900;
        }

        @media (max-width: 1200px) {
            .portfolio-hero-grid {
                grid-template-columns: 1fr;
            }

            .portfolio-hero-title {
                font-size: 2.45rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def get_order_field(order, key, default=None):
    if isinstance(order, dict):
        return order.get(key, default)
    return getattr(order, key, default)


DEFAULT_SECTEURS = {
    "AAPL": "Technologie",
    "MSFT": "Technologie",
    "NVDA": "Technologie",
    "AMZN": "Consommation discrétionnaire",
    "GOOGL": "Communication",
    "GOOG": "Communication",
    "META": "Communication",
    "JNJ": "Santé",
    "UNH": "Santé",
    "PFE": "Santé",
    "JPM": "Finance",
    "V": "Finance",
    "MA": "Finance",
    "GS": "Finance",
    "KO": "Consommation de base",
    "PG": "Consommation de base",
    "WMT": "Consommation de base",
    "MCD": "Consommation discrétionnaire",
    "DIS": "Communication",
    "CAT": "Industrie",
    "BA": "Industrie",
    "MMM": "Industrie",
    "XOM": "Énergie",
    "CVX": "Énergie",
    "SPY": "ETF diversifié",
    "VTI": "ETF diversifié",
}

# Actions proposées dans la barre de recherche du formulaire d'ordre.
# Streamlit selectbox est recherchable : l'utilisateur peut taper le nom ou le ticker.
ACTIONS_DISPONIBLES = {
    "Apple Inc. — AAPL — Technologie": {
        "ticker": "AAPL", "name": "Apple Inc.", "sector": "Technologie", "default_price": 195.0
    },
    "Microsoft — MSFT — Technologie": {
        "ticker": "MSFT", "name": "Microsoft", "sector": "Technologie", "default_price": 421.7
    },
    "NVIDIA — NVDA — Technologie": {
        "ticker": "NVDA", "name": "NVIDIA", "sector": "Technologie", "default_price": 120.0
    },
    "Alphabet — GOOGL — Communication": {
        "ticker": "GOOGL", "name": "Alphabet", "sector": "Communication", "default_price": 175.0
    },
    "Amazon — AMZN — Consommation discrétionnaire": {
        "ticker": "AMZN", "name": "Amazon", "sector": "Consommation discrétionnaire", "default_price": 185.0
    },
    "Meta Platforms — META — Communication": {
        "ticker": "META", "name": "Meta Platforms", "sector": "Communication", "default_price": 480.0
    },
    "Johnson & Johnson — JNJ — Santé": {
        "ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Santé", "default_price": 158.0
    },
    "UnitedHealth — UNH — Santé": {
        "ticker": "UNH", "name": "UnitedHealth", "sector": "Santé", "default_price": 510.0
    },
    "Pfizer — PFE — Santé": {
        "ticker": "PFE", "name": "Pfizer", "sector": "Santé", "default_price": 28.0
    },
    "JPMorgan Chase — JPM — Finance": {
        "ticker": "JPM", "name": "JPMorgan Chase", "sector": "Finance", "default_price": 191.8
    },
    "Visa — V — Finance": {
        "ticker": "V", "name": "Visa", "sector": "Finance", "default_price": 279.4
    },
    "Mastercard — MA — Finance": {
        "ticker": "MA", "name": "Mastercard", "sector": "Finance", "default_price": 455.0
    },
    "Coca-Cola — KO — Consommation de base": {
        "ticker": "KO", "name": "Coca-Cola", "sector": "Consommation de base", "default_price": 78.4
    },
    "Procter & Gamble — PG — Consommation de base": {
        "ticker": "PG", "name": "Procter & Gamble", "sector": "Consommation de base", "default_price": 168.0
    },
    "Walmart — WMT — Consommation de base": {
        "ticker": "WMT", "name": "Walmart", "sector": "Consommation de base", "default_price": 127.6
    },
    "McDonald's — MCD — Consommation discrétionnaire": {
        "ticker": "MCD", "name": "McDonald's", "sector": "Consommation discrétionnaire", "default_price": 290.0
    },
    "Cisco Systems — CSCO — Technologie": {
        "ticker": "CSCO", "name": "Cisco Systems", "sector": "Technologie", "default_price": 52.0
    },
    "Verizon — VZ — Communication": {
        "ticker": "VZ", "name": "Verizon", "sector": "Communication", "default_price": 40.0
    },
    "Exxon Mobil — XOM — Énergie": {
        "ticker": "XOM", "name": "Exxon Mobil", "sector": "Énergie", "default_price": 115.0
    },
    "SPDR S&P 500 ETF — SPY — ETF diversifié": {
        "ticker": "SPY", "name": "SPDR S&P 500 ETF", "sector": "ETF diversifié", "default_price": 520.0
    },
}


def get_action_meta_from_label(label):
    return ACTIONS_DISPONIBLES.get(label, next(iter(ACTIONS_DISPONIBLES.values())))


def get_suggested_order_price(ticker, fallback_price):
    latest = get_latest_price(ticker)
    if latest is not None and latest > 0:
        return float(latest), "Marché"
    return float(fallback_price), "Estimé"


def get_sector_for_ticker(ticker):
    ticker_clean = str(ticker).upper().strip()

    try:
        from config import SECTEURS
        if ticker_clean in SECTEURS and SECTEURS[ticker_clean]:
            return SECTEURS[ticker_clean]
    except Exception:
        pass

    return DEFAULT_SECTEURS.get(ticker_clean, "Autre")


def build_sector_allocation(position_rows, cash_balance):
    total = cash_balance + sum(row["value"] for row in position_rows)
    sector_values = {}

    if cash_balance > 0:
        sector_values["Cash"] = cash_balance

    for row in position_rows:
        sector = row.get("secteur", "Autre")
        sector_values[sector] = sector_values.get(sector, 0.0) + row["value"]

    sector_rows = []
    for sector, value in sector_values.items():
        weight = (value / total * 100) if total > 0 else 0
        sector_rows.append(
            {
                "sector": sector,
                "value": value,
                "weight": weight,
            }
        )

    sector_rows = sorted(sector_rows, key=lambda x: x["weight"], reverse=True)
    return sector_rows


def sector_commentary(sector_rows):
    non_cash = [row for row in sector_rows if row["sector"] != "Cash"]

    if not non_cash:
        return "Le portefeuille est entièrement en cash. Il n’existe pas encore d’exposition sectorielle."

    dominant = max(non_cash, key=lambda x: x["weight"])

    if len(non_cash) == 1:
        return (
            f"Le portefeuille est exposé à un seul secteur : {dominant['sector']}. "
            "La diversification sectorielle est faible, ce qui augmente le risque spécifique."
        )

    if dominant["weight"] > 45:
        return (
            f"Le secteur dominant est {dominant['sector']} avec {dominant['weight']:.1f}% du portefeuille. "
            "Une diversification vers d’autres secteurs pourrait réduire la dépendance à un seul thème."
        )

    return "La répartition sectorielle est relativement diversifiée. Aucun secteur ne domine excessivement le portefeuille."


@st.cache_data(show_spinner=False, ttl=900)
def get_latest_price(ticker):
    try:
        import yfinance as yf

        ticker = str(ticker).upper().strip()
        data = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=False)

        if data is None or data.empty:
            return None

        if "Close" in data.columns:
            close = data["Close"].dropna()
            if not close.empty:
                value = close.iloc[-1]

                if hasattr(value, "iloc"):
                    value = value.iloc[0]

                return float(value)

        return None

    except Exception:
        return None


def build_position_rows(positions):
    rows = []
    invested = 0.0
    real_price_count = 0

    for ticker, nom, qty, avg_buy_price in positions:
        if qty <= 0:
            continue

        ticker_clean = str(ticker).upper().strip()
        latest_price = get_latest_price(ticker_clean)

        if latest_price is not None and latest_price > 0:
            current_price = latest_price
            price_source = "Marché"
            real_price_count += 1
        else:
            current_price = avg_buy_price * 1.04
            price_source = "Estimé"

        value = qty * current_price
        pnl_pct = ((current_price - avg_buy_price) / avg_buy_price * 100) if avg_buy_price else 0

        invested += value

        rows.append(
            {
                "ticker": ticker_clean,
                "nom": nom,
                "qty": qty,
                "avg": avg_buy_price,
                "current": current_price,
                "value": value,
                "pnl_pct": pnl_pct,
                "price_source": price_source,
                "secteur": get_sector_for_ticker(ticker_clean),
            }
        )

    return rows, invested, real_price_count


def build_demo_positions():
    sample_positions = [
        ("JNJ", "Johnson & Johnson", 18, 152.40, 158.20),
        ("JPM", "JPMorgan Chase", 10, 186.10, 191.80),
        ("V", "Visa", 9, 272.80, 279.40),
        ("MSFT", "Microsoft", 5, 410.20, 421.70),
    ]

    rows = []
    invested = 0.0

    for ticker, nom, qty, avg, current in sample_positions:
        value = qty * current
        pnl_pct = ((current - avg) / avg) * 100 if avg else 0
        invested += value

        rows.append(
            {
                "ticker": ticker,
                "nom": nom,
                "qty": qty,
                "avg": avg,
                "current": current,
                "value": value,
                "pnl_pct": pnl_pct,
                "price_source": "Démo",
                "secteur": get_sector_for_ticker(ticker),
            }
        )

    return rows, invested


def get_real_position_map(positions):
    position_map = {}

    for ticker, nom, qty, avg_buy_price in positions:
        ticker_clean = str(ticker).upper().strip()
        position_map[ticker_clean] = {
            "ticker": ticker_clean,
            "nom": nom,
            "qty": qty,
            "avg": avg_buy_price,
        }

    return position_map


def portfolio_commentary(cash_balance, invested_value, position_rows):
    total = cash_balance + invested_value

    if total <= 0:
        return "Le portefeuille est vide. Commencez par simuler un premier achat."

    cash_weight = cash_balance / total * 100

    if not position_rows:
        return "Votre portefeuille est entièrement en cash. Le risque est faible, mais vous n’êtes pas encore exposé au marché."

    max_position = max(position_rows, key=lambda x: x["value"])
    max_weight = max_position["value"] / total * 100

    if len(position_rows) == 1:
        return (
            f"Votre portefeuille contient une seule position : {max_position['ticker']}. "
            "C’est lisible, mais le risque spécifique reste concentré sur une seule action."
        )

    if cash_weight > 50:
        return (
            f"Le portefeuille est très liquide : le cash représente {cash_weight:.1f}% du total. "
            "C’est prudent, mais le rendement potentiel peut être limité."
        )

    if max_weight > 30:
        return (
            f"{max_position['ticker']} représente {max_weight:.1f}% du portefeuille. "
            "Pensez à diversifier pour réduire le risque spécifique."
        )

    return "L’allocation est relativement équilibrée. La prochaine étape est d’analyser la diversification sectorielle."


def show_sidebar():
    render_sidebar(
        active_page="portefeuille",
        cash_balance=cash_balance,
        logout_callback=logout,
    )


# ============================================================
# DATA
# ============================================================

cash_balance = get_user_cash_balance(user_id)
positions = get_portfolio_positions(user_id)
orders = get_user_orders(user_id)

real_position_map = get_real_position_map(positions)
has_real_positions = len([p for p in positions if p[2] > 0]) > 0

if has_real_positions:
    position_rows, invested_value, real_price_count = build_position_rows(positions)
    using_demo_data = False
else:
    position_rows, invested_value = build_demo_positions()
    real_price_count = 0
    using_demo_data = True

total_portfolio = cash_balance + invested_value
global_pnl = sum((r["current"] - r["avg"]) * r["qty"] for r in position_rows)
global_pnl_pct = (global_pnl / invested_value * 100) if invested_value > 0 else 0

sector_rows = build_sector_allocation(position_rows, cash_balance)

pnl_sign = "+" if global_pnl >= 0 else ""
pnl_class = "fp-positive" if global_pnl >= 0 else "fp-negative"


# ============================================================
# SIDEBAR + HEADER
# ============================================================

show_sidebar()

hero_html = f"""
<div class="portfolio-hero">
    <div class="portfolio-hero-grid">
        <div>
            <div class="portfolio-hero-label">Portefeuille</div>
            <div class="portfolio-hero-title">Vue d’ensemble de vos positions</div>
            <div class="portfolio-hero-subtitle">
                Suivez votre portefeuille, votre cash, vos performances et vos opérations dans une interface claire et dynamique.
            </div>
            <div class="portfolio-chip-wrap">
                <div class="portfolio-chip">Total : ${total_portfolio:,.2f}</div>
                <div class="portfolio-chip">Cash : ${cash_balance:,.2f}</div>
                <div class="portfolio-chip">Positions : {len(position_rows)}</div>
                <div class="portfolio-chip">P/L latent : {pnl_sign}${global_pnl:,.2f}</div>
            </div>
        </div>

        <div class="hero-visual">
            <div class="hero-grid-lines"></div>

            <svg class="hero-line-svg" viewBox="0 0 460 185" preserveAspectRatio="none">
                <path class="hero-line-bg"
                      d="M10,136 C38,122 55,80 82,92 C118,108 134,142 165,112 C193,85 212,56 244,74 C275,92 289,43 326,54 C360,64 376,25 450,20" />
                <path class="hero-line"
                      d="M10,136 C38,122 55,80 82,92 C118,108 134,142 165,112 C193,85 212,56 244,74 C275,92 289,43 326,54 C360,64 376,25 450,20" />
                <circle class="hero-dot" cx="450" cy="20" r="4"></circle>
            </svg>

            <div class="hero-bars">
                <div class="hero-bar"></div>
                <div class="hero-bar"></div>
                <div class="hero-bar"></div>
                <div class="hero-bar"></div>
                <div class="hero-bar"></div>
                <div class="hero-bar"></div>
            </div>

            <div class="hero-stat-card">
                <small>Performance simulée</small>
                <strong>{pnl_sign}{global_pnl_pct:.2f}%</strong>
            </div>
        </div>
    </div>
</div>
"""

hero_html = "\n".join(line.strip() for line in hero_html.strip().splitlines())
st.markdown(hero_html, unsafe_allow_html=True)

if using_demo_data:
    st.markdown(
        """
        <div class="portfolio-alert">
            <b>Données de démonstration :</b> aucune position réelle n’est enregistrée. Les positions ci-dessous illustrent le fonctionnement.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    if real_price_count > 0:
        st.markdown(
            f"""
            <div class="portfolio-good">
                <b>Portefeuille réel :</b> {real_price_count} prix de marché récupéré(s). Les autres prix peuvent être estimés.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="portfolio-alert">
                <b>Prix estimés :</b> aucun prix de marché récupéré. Vérifiez votre connexion ou yfinance.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# KPI
# ============================================================

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.markdown(
        f"""
        <div class="vivid-kpi" style="background:linear-gradient(135deg,#2F7CFF,#1E5FE6);">
            <div class="vivid-kpi-label">Valeur totale</div>
            <div class="vivid-kpi-value">${total_portfolio:,.2f}</div>
            <div class="vivid-kpi-sub">Portefeuille + liquidités</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    pnl_bg = "linear-gradient(135deg,#19B87B,#0F9E66)" if global_pnl >= 0 else "linear-gradient(135deg,#E84A5F,#B83245)"
    st.markdown(
        f"""
        <div class="vivid-kpi" style="background:{pnl_bg};">
            <div class="vivid-kpi-label">Gain / perte latent</div>
            <div class="vivid-kpi-value">{pnl_sign}${global_pnl:,.2f}</div>
            <div class="vivid-kpi-sub">{pnl_sign}{global_pnl_pct:.2f}% sur les positions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="vivid-kpi" style="background:linear-gradient(135deg,#7A5CFF,#5E3EEA);">
            <div class="vivid-kpi-label">Cash disponible</div>
            <div class="vivid-kpi-value">${cash_balance:,.2f}</div>
            <div class="vivid-kpi-sub">Capital prêt à être investi</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f"""
        <div class="vivid-kpi" style="background:linear-gradient(135deg,#FFAE36,#F18A00);">
            <div class="vivid-kpi-label">Positions ouvertes</div>
            <div class="vivid-kpi-value">{len(position_rows)}</div>
            <div class="vivid-kpi-sub">Lignes suivies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

left, right = st.columns([1.75, 1], gap="large")


# ============================================================
# LEFT COLUMN
# ============================================================

with left:
    st.markdown(
        """
        <div class="fp-card">
            <div class="section-title-row">
                <div class="section-icon">1</div>
                <div>
                    <div class="fp-card-title">Évolution du portefeuille</div>
                    <div class="fp-card-sub">Valeur estimée du portefeuille après vos opérations.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Courbe d'évolution de la valeur du portefeuille
    # Timeline + courbe d'évolution de la valeur du portefeuille
    if orders:
        sorted_orders = list(reversed(orders))

        initial_value = 10000.0
        first_order = sorted_orders[0]
        last_order = sorted_orders[-1]

        first_type = get_order_field(first_order, "order_type", "")
        first_ticker = get_order_field(first_order, "ticker", "")
        first_cash_after = float(get_order_field(first_order, "cash_after", cash_balance))

        last_cash_after = float(get_order_field(last_order, "cash_after", cash_balance))
        current_value = total_portfolio
        latent_gain = current_value - initial_value
        latent_gain_sign = "+" if latent_gain >= 0 else ""
        latent_gain_class = "fp-positive" if latent_gain >= 0 else "fp-negative"

        first_label = "Achat" if first_type == "BUY" else "Vente"

        t1, t2, t3 = st.columns(3, gap="medium")

        with t1:
            st.markdown(
                f'<div class="timeline-card"><div class="timeline-step">1</div><div class="timeline-title">Départ</div><div class="timeline-value">${initial_value:,.2f}</div><div class="timeline-text">Capital initial de simulation.</div></div>',
                unsafe_allow_html=True,
            )

        with t2:
            st.markdown(
                f'<div class="timeline-card"><div class="timeline-step">2</div><div class="timeline-title">Après première opération</div><div class="timeline-value">${first_cash_after:,.2f}</div><div class="timeline-text">{first_label} sur <b>{first_ticker}</b>. Cash restant après ordre.</div></div>',
                unsafe_allow_html=True,
            )

        with t3:
            st.markdown(
                f'<div class="timeline-card"><div class="timeline-step">3</div><div class="timeline-title">Aujourd’hui</div><div class="timeline-value">${current_value:,.2f}</div><div class="timeline-text">Valeur actuelle estimée : <span class="{latent_gain_class}" style="font-weight:900;">{latent_gain_sign}${latent_gain:,.2f}</span></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        portfolio_dates = ["Départ"]
        portfolio_values = [initial_value]

        for idx, order in enumerate(sorted_orders, start=1):
            cash_after = float(get_order_field(order, "cash_after", cash_balance))

            # Approximation pédagogique :
            # cash après ordre + valeur actuelle des positions.
            estimated_portfolio_value = cash_after + invested_value

            if len(sorted_orders) == 1:
                label = "Après ordre"
            else:
                label = f"Ordre {idx}"

            portfolio_dates.append(label)
            portfolio_values.append(estimated_portfolio_value)

        portfolio_dates.append("Aujourd’hui")
        portfolio_values.append(total_portfolio)

        fig_portfolio = go.Figure()

        fig_portfolio.add_trace(
            go.Scatter(
                x=portfolio_dates,
                y=portfolio_values,
                mode="lines+markers",
                line=dict(color="#2F7CFF", width=5, shape="spline"),
                marker=dict(size=12, color="#31E6A8", line=dict(color="white", width=3)),
                fill="tozeroy",
                fillcolor="rgba(47,124,255,0.13)",
                hovertemplate="<b>%{x}</b><br>Valeur : $%{y:,.2f}<extra></extra>",
            )
        )

        y_min = min(portfolio_values)
        y_max = max(portfolio_values)
        delta = y_max - y_min

        if delta == 0:
            delta = y_max * 0.05 if y_max else 100

        # Axe volontairement resserré pour rendre la variation visible.
        y_min = y_min - delta * 0.35
        y_max = y_max + delta * 0.35

        fig_portfolio.update_layout(
            height=390,
            margin=dict(l=20, r=20, t=20, b=45),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#10233F"),
            xaxis=dict(
                type="category",
                showgrid=False,
                zeroline=False,
                tickfont=dict(color="#53657F", size=13),
            ),
            yaxis=dict(
                range=[y_min, y_max],
                showgrid=True,
                gridcolor="#E6EEF8",
                zeroline=False,
                tickfont=dict(color="#53657F", size=13),
                tickprefix="$",
            ),
            showlegend=False,
        )

        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.plotly_chart(fig_portfolio, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        if len(sorted_orders) == 1:
            st.markdown(
                """
                <div class="portfolio-note">
                    Avec une seule opération, la courbe reste volontairement simple. Elle deviendra plus détaillée après plusieurs achats ou ventes.
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.markdown(
            """
            <div class="empty-chart-card">
                <div class="empty-chart-title">Aucun ordre enregistré</div>
                <div class="empty-chart-text">
                    La timeline et la courbe d’évolution apparaîtront après votre première opération.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="portfolio-insight">
            <div class="portfolio-insight-title">Lecture rapide</div>
            <div class="portfolio-insight-text">{portfolio_commentary(cash_balance, invested_value, position_rows)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="fp-table">
            <div class="fp-table-title">Positions du portefeuille</div>
            <div class="fp-row fp-row-header" style="grid-template-columns:2fr 1fr 1fr 1fr;">
                <div>Actif</div>
                <div>Prix actuel</div>
                <div>Performance</div>
                <div>Poids</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    for row in position_rows:
        weight = (row["value"] / invested_value * 100) if invested_value > 0 else 0
        var_class = "fp-positive" if row["pnl_pct"] >= 0 else "fp-negative"

        st.markdown(
            f"""
            <div class="fp-row" style="grid-template-columns:2fr 1fr 1fr 1fr;">
                <div>
                    <div class="fp-main-text">{row["nom"]} ({row["ticker"]})</div>
                    <div class="fp-sub-text">Quantité {row["qty"]:.2f} · PRU ${row["avg"]:,.2f} · {row["secteur"]}</div>
                </div>
                <div>
                    <div class="fp-main-text">${row["current"]:,.2f}</div>
                    <div class="price-badge">{row["price_source"]}</div>
                </div>
                <div class="fp-main-text {var_class}">{row["pnl_pct"]:+.2f}%</div>
                <div>
                    <div class="fp-main-text">{weight:.1f}%</div>
                    <div style="height:8px;background:#E7EEF9;border-radius:99px;margin-top:0.5rem;overflow:hidden;">
                        <div style="height:100%;width:{min(weight,100)}%;background:linear-gradient(135deg,#2F7CFF,#31E6A8);border-radius:99px;"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="fp-card">
            <div class="section-title-row">
                <div class="section-icon">+</div>
                <div>
                    <div class="fp-card-title">Simuler un ordre</div>
                    <div class="fp-card-sub">Testez un achat ou une vente en toute sécurité.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sim-form-card">', unsafe_allow_html=True)

    oc1, oc2, oc3 = st.columns([1.45, 0.75, 0.80])

    with oc1:
        selected_action_label = st.selectbox(
            "Action à simuler",
            options=list(ACTIONS_DISPONIBLES.keys()),
            key="order_action_select",
            help="Tapez le nom de l’action ou son ticker pour la rechercher rapidement.",
        )
        selected_action = get_action_meta_from_label(selected_action_label)
        order_ticker = selected_action["ticker"].upper().strip()
        order_name = selected_action["name"]
        order_sector = selected_action["sector"]

    suggested_price, price_source = get_suggested_order_price(
        order_ticker,
        selected_action.get("default_price", 100.0),
    )

    with oc2:
        order_qty = st.number_input("Quantité", min_value=0.01, value=1.0, step=0.01, key="order_qty")

    with oc3:
        order_price = st.number_input(
            "Prix unitaire ($)",
            min_value=0.01,
            value=float(round(suggested_price, 2)),
            step=0.01,
            key=f"order_price_{order_ticker}",
            help="Prix prérempli automatiquement quand le cours est disponible ; vous pouvez le modifier pour une simulation.",
        )

    st.markdown(
        f"""
        <div class="portfolio-note" style="margin-top:.4rem;">
            <b>Action sélectionnée :</b> {order_name} ({order_ticker}) · {order_sector}<br>
            <b>Prix proposé :</b> ${order_price:,.2f} · Source : {price_source}
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2 = st.columns(2)

    with b1:
        if st.button("Acheter", use_container_width=True, type="primary", key="btn_buy"):
            ticker_clean = order_ticker
            total = order_qty * order_price

            if total > cash_balance:
                st.error(f"Cash insuffisant. Solde disponible : ${cash_balance:,.2f}")
            else:
                new_cash = cash_balance - total

                update_cash_balance(user_id, new_cash)
                upsert_portfolio_position(user_id, ticker_clean, order_name, order_qty, order_price)
                add_order(user_id, ticker_clean, "BUY", order_qty, order_price, total, new_cash)

                st.success(f"Achat enregistré : {order_qty:.2f} action(s) {order_name} ({ticker_clean}).")
                st.experimental_rerun()

    with b2:
        if st.button("Vendre", use_container_width=True, key="btn_sell"):
            ticker_clean = order_ticker
            total = order_qty * order_price

            if ticker_clean not in real_position_map:
                st.error(f"Vente impossible : vous ne détenez aucune position {ticker_clean}.")
            elif real_position_map[ticker_clean]["qty"] < order_qty:
                st.error(
                    f"Vente impossible : quantité détenue insuffisante. "
                    f"Vous détenez {real_position_map[ticker_clean]['qty']:.2f} action(s) {ticker_clean}."
                )
            else:
                new_cash = cash_balance + total

                update_cash_balance(user_id, new_cash)
                upsert_portfolio_position(user_id, ticker_clean, order_name, -order_qty, order_price)
                add_order(user_id, ticker_clean, "SELL", order_qty, order_price, total, new_cash)

                st.success(f"Vente enregistrée : {order_qty:.2f} action(s) {order_name} ({ticker_clean}).")
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RIGHT COLUMN
# ============================================================

with right:
    st.markdown(
        """
        <div class="fp-card">
            <div class="section-title-row">
                <div class="section-icon">%</div>
                <div>
                    <div class="fp-card-title">Répartition</div>
                    <div class="fp-card-sub">Allocation entre positions et cash.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    labels = [r["ticker"] for r in position_rows] + ["Cash"]
    values = [r["value"] for r in position_rows] + [cash_balance]

    fig_alloc = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                marker=dict(colors=["#2F7CFF", "#31E6A8", "#7A5CFF", "#F3C969", "#D44D61", "#6EA8FF"]),
                textinfo="label",
                hovertemplate="%{label}: $%{value:,.0f}<extra></extra>",
            )
        ]
    )

    fig_alloc.update_traces(
        textfont=dict(family="Inter", size=13, color="#10233F"),
        marker=dict(line=dict(color="white", width=3)),
    )

    fig_alloc.update_layout(
        height=395,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#10233F", size=14),
        showlegend=True,
        legend=dict(
            orientation="v",
            font=dict(size=12, color="#10233F"),
        ),
    )

    st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
    st.plotly_chart(fig_alloc, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="fp-card">
            <div class="section-title-row">
                <div class="section-icon">S</div>
                <div>
                    <div class="fp-card-title">Répartition par secteur</div>
                    <div class="fp-card-sub">Lecture du risque sectoriel du portefeuille.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for sector_item in sector_rows:
        sector = sector_item["sector"]
        weight = sector_item["weight"]
        value = sector_item["value"]

        st.markdown(
            f"""
            <div class="sector-row-card">
                <div class="sector-row-head">
                    <div class="sector-name">{sector}</div>
                    <div class="sector-weight">{weight:.1f}%</div>
                </div>
                <div class="sector-bar-wrap">
                    <div class="sector-bar" style="width:{min(weight, 100)}%;"></div>
                </div>
                <div class="fp-sub-text" style="margin-top:0.55rem;">${value:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="sector-risk-box">
            <div class="sector-risk-title">Analyse sectorielle</div>
            <div class="sector-risk-text">{sector_commentary(sector_rows)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if position_rows:
        best = max(position_rows, key=lambda x: x["pnl_pct"])

        if len(position_rows) == 1:
            st.markdown(
                f"""
                <div class="fp-card">
                    <div class="fp-card-title">Position principale</div>
                    <div class="fp-card-sub" style="font-size:1.25rem;font-weight:900;color:#10233F;">{best["nom"]} ({best["ticker"]})</div>
                    <div class="fp-card-sub {pnl_class}" style="font-size:1.25rem;font-weight:900;">{best["pnl_pct"]:+.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            worst = min(position_rows, key=lambda x: x["pnl_pct"])

            st.markdown(
                f"""
                <div class="fp-card">
                    <div class="fp-card-title">Meilleure position</div>
                    <div class="fp-card-sub" style="font-size:1.25rem;font-weight:900;color:#10233F;">{best["nom"]} ({best["ticker"]})</div>
                    <div class="fp-card-sub fp-positive" style="font-size:1.25rem;font-weight:900;">{best["pnl_pct"]:+.2f}%</div>
                </div>

                <div class="fp-card">
                    <div class="fp-card-title">Position à surveiller</div>
                    <div class="fp-card-sub" style="font-size:1.25rem;font-weight:900;color:#10233F;">{worst["nom"]} ({worst["ticker"]})</div>
                    <div class="fp-card-sub fp-negative" style="font-size:1.25rem;font-weight:900;">{worst["pnl_pct"]:+.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="fp-card">
                <div class="fp-card-title">Ordres enregistrés</div>
                <div class="fp-card-sub" style="font-size:1.25rem;font-weight:900;color:#10233F;">{len(orders)} opération(s)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="fp-card">
            <div class="fp-card-title">Derniers ordres</div>
            <div class="fp-card-sub">Aperçu rapide des opérations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if orders:
        last_orders = orders[:5]

        for order in last_orders:
            otype = get_order_field(order, "order_type", "")
            ticker = get_order_field(order, "ticker", "")
            qty = float(get_order_field(order, "quantity", 0))
            price = float(get_order_field(order, "price", 0))
            total = float(get_order_field(order, "total", qty * price))
            created_at = str(get_order_field(order, "created_at", ""))[:16].replace("T", " ")

            label = "Achat" if otype == "BUY" else "Vente"
            label_class = "order-buy" if otype == "BUY" else "order-sell"

            st.markdown(
                f"""
                <div class="mini-order-card">
                    <div class="mini-order-title">
                        <span class="{label_class}">{label}</span> · {ticker}
                    </div>
                    <div class="mini-order-text">
                        Quantité : <b>{qty:.2f}</b> · Prix : <b>${price:,.2f}</b> · Total : <b>${total:,.2f}</b><br>
                        {created_at}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="portfolio-note">
                Aucun ordre enregistré. Créez votre première simulation avec le formulaire.
            </div>
            """,
            unsafe_allow_html=True,
        )
