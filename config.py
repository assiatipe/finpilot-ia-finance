# =============================================================================
# config.py — Constantes globales du projet
# Projet : IA et Marchés Financiers — EMI 2025-2026
# =============================================================================

# ─── Paramètres temporels ─────────────────────────────────────────────────────
HISTORIQUE_ANNEES = 3
JOURS_BOURSE_PAR_AN = 252

# ─── Taux sans risque ─────────────────────────────────────────────────────────
TICKER_TAUX_SANS_RISQUE = "^IRX"   # Bon du Trésor US 3 mois
TAUX_SANS_RISQUE_DEFAUT = 0.05     # 5 % si récupération impossible

# ─── Indice de référence pour le bêta ────────────────────────────────────────
TICKER_INDICE = "^DJI"             # Dow Jones Industrial Average

# ─── Univers d’analyse : actions du DJIA ─────────────────────────────────────
DJIA_ACTIONS = {
    "AAPL": ("Apple Inc.", "Technologie"),
    "AMGN": ("Amgen Inc.", "Santé"),
    "AXP": ("American Express Co.", "Finance"),
    "BA": ("Boeing Co.", "Industrie"),
    "CAT": ("Caterpillar Inc.", "Industrie"),
    "CRM": ("Salesforce Inc.", "Technologie"),
    "CSCO": ("Cisco Systems Inc.", "Technologie"),
    "CVX": ("Chevron Corp.", "Énergie"),
    "DIS": ("Walt Disney Co.", "Consommation discrétionnaire"),
    "DOW": ("Dow Inc.", "Matériaux"),
    "GS": ("Goldman Sachs Group Inc.", "Finance"),
    "HD": ("Home Depot Inc.", "Consommation discrétionnaire"),
    "HON": ("Honeywell International Inc.", "Industrie"),
    "IBM": ("IBM Corp.", "Technologie"),
    "INTC": ("Intel Corp.", "Technologie"),
    "JNJ": ("Johnson & Johnson", "Santé"),
    "JPM": ("JPMorgan Chase & Co.", "Finance"),
    "KO": ("Coca-Cola Co.", "Consommation de base"),
    "MCD": ("McDonald's Corp.", "Consommation discrétionnaire"),
    "MMM": ("3M Co.", "Industrie"),
    "MRK": ("Merck & Co. Inc.", "Santé"),
    "MSFT": ("Microsoft Corp.", "Technologie"),
    "NKE": ("Nike Inc.", "Consommation discrétionnaire"),
    "PG": ("Procter & Gamble Co.", "Consommation de base"),
    "TRV": ("Travelers Companies Inc.", "Finance"),
    "UNH": ("UnitedHealth Group Inc.", "Santé"),
    "V": ("Visa Inc.", "Finance"),
    "VZ": ("Verizon Communications Inc.", "Télécommunications"),
    "WMT": ("Walmart Inc.", "Consommation de base"),
    "NVDA": ("NVIDIA Corp.", "Technologie"),
}

TICKERS = list(DJIA_ACTIONS.keys())
NOMS = {ticker: infos[0] for ticker, infos in DJIA_ACTIONS.items()}
SECTEURS = {ticker: infos[1] for ticker, infos in DJIA_ACTIONS.items()}

# ─── Pondérations par profil (cohérentes avec le rapport) ───────────────────
PONDERATIONS = {
    "Prudent": {
        "w_sigma": 0.40,
        "w_beta": 0.35,
        "w_sharpe": 0.15,
        "w_rendement": 0.10,
    },
    "Modéré": {
        "w_sigma": 0.25,
        "w_beta": 0.25,
        "w_sharpe": 0.25,
        "w_rendement": 0.25,
    },
    "Dynamique": {
        "w_sigma": 0.10,
        "w_beta": 0.10,
        "w_sharpe": 0.35,
        "w_rendement": 0.45,
    },
}

# ─── Horizon investisseur ────────────────────────────────────────────────────
HORIZONS = {
    "Court terme (< 1 an)": "court",
    "Moyen terme (1 à 3 ans)": "moyen",
    "Long terme (> 3 ans)": "long",
}

# ─── Paramètres d’affichage ──────────────────────────────────────────────────
TOP_N = 5

# ─── Qualité des données ─────────────────────────────────────────────────────
SEUIL_NAN = 0.05   # 5 % maximum de données manquantes
MIN_OBSERVATIONS = 200
LISTE_SECTEURS = sorted(list(set(SECTEURS.values())))