# =============================================================================
# scoring.py — Normalisation et calcul du score MCDA
# =============================================================================

import pandas as pd

from config import PONDERATIONS


def normalisation_min_max(serie: pd.Series) -> pd.Series:
    """
    Normalisation min-max classique sur [0, 1].
    """
    min_val = serie.min()
    max_val = serie.max()

    if max_val == min_val:
        return pd.Series(1.0, index=serie.index)

    return (serie - min_val) / (max_val - min_val)


def normalisation_inversee(serie: pd.Series) -> pd.Series:
    """
    Normalisation min-max inversée sur [0, 1].
    Utile quand une faible valeur est meilleure (sigma, beta).
    """
    min_val = serie.min()
    max_val = serie.max()

    if max_val == min_val:
        return pd.Series(1.0, index=serie.index)

    return 1 - (serie - min_val) / (max_val - min_val)


def normaliser_indicateurs(df_indicateurs: pd.DataFrame) -> pd.DataFrame:
    """
    Retourne un DataFrame avec les indicateurs normalisés.
    """
    df = df_indicateurs.copy()

    df["rendement_norm"] = normalisation_min_max(df["rendement_annuel"])
    df["sharpe_norm"] = normalisation_min_max(df["sharpe"])

    df["sigma_norm"] = normalisation_inversee(df["volatilite_annuelle"])
    df["beta_norm"] = normalisation_inversee(df["beta"])

    return df


def calculer_score(df_indicateurs: pd.DataFrame, profil: str) -> pd.DataFrame:
    """
    Calcule le score final MCDA selon le profil investisseur.
    """
    if profil not in PONDERATIONS:
        raise ValueError(f"Profil inconnu : {profil}")

    poids = PONDERATIONS[profil]
    df = normaliser_indicateurs(df_indicateurs)

    df["score"] = 100 * (
        poids["w_sigma"] * df["sigma_norm"]
        + poids["w_beta"] * df["beta_norm"]
        + poids["w_sharpe"] * df["sharpe_norm"]
        + poids["w_rendement"] * df["rendement_norm"]
    )

    df["score"] = df["score"].round(2)

    df = df.sort_values(by="score", ascending=False).copy()
    df["rang"] = range(1, len(df) + 1)

    return df