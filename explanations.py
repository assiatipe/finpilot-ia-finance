# =============================================================================
# explanations.py — Génération de justifications textuelles améliorées
# =============================================================================

from config import PONDERATIONS


def generer_justification(ticker: str, ligne, profil: str) -> str:
    """
    Génère une justification textuelle plus naturelle et adaptée au profil.
    """
    poids = PONDERATIONS[profil]

    sigma_n = ligne["sigma_norm"]
    beta_n = ligne["beta_norm"]
    sharpe_n = ligne["sharpe_norm"]
    rendement_n = ligne["rendement_norm"]
    score = ligne["score"]

    phrases = []

    # -------------------------------------------------------------------------
    # Introduction adaptée au profil
    # -------------------------------------------------------------------------
    if profil == "Prudent":
        phrases.append(
            f"L’action {ticker} ressort comme une option plutôt défensive pour un profil prudent."
        )
    elif profil == "Modéré":
        phrases.append(
            f"L’action {ticker} présente un compromis intéressant pour un profil modéré."
        )
    else:
        phrases.append(
            f"L’action {ticker} se distingue par un potentiel plus offensif, cohérent avec un profil dynamique."
        )

    # -------------------------------------------------------------------------
    # Analyse de la volatilité
    # -------------------------------------------------------------------------
    if poids["w_sigma"] >= 0.25:
        if sigma_n > 0.75:
            phrases.append(
                "Sa volatilité est bien maîtrisée, ce qui renforce sa compatibilité avec une recherche de stabilité."
            )
        elif sigma_n > 0.45:
            phrases.append(
                "Sa volatilité reste modérée, ce qui permet de contenir le risque sans l’éliminer totalement."
            )
        else:
            phrases.append(
                "Sa volatilité est relativement élevée, ce qui limite son attractivité pour un investisseur sensible au risque."
            )

    # -------------------------------------------------------------------------
    # Analyse du bêta
    # -------------------------------------------------------------------------
    if poids["w_beta"] >= 0.25:
        if beta_n > 0.75:
            phrases.append(
                "Son bêta indique une sensibilité modérée aux mouvements du marché."
            )
        elif beta_n > 0.45:
            phrases.append(
                "Son bêta reste acceptable au regard du profil sélectionné."
            )
        else:
            phrases.append(
                "Son bêta traduit une sensibilité marquée au marché, ce qui pénalise son classement."
            )

    # -------------------------------------------------------------------------
    # Analyse du ratio de Sharpe
    # -------------------------------------------------------------------------
    if poids["w_sharpe"] >= 0.25:
        if sharpe_n > 0.75:
            phrases.append(
                "Son ratio de Sharpe est élevé, ce qui reflète une bonne performance ajustée au risque."
            )
        elif sharpe_n > 0.45:
            phrases.append(
                "Son ratio de Sharpe est correct, avec une performance ajustée au risque globalement satisfaisante."
            )
        else:
            phrases.append(
                "Son ratio de Sharpe demeure limité, ce qui réduit l’intérêt de l’action en termes de performance ajustée au risque."
            )

    # -------------------------------------------------------------------------
    # Analyse du rendement
    # -------------------------------------------------------------------------
    if poids["w_rendement"] >= 0.25:
        if rendement_n > 0.75:
            phrases.append(
                "Son rendement historique figure parmi les plus solides de l’univers analysé."
            )
        elif rendement_n > 0.45:
            phrases.append(
                "Son rendement historique est convenable, sans toutefois se situer parmi les plus élevés."
            )
        else:
            phrases.append(
                "Son rendement historique reste relativement modeste par rapport aux autres actions étudiées."
            )

    # -------------------------------------------------------------------------
    # Conclusion
    # -------------------------------------------------------------------------
    if score >= 80:
        conclusion = f"Au final, son score de {score:.2f}/100 confirme une très bonne adéquation avec le profil sélectionné."
    elif score >= 65:
        conclusion = f"Au final, son score de {score:.2f}/100 traduit une compatibilité solide avec le profil sélectionné."
    elif score >= 50:
        conclusion = f"Au final, son score de {score:.2f}/100 montre une compatibilité moyenne mais exploitable selon les préférences de l’utilisateur."
    else:
        conclusion = f"Au final, son score de {score:.2f}/100 indique une compatibilité plus limitée avec le profil retenu."

    phrases.append(conclusion)

    return " ".join(phrases)