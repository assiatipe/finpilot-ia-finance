# =============================================================================
# indicators.py — Calcul des indicateurs financiers
# =============================================================================

import numpy as np
import pandas as pd

from config import JOURS_BOURSE_PAR_AN


def calculer_rendements(df_prix: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les rendements journaliers simples.
    """
    return df_prix.pct_change().dropna()


def calculer_rendement_moyen_annuel(df_rendements: pd.DataFrame) -> pd.Series:
    """
    Rendement moyen annualisé :
    moyenne journalière × nombre de jours de bourse
    """
    return df_rendements.mean() * JOURS_BOURSE_PAR_AN


def calculer_volatilite_annuelle(df_rendements: pd.DataFrame) -> pd.Series:
    """
    Volatilité annualisée :
    écart-type journalier × racine(252)
    """
    return df_rendements.std() * np.sqrt(JOURS_BOURSE_PAR_AN)


def calculer_beta(df_rendements_actions: pd.DataFrame, rendements_indice: pd.Series) -> pd.Series:
    """
    Calcule le bêta de chaque action par rapport à l’indice de référence.
    """
    variance_marche = rendements_indice.var()

    betas = {}
    for ticker in df_rendements_actions.columns:
        covariance = df_rendements_actions[ticker].cov(rendements_indice)
        beta = covariance / variance_marche if variance_marche != 0 else np.nan
        betas[ticker] = beta

    return pd.Series(betas)


def calculer_sharpe(
    rendement_moyen_annuel: pd.Series,
    volatilite_annuelle: pd.Series,
    taux_sans_risque: float
) -> pd.Series:
    """
    Ratio de Sharpe :
    (R_i - R_f) / sigma_i
    """
    sharpe = (rendement_moyen_annuel - taux_sans_risque) / volatilite_annuelle
    return sharpe.replace([np.inf, -np.inf], np.nan)


def calculer_indicateurs(
    df_prix: pd.DataFrame,
    df_indice: pd.DataFrame,
    taux_sans_risque: float
) -> pd.DataFrame:
    """
    Fonction principale :
    retourne un DataFrame avec les 4 indicateurs du projet
    """
    # Rendements journaliers
    rendements_actions = calculer_rendements(df_prix)
    rendements_indice = calculer_rendements(df_indice).iloc[:, 0]

    # Aligner encore une fois les dates au cas où
    dates_communes = rendements_actions.index.intersection(rendements_indice.index)
    rendements_actions = rendements_actions.loc[dates_communes]
    rendements_indice = rendements_indice.loc[dates_communes]

    # Calculs
    rendement_annuel = calculer_rendement_moyen_annuel(rendements_actions)
    volatilite_annuelle = calculer_volatilite_annuelle(rendements_actions)
    beta = calculer_beta(rendements_actions, rendements_indice)
    sharpe = calculer_sharpe(rendement_annuel, volatilite_annuelle, taux_sans_risque)

    # Tableau final
    df_indicateurs = pd.DataFrame({
        "rendement_annuel": rendement_annuel,
        "volatilite_annuelle": volatilite_annuelle,
        "beta": beta,
        "sharpe": sharpe,
    })

    return df_indicateurs.sort_index()