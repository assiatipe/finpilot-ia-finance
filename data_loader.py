# =============================================================================
# data_loader.py — Collecte des données de marché via yfinance
# =============================================================================

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from config import (
    HISTORIQUE_ANNEES,
    TICKER_INDICE,
    TICKER_TAUX_SANS_RISQUE,
    TICKERS,
    TAUX_SANS_RISQUE_DEFAUT,
    SEUIL_NAN,
    MIN_OBSERVATIONS,
)


def calculer_dates():
    """Retourne la date de début et de fin pour le téléchargement."""
    fin = datetime.today()
    debut = fin - timedelta(days=HISTORIQUE_ANNEES * 365 + 5)
    return debut.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d")


def extraire_close(df_brut):
    """
    Extrait la colonne Close d'un téléchargement yfinance.
    Gère le cas multi-tickers et mono-ticker.
    """
    if isinstance(df_brut.columns, pd.MultiIndex):
        if "Close" in df_brut.columns.get_level_values(0):
            return df_brut["Close"]
        raise ValueError("La colonne 'Close' est introuvable.")
    else:
        if "Close" in df_brut.columns:
            return df_brut[["Close"]]
        raise ValueError("La colonne 'Close' est introuvable.")


def recuperer_taux_sans_risque():
    """
    Télécharge ^IRX et retourne le dernier taux disponible en décimal.
    Exemple : 4.9 % -> 0.049
    """
    try:
        debut, fin = calculer_dates()
        brut = yf.download(
            TICKER_TAUX_SANS_RISQUE,
            start=debut,
            end=fin,
            progress=False,
        )
        close = extraire_close(brut)

        if close.empty:
            return TAUX_SANS_RISQUE_DEFAUT

        taux = float(close.iloc[-1].values[0]) / 100.0
        return taux

    except Exception:
        return TAUX_SANS_RISQUE_DEFAUT


def verifier_qualite(df):
    """
    Nettoie les données :
    - supprime colonnes vides
    - exclut les tickers avec trop de NaN
    - exclut les historiques trop courts
    - remplit les petits trous
    """
    rapport = {
        "tickers_initiaux": list(df.columns),
        "tickers_exclus_nan": [],
        "tickers_exclus_court": [],
        "tickers_retenus": [],
        "nb_observations": len(df),
    }

    # supprimer colonnes entièrement vides
    df = df.dropna(axis=1, how="all")

    # exclure tickers avec trop de NaN
    taux_nan = df.isnull().mean()
    exclus_nan = [col for col in df.columns if taux_nan[col] > SEUIL_NAN]
    rapport["tickers_exclus_nan"] = exclus_nan
    df = df.drop(columns=exclus_nan, errors="ignore")

    # exclure tickers avec historique trop court
    exclus_courts = [col for col in df.columns if df[col].dropna().shape[0] < MIN_OBSERVATIONS]
    rapport["tickers_exclus_court"] = exclus_courts
    df = df.drop(columns=exclus_courts, errors="ignore")

    # compléter petits trous
    df = df.ffill().bfill()

    # dates propres
    df = df[~df.index.duplicated(keep="first")]
    df = df.sort_index()

    rapport["tickers_retenus"] = list(df.columns)
    rapport["nb_observations"] = len(df)

    return df, rapport


def charger_donnees():
    """
    Télécharge :
    - prix des actions du DJIA
    - indice de référence ^DJI
    - taux sans risque ^IRX

    Retourne :
    df_prix, df_indice, rf_annuel, rapport
    """
    debut, fin = calculer_dates()

    # actions
    brut_actions = yf.download(
        TICKERS,
        start=debut,
        end=fin,
        auto_adjust=True,
        progress=False,
    )
    df_prix = extraire_close(brut_actions)

    # indice
    brut_indice = yf.download(
        TICKER_INDICE,
        start=debut,
        end=fin,
        auto_adjust=True,
        progress=False,
    )
    df_indice = extraire_close(brut_indice)
    df_indice.columns = [TICKER_INDICE]

    # nettoyage actions
    df_prix, rapport = verifier_qualite(df_prix)

    # aligner les dates entre actions et indice
    dates_communes = df_prix.index.intersection(df_indice.index)
    df_prix = df_prix.loc[dates_communes]
    df_indice = df_indice.loc[dates_communes]

    # taux sans risque
    rf_annuel = recuperer_taux_sans_risque()

    return df_prix, df_indice, rf_annuel, rapport