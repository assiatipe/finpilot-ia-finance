import streamlit as st
import sys
import os
from textwrap import dedent

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import init_auth_state, logout
from database import (
    init_db,
    get_user_cash_balance,
    get_user_initial_capital,
    has_user_capital_configured,
    load_user_history,
    get_user_orders,
    get_portfolio_positions,
    get_user_feedbacks,
)
from styles import load_global_styles
from sidebar_ui import render_sidebar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinPilot · Progression",
    page_icon="assets/finpilot_logo_final.png",
    layout="wide",
)

init_db()
init_auth_state()
st.markdown(load_global_styles(), unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.user_id
cash_balance = get_user_cash_balance(user_id)


# ============================================================
# HELPERS
# ============================================================

def html(content: str):
    cleaned = "\n".join(line.strip() for line in dedent(content).strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def safe_len(value):
    try:
        return len(value)
    except Exception:
        return 0


def calculate_progression(user_id: int):
    """
    Calcule les points, le niveau et les badges à partir des données déjà existantes.
    Aucune nouvelle table n'est nécessaire.
    """

    try:
        capital_configured = has_user_capital_configured(user_id)
    except Exception:
        capital_configured = False

    try:
        initial_capital = get_user_initial_capital(user_id)
    except Exception:
        initial_capital = 0.0

    try:
        analyses = load_user_history(user_id)
    except Exception:
        analyses = []

    try:
        orders = get_user_orders(user_id)
    except Exception:
        orders = []

    try:
        positions = get_portfolio_positions(user_id)
    except Exception:
        positions = []

    try:
        feedbacks = get_user_feedbacks(user_id)
    except Exception:
        feedbacks = []

    nb_analyses = safe_len(analyses)
    nb_orders = safe_len(orders)
    nb_positions = safe_len(positions)
    nb_feedbacks = safe_len(feedbacks)

    # Points simples et compréhensibles pour la présentation
    points = 0

    if capital_configured or initial_capital > 0:
        points += 10

    points += nb_analyses * 20
    points += nb_orders * 15
    points += nb_positions * 15

    if nb_feedbacks > 0:
        points += 10

    # Niveau
    if points < 30:
        level = "Bronze"
        level_color = "#B7791F"
        level_subtitle = "Découverte de l’application"
        next_level = "Silver"
        next_threshold = 30
        previous_threshold = 0
    elif points < 70:
        level = "Silver"
        level_color = "#64748B"
        level_subtitle = "Analyse expliquée"
        next_level = "Gold"
        next_threshold = 70
        previous_threshold = 30
    elif points < 120:
        level = "Gold"
        level_color = "#D99A18"
        level_subtitle = "Diversification avancée"
        next_level = "Platinum"
        next_threshold = 120
        previous_threshold = 70
    else:
        level = "Platinum"
        level_color = "#7A5CFF"
        level_subtitle = "Rapport personnalisé"
        next_level = "Maximum"
        next_threshold = points
        previous_threshold = 120

    if level == "Platinum":
        progress_pct = 100
        points_to_next = 0
    else:
        progress_pct = ((points - previous_threshold) / (next_threshold - previous_threshold)) * 100
        progress_pct = max(0, min(progress_pct, 100))
        points_to_next = max(next_threshold - points, 0)

    # Badges plus visuels pour renforcer la gamification
    badges = [
        {
            "name": "Explorateur FinPilot",
            "icon": "◆",
            "condition": nb_analyses >= 1,
            "description": "Première analyse IA réalisée.",
            "requirement": "Faire une analyse IA.",
            "reward": "+20 points",
        },
        {
            "name": "Premier Trade",
            "icon": "↗",
            "condition": any(str(o.get("order_type", "")).upper() == "BUY" for o in orders if isinstance(o, dict)),
            "description": "Premier achat simulé enregistré.",
            "requirement": "Simuler un achat dans le portefeuille.",
            "reward": "+15 points",
        },
        {
            "name": "Analyste IA",
            "icon": "AI",
            "condition": nb_analyses >= 3,
            "description": "Utilisation régulière de l’analyse intelligente.",
            "requirement": "Faire 3 analyses IA.",
            "reward": "Badge Silver+",
        },
        {
            "name": "Diversificateur",
            "icon": "3",
            "condition": nb_positions >= 3,
            "description": "Portefeuille réparti sur plusieurs actions.",
            "requirement": "Détenir au moins 3 actions différentes.",
            "reward": "Accès Gold",
        },
        {
            "name": "Ambassadeur",
            "icon": "★",
            "condition": nb_feedbacks >= 1,
            "description": "Avis client déposé pour améliorer FinPilot.",
            "requirement": "Laisser un avis client.",
            "reward": "+10 points",
        },
        {
            "name": "Stratège prudent",
            "icon": "%",
            "condition": cash_balance >= initial_capital * 0.5 if initial_capital > 0 else False,
            "description": "Liquidité conservée à un niveau prudent.",
            "requirement": "Garder au moins 50 % du capital en cash.",
            "reward": "Badge prudence",
        },
    ]

    unlocked_badges = [b for b in badges if b["condition"]]
    locked_badges = [b for b in badges if not b["condition"]]

    return {
        "capital_configured": capital_configured,
        "initial_capital": initial_capital,
        "analyses": analyses,
        "orders": orders,
        "positions": positions,
        "feedbacks": feedbacks,
        "nb_analyses": nb_analyses,
        "nb_orders": nb_orders,
        "nb_positions": nb_positions,
        "nb_feedbacks": nb_feedbacks,
        "points": points,
        "level": level,
        "level_color": level_color,
        "level_subtitle": level_subtitle,
        "next_level": next_level,
        "next_threshold": next_threshold,
        "progress_pct": progress_pct,
        "points_to_next": points_to_next,
        "badges": badges,
        "unlocked_badges": unlocked_badges,
        "locked_badges": locked_badges,
    }


def is_level_unlocked(points: int, threshold: int):
    return points >= threshold


def lock_label(unlocked: bool):
    return "Débloqué" if unlocked else "Verrouillé"


def lock_class(unlocked: bool):
    return "unlocked" if unlocked else "locked"


def next_objective(data):
    if data["level"] == "Bronze":
        return "Réalisez une analyse IA et simulez un premier achat pour débloquer Silver."
    if data["level"] == "Silver":
        return "Réalisez 3 analyses IA, 3 ordres simulés et détenez au moins 2 positions pour débloquer Gold."
    if data["level"] == "Gold":
        return "Complétez 5 analyses IA, 5 ordres simulés et laissez un avis pour débloquer Platinum."
    return "Vous avez atteint le niveau maximal. Vous pouvez continuer à enrichir votre historique FinPilot."


def get_daily_mission(data):
    """Mission visible et actionnable pour rendre la progression plus fun."""
    if data["nb_analyses"] == 0:
        return {
            "title": "Mission du jour",
            "name": "Lancer votre première analyse IA",
            "text": "Répondez au questionnaire investisseur pour découvrir votre profil et gagner vos premiers points.",
            "reward": "+20 points · Badge Explorateur FinPilot",
            "button": "Lancer l’analyse IA",
            "page": "pages/analyse.py",
        }

    if data["nb_orders"] == 0:
        return {
            "title": "Mission du jour",
            "name": "Simuler un premier achat",
            "text": "Choisissez une action dans le portefeuille et testez un achat sans argent réel.",
            "reward": "+15 points · Badge Premier Trade",
            "button": "Simuler un ordre",
            "page": "pages/portefeuille.py",
        }

    if data["nb_positions"] < 3:
        return {
            "title": "Mission du jour",
            "name": "Diversifier le portefeuille",
            "text": "Ajoutez plusieurs positions pour réduire le risque spécifique et progresser vers Gold.",
            "reward": "Badge Diversificateur · Analyse avancée Gold",
            "button": "Voir le portefeuille",
            "page": "pages/portefeuille.py",
        }

    if data["nb_feedbacks"] == 0:
        return {
            "title": "Mission du jour",
            "name": "Partager votre avis",
            "text": "Laissez un retour utilisateur pour contribuer à l’amélioration de FinPilot.",
            "reward": "+10 points · Badge Ambassadeur",
            "button": "Donner un avis",
            "page": "pages/feedback.py",
        }

    return {
        "title": "Mission bonus",
        "name": "Continuer à enrichir votre parcours",
        "text": "Refaites une analyse, comparez les recommandations et améliorez votre portefeuille simulé.",
        "reward": "Historique plus riche · Rapport personnalisé",
        "button": "Nouvelle analyse",
        "page": "pages/analyse.py",
    }


def level_reward(level):
    rewards = {
        "Bronze": "Récompense actuelle : accès au questionnaire, au Top 5 et au portefeuille simulé.",
        "Silver": "Récompense actuelle : explications détaillées des recommandations IA.",
        "Gold": "Récompense actuelle : analyse avancée de diversification du portefeuille.",
        "Platinum": "Récompense actuelle : rapport personnalisé du parcours FinPilot.",
    }
    return rewards.get(level, "Récompense actuelle : parcours FinPilot actif.")


# ============================================================
# SIDEBAR / NAVIGATION
# ============================================================

render_sidebar(
    active_page="progression",
    cash_balance=cash_balance,
    logout_callback=logout,
)


# ============================================================
# STYLE LOCAL
# ============================================================

html(
    """
    <style>
        .block-container {
            padding-top: 0.2rem !important;
        }

        .progression-hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.3rem;
            border-radius: 30px;
            color: white;
            background:
                radial-gradient(circle at 88% 20%, rgba(122,92,255,.55), transparent 24%),
                radial-gradient(circle at 8% 80%, rgba(49,230,168,.20), transparent 25%),
                linear-gradient(120deg, #051633 0%, #0A2D78 52%, #2563EB 100%);
            box-shadow: 0 22px 58px rgba(8,25,70,.24);
            border: 1px solid rgba(255,255,255,.12);
            margin-bottom: 1.2rem;
        }

        .progression-label {
            color: #83EFFF;
            font-size: .86rem;
            font-weight: 900;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .65rem;
            font-family: 'Sora', sans-serif;
        }

        .progression-title {
            font-family: 'Sora', sans-serif;
            font-size: 2.85rem;
            font-weight: 900;
            letter-spacing: -.055em;
            line-height: 1.08;
            margin-bottom: .75rem;
            color: white;
        }

        .progression-subtitle {
            color: rgba(255,255,255,.88);
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 920px;
        }

        .hero-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .7rem;
            margin-top: 1rem;
        }

        .hero-chip {
            background: rgba(255,255,255,.13);
            border: 1px solid rgba(255,255,255,.17);
            color: white;
            border-radius: 999px;
            padding: .55rem .9rem;
            font-size: .9rem;
            font-weight: 800;
        }

        .level-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid #DCE7F8;
            border-radius: 26px;
            padding: 1.45rem;
            box-shadow: 0 16px 38px rgba(22,46,90,.075);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }

        .level-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: var(--level-color);
        }

        .level-small {
            color: #64748B;
            font-size: .82rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-family: 'Sora', sans-serif;
            margin-bottom: .4rem;
        }

        .level-name {
            color: var(--level-color);
            font-family: 'Sora', sans-serif;
            font-size: 2.55rem;
            font-weight: 900;
            letter-spacing: -.05em;
            line-height: 1.05;
        }

        .level-sub {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.6;
            margin-top: .45rem;
        }

        .points-value {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: 2.2rem;
            font-weight: 900;
            line-height: 1.05;
        }

        .progress-track {
            height: 13px;
            background: #E7EEF9;
            border-radius: 999px;
            overflow: hidden;
            margin-top: .8rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2F7CFF, #31E6A8);
            border-radius: 999px;
        }

        .kpi-box {
            border-radius: 24px;
            padding: 1.25rem 1.25rem;
            min-height: 132px;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 34px rgba(30,64,140,.14);
            border: 1px solid rgba(255,255,255,.14);
            margin-bottom: 1rem;
        }

        .kpi-box::after {
            content: "";
            position: absolute;
            width: 118px;
            height: 118px;
            border-radius: 50%;
            right: -42px;
            bottom: -44px;
            background: rgba(255,255,255,.18);
        }

        .kpi-label {
            position: relative;
            z-index: 2;
            color: rgba(255,255,255,.92);
            font-size: .78rem;
            font-weight: 900;
            letter-spacing: .07em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: .55rem;
        }

        .kpi-value {
            position: relative;
            z-index: 2;
            color: white;
            font-family: 'Sora', sans-serif;
            font-size: 2rem;
            font-weight: 900;
            line-height: 1.05;
        }

        .kpi-sub {
            position: relative;
            z-index: 2;
            color: rgba(255,255,255,.88);
            font-size: .9rem;
            line-height: 1.45;
            margin-top: .5rem;
        }

        .section-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid #DCE7F8;
            border-radius: 24px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 14px 34px rgba(22,46,90,.065);
            margin-bottom: 1rem;
        }

        .section-title {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: 1.35rem;
            font-weight: 900;
            line-height: 1.25;
        }

        .section-sub {
            color: #64748B;
            font-size: .96rem;
            line-height: 1.6;
            margin-top: .35rem;
        }

        .roadmap-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .roadmap-card {
            background: #FFFFFF;
            border: 1px solid #DCE7F8;
            border-radius: 22px;
            padding: 1.1rem;
            box-shadow: 0 12px 28px rgba(22,46,90,.06);
            min-height: 245px;
            position: relative;
            overflow: hidden;
        }

        .roadmap-card.unlocked {
            border-color: #A7F3D0;
            background: linear-gradient(180deg, #FFFFFF 0%, #F0FFF8 100%);
        }

        .roadmap-card.locked {
            opacity: .72;
            background: linear-gradient(180deg, #FFFFFF 0%, #F6F8FB 100%);
        }

        .roadmap-status {
            display: inline-block;
            padding: .34rem .7rem;
            border-radius: 999px;
            font-size: .76rem;
            font-weight: 900;
            margin-bottom: .75rem;
        }

        .roadmap-status.unlocked {
            background: #E9FBF5;
            color: #1C9C73;
            border: 1px solid #C5F3E1;
        }

        .roadmap-status.locked {
            background: #F1F5F9;
            color: #64748B;
            border: 1px solid #E2E8F0;
        }

        .roadmap-level {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: 1.3rem;
            font-weight: 900;
            margin-bottom: .35rem;
        }

        .roadmap-points {
            color: #2F7CFF;
            font-size: .9rem;
            font-weight: 900;
            margin-bottom: .7rem;
        }

        .roadmap-text {
            color: #64748B;
            font-size: .92rem;
            line-height: 1.55;
        }

        .roadmap-reward {
            margin-top: .75rem;
            padding: .7rem .75rem;
            border-radius: 15px;
            background: #F4F8FF;
            border: 1px solid #DCE7F8;
            color: #204A7A;
            font-size: .86rem;
            line-height: 1.45;
            font-weight: 700;
        }

        .badge-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .badge-card {
            background: #FFFFFF;
            border: 1px solid #DCE7F8;
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 26px rgba(22,46,90,.055);
            min-height: 158px;
        }

        .badge-card.unlocked {
            background: linear-gradient(180deg, #FFFFFF 0%, #F0FFF8 100%);
            border-color: #A7F3D0;
        }

        .badge-card.locked {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            opacity: .74;
        }

        .badge-icon {
            width: 42px;
            height: 42px;
            border-radius: 15px;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Sora', sans-serif;
            margin-bottom: .7rem;
        }

        .badge-card.locked .badge-icon {
            background: #CBD5E1;
        }

        .badge-title {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: 1.02rem;
            font-weight: 900;
            margin-bottom: .35rem;
        }

        .badge-text {
            color: #64748B;
            font-size: .9rem;
            line-height: 1.5;
        }

        .objective-card {
            background: linear-gradient(135deg, #EAF2FF, #F0FFF8);
            border: 1px solid #CFE0FF;
            border-radius: 24px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 12px 30px rgba(47,124,255,.08);
            margin-bottom: 1rem;
        }

        .objective-title {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: 1.2rem;
            font-weight: 900;
            margin-bottom: .35rem;
        }

        .objective-text {
            color: #405A78;
            font-size: .98rem;
            line-height: 1.65;
        }

        .mission-card {
            position: relative;
            overflow: hidden;
            border-radius: 26px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1rem;
            color: white;
            background:
                radial-gradient(circle at 90% 10%, rgba(255,255,255,.20), transparent 28%),
                linear-gradient(135deg, #0B1D48 0%, #2F7CFF 52%, #31C48D 100%);
            box-shadow: 0 18px 42px rgba(47,124,255,.16);
            border: 1px solid rgba(255,255,255,.15);
        }

        .mission-card::after {
            content: "";
            position: absolute;
            right: -62px;
            bottom: -64px;
            width: 170px;
            height: 170px;
            border-radius: 50%;
            background: rgba(255,255,255,.15);
        }

        .mission-kicker {
            position: relative;
            z-index: 2;
            color: #A7FFF0;
            font-size: .82rem;
            font-weight: 950;
            letter-spacing: .10em;
            text-transform: uppercase;
            font-family: 'Sora', sans-serif;
            margin-bottom: .35rem;
        }

        .mission-title {
            position: relative;
            z-index: 2;
            font-family: 'Sora', sans-serif;
            font-size: 1.55rem;
            font-weight: 950;
            letter-spacing: -.035em;
            line-height: 1.16;
            margin-bottom: .45rem;
            color: white;
        }

        .mission-text {
            position: relative;
            z-index: 2;
            color: rgba(255,255,255,.88);
            font-size: .98rem;
            line-height: 1.6;
            max-width: 860px;
        }

        .mission-reward {
            position: relative;
            z-index: 2;
            display: inline-block;
            margin-top: .9rem;
            padding: .48rem .78rem;
            border-radius: 999px;
            background: rgba(255,255,255,.14);
            border: 1px solid rgba(255,255,255,.18);
            font-size: .86rem;
            font-weight: 900;
            color: white;
        }

        .fun-path {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .8rem;
            margin-bottom: 1rem;
        }

        .fun-step {
            background: #FFFFFF;
            border: 1px solid #DCE7F8;
            border-radius: 18px;
            padding: .95rem;
            box-shadow: 0 10px 24px rgba(22,46,90,.055);
            min-height: 115px;
        }

        .fun-step.active {
            border-color: #9FD8FF;
            background: linear-gradient(180deg, #FFFFFF 0%, #EEF7FF 100%);
            box-shadow: 0 12px 30px rgba(47,124,255,.12);
        }

        .fun-step.locked {
            opacity: .70;
        }

        .fun-step-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .5rem;
            margin-bottom: .55rem;
        }

        .fun-step-icon {
            width: 34px;
            height: 34px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #2F7CFF, #31E6A8);
            color: white;
            font-family: 'Sora', sans-serif;
            font-weight: 950;
        }

        .fun-step-status {
            color: #64748B;
            font-size: .74rem;
            font-weight: 900;
        }

        .fun-step-title {
            color: #10233F;
            font-family: 'Sora', sans-serif;
            font-size: .98rem;
            font-weight: 950;
            margin-bottom: .25rem;
        }

        .fun-step-text {
            color: #64748B;
            font-size: .84rem;
            line-height: 1.42;
        }

        .badge-meta {
            margin-top: .55rem;
            display: inline-block;
            padding: .28rem .55rem;
            border-radius: 999px;
            background: #EEF6FF;
            color: #2F7CFF;
            font-size: .74rem;
            font-weight: 900;
        }

        @media (max-width: 1100px) {
            .roadmap-grid,
            .badge-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 760px) {
            .roadmap-grid,
            .badge-grid {
                grid-template-columns: 1fr;
            }

            .progression-title {
                font-size: 2.2rem;
            }
        }
    </style>
    """
)


# ============================================================
# DATA
# ============================================================

data = calculate_progression(user_id)
points = data["points"]
level = data["level"]
level_color = data["level_color"]
progress_pct = data["progress_pct"]
mission = get_daily_mission(data)


# ============================================================
# HERO
# ============================================================

html(
    f"""
    <div class="progression-hero">
        <div class="progression-label">Parcours FinPilot</div>
        <div class="progression-title">Progressez en apprenant à investir</div>
        <div class="progression-subtitle">
            FinPilot valorise les actions utiles : analyser son profil, simuler des décisions,
            diversifier son portefeuille et contribuer avec un avis. Les niveaux et badges
            sont visibles dès le départ pour guider l’utilisateur.
        </div>
        <div class="hero-chip-row">
            <div class="hero-chip">Niveau actuel : {level}</div>
            <div class="hero-chip">Points : {points}</div>
            <div class="hero-chip">Badges débloqués : {len(data["unlocked_badges"])}/{len(data["badges"])}</div>
            <div class="hero-chip">Prochaine étape : {data["next_level"]}</div>
        </div>
    </div>
    """
)


# ============================================================
# LEVEL SUMMARY
# ============================================================

left, right = st.columns([1.4, 1], gap="large")

with left:
    html(
        f"""
        <div class="level-card" style="--level-color:{level_color};">
            <div class="level-small">Niveau actuel</div>
            <div class="level-name">{level}</div>
            <div class="level-sub">{data["level_subtitle"]}</div>

            <div style="height:1rem;"></div>

            <div class="level-small">Progression vers {data["next_level"]}</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{progress_pct:.1f}%;"></div>
            </div>
            <div class="level-sub">
                Progression : <b>{progress_pct:.1f}%</b>
                {" · Points restants : <b>" + str(data["points_to_next"]) + "</b>" if data["next_level"] != "Maximum" else " · Niveau maximal atteint"}
            </div>
        </div>
        """
    )

with right:
    html(
        f"""
        <div class="level-card" style="--level-color:#2F7CFF;">
            <div class="level-small">Score global</div>
            <div class="points-value">{points} points</div>
            <div class="level-sub">
                Les points sont calculés automatiquement à partir des analyses IA,
                des ordres simulés, des positions et des avis.
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
        <div class="kpi-box" style="background:linear-gradient(135deg,#2F7CFF,#1E5FE6);">
            <div class="kpi-label">Analyses IA</div>
            <div class="kpi-value">{data["nb_analyses"]}</div>
            <div class="kpi-sub">+20 points par analyse</div>
        </div>
        """
    )

with k2:
    html(
        f"""
        <div class="kpi-box" style="background:linear-gradient(135deg,#31C48D,#149D72);">
            <div class="kpi-label">Ordres simulés</div>
            <div class="kpi-value">{data["nb_orders"]}</div>
            <div class="kpi-sub">+15 points par ordre</div>
        </div>
        """
    )

with k3:
    html(
        f"""
        <div class="kpi-box" style="background:linear-gradient(135deg,#7A5CFF,#5E3EEA);">
            <div class="kpi-label">Positions</div>
            <div class="kpi-value">{data["nb_positions"]}</div>
            <div class="kpi-sub">+15 points par position</div>
        </div>
        """
    )

with k4:
    html(
        f"""
        <div class="kpi-box" style="background:linear-gradient(135deg,#FFAE36,#F18A00);">
            <div class="kpi-label">Avis clients</div>
            <div class="kpi-value">{data["nb_feedbacks"]}</div>
            <div class="kpi-sub">+10 points si avis déposé</div>
        </div>
        """
    )


# ============================================================
# MISSION DU JOUR + CHEMIN FUN
# ============================================================

html(
    f"""
    <div class="mission-card">
        <div class="mission-kicker">{mission["title"]}</div>
        <div class="mission-title">{mission["name"]}</div>
        <div class="mission-text">{mission["text"]}</div>
        <div class="mission-reward">Récompense : {mission["reward"]}</div>
    </div>
    """
)

mc1, mc2, mc3 = st.columns([1, 1, 2], gap="medium")
with mc1:
    if st.button(mission["button"], use_container_width=True, type="primary", key="daily_mission_button"):
        st.switch_page(mission["page"])
with mc2:
    if st.button("Voir mes badges", use_container_width=True, key="see_badges_button"):
        st.toast("Descendez pour voir les badges débloqués et verrouillés.")

fun_steps = [
    {"title": "Profil", "icon": "1", "done": data["nb_analyses"] >= 1, "text": "Découvrir votre profil investisseur."},
    {"title": "Simulation", "icon": "2", "done": data["nb_orders"] >= 1, "text": "Tester une décision d’achat ou de vente."},
    {"title": "Diversification", "icon": "3", "done": data["nb_positions"] >= 3, "text": "Répartir le portefeuille sur plusieurs actions."},
    {"title": "Contribution", "icon": "4", "done": data["nb_feedbacks"] >= 1, "text": "Partager un avis pour améliorer FinPilot."},
]

path_html = '<div class="fun-path">'
for step in fun_steps:
    cls = "active" if step["done"] else "locked"
    status = "Terminé" if step["done"] else "À faire"
    path_html += f"""
    <div class="fun-step {cls}">
        <div class="fun-step-top">
            <div class="fun-step-icon">{step['icon']}</div>
            <div class="fun-step-status">{status}</div>
        </div>
        <div class="fun-step-title">{step['title']}</div>
        <div class="fun-step-text">{step['text']}</div>
    </div>
    """
path_html += "</div>"
html(path_html)


# ============================================================
# NEXT OBJECTIVE
# ============================================================

html(
    f"""
    <div class="objective-card">
        <div class="objective-title">Prochain objectif</div>
        <div class="objective-text">{next_objective(data)}<br><b>{level_reward(level)}</b></div>
    </div>
    """
)


# ============================================================
# ROADMAP LEVELS
# ============================================================

html(
    """
    <div class="section-card">
        <div class="section-title">Roadmap des niveaux</div>
        <div class="section-sub">
            Tous les niveaux sont visibles dès le début. Les options avancées apparaissent comme
            verrouillées tant que les conditions ne sont pas remplies.
        </div>
    </div>
    """
)

levels = [
    {
        "name": "Bronze",
        "threshold": 0,
        "points": "0 point",
        "description": "Découverte de l’application et configuration du capital.",
        "reward": "Questionnaire investisseur, Top 5, portefeuille simulé et historique simple.",
    },
    {
        "name": "Silver",
        "threshold": 30,
        "points": "30 points",
        "description": "Premières analyses et premières simulations.",
        "reward": "Débloque les explications détaillées des recommandations IA.",
    },
    {
        "name": "Gold",
        "threshold": 70,
        "points": "70 points",
        "description": "Usage régulier et construction d’un portefeuille plus complet.",
        "reward": "Débloque l’analyse avancée de diversification.",
    },
    {
        "name": "Platinum",
        "threshold": 120,
        "points": "120 points",
        "description": "Parcours complet avec analyses, ordres, avis et historique riche.",
        "reward": "Débloque le rapport personnalisé FinPilot.",
    },
]

roadmap_html = '<div class="roadmap-grid">'

for item in levels:
    unlocked = is_level_unlocked(points, item["threshold"])
    roadmap_html += f"""
    <div class="roadmap-card {lock_class(unlocked)}">
        <span class="roadmap-status {lock_class(unlocked)}">{lock_label(unlocked)}</span>
        <div class="roadmap-level">{item["name"]}</div>
        <div class="roadmap-points">{item["points"]}</div>
        <div class="roadmap-text">{item["description"]}</div>
        <div class="roadmap-reward"><b>Option :</b> {item["reward"]}</div>
    </div>
    """

roadmap_html += "</div>"
html(roadmap_html)


# ============================================================
# BADGES
# ============================================================

html(
    """
    <div class="section-card">
        <div class="section-title">Badges FinPilot</div>
        <div class="section-sub">
            Les badges valorisent les étapes importantes du parcours utilisateur.
        </div>
    </div>
    """
)

badge_html = '<div class="badge-grid">'

for badge in data["badges"]:
    unlocked = badge["condition"]

    if unlocked:
        status_text = badge["description"]
    else:
        status_text = f"À débloquer : {badge['requirement']}"

    badge_icon = badge.get("icon", "✓") if unlocked else "🔒"
    badge_html += f"""
    <div class="badge-card {lock_class(unlocked)}">
        <div class="badge-icon">{badge_icon}</div>
        <div class="badge-title">{badge["name"]}</div>
        <div class="badge-text">{status_text}</div>
        <div class="badge-meta">{badge.get("reward", "Récompense")}</div>
    </div>
    """

badge_html += "</div>"
html(badge_html)


# ============================================================
# OPTIONS UNLOCKED / LOCKED
# ============================================================

html(
    """
    <div class="section-card">
        <div class="section-title">Options débloquées et verrouillées</div>
        <div class="section-sub">
            Cette section rend la gamification transparente : l’utilisateur voit ce qu’il possède déjà
            et ce qu’il peut débloquer ensuite.
        </div>
    </div>
    """
)

silver_unlocked = points >= 30
gold_unlocked = points >= 70
platinum_unlocked = points >= 120

options_html = f"""
<div class="roadmap-grid">
    <div class="roadmap-card unlocked">
        <span class="roadmap-status unlocked">Débloqué</span>
        <div class="roadmap-level">Analyse basique</div>
        <div class="roadmap-text">
            Questionnaire investisseur, score de profil, Top 5 et simulation de portefeuille.
        </div>
    </div>

    <div class="roadmap-card {lock_class(silver_unlocked)}">
        <span class="roadmap-status {lock_class(silver_unlocked)}">{lock_label(silver_unlocked)}</span>
        <div class="roadmap-level">Explications détaillées</div>
        <div class="roadmap-text">
            Comprendre pourquoi chaque action est recommandée : forces, limites et adéquation au profil.
        </div>
    </div>

    <div class="roadmap-card {lock_class(gold_unlocked)}">
        <span class="roadmap-status {lock_class(gold_unlocked)}">{lock_label(gold_unlocked)}</span>
        <div class="roadmap-level">Diversification avancée</div>
        <div class="roadmap-text">
            Score de diversification, alerte de concentration et conseils d’équilibrage.
        </div>
    </div>

    <div class="roadmap-card {lock_class(platinum_unlocked)}">
        <span class="roadmap-status {lock_class(platinum_unlocked)}">{lock_label(platinum_unlocked)}</span>
        <div class="roadmap-level">Rapport personnalisé</div>
        <div class="roadmap-text">
            Synthèse du parcours : profil dominant, décisions, recommandations et progression.
        </div>
    </div>
</div>
"""

html(options_html)