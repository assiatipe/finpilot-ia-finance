def get_history_summary(history_rows: list, recommended_rows: list) -> dict:
    """Summarize analysis history to extract dominant profile and insights."""
    profil_dominant = None
    score_moyen = 0

    if history_rows:
        profiles = [r.get("profil") or r["profil"] for r in history_rows if r]
        if profiles:
            profil_dominant = max(set(profiles), key=profiles.count)
        scores = [r.get("score", 0) for r in history_rows if r]
        score_moyen = sum(scores) / len(scores) if scores else 0

    return {
        "profil_dominant": profil_dominant,
        "score_moyen": round(score_moyen, 1),
        "nb_analyses": len(history_rows),
        "nb_recommended": len(recommended_rows),
    }


def format_currency(value: float, symbol: str = "$") -> str:
    """Format a float as currency string."""
    if value >= 1_000_000:
        return f"{symbol}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{symbol}{value:,.2f}"
    else:
        return f"{symbol}{value:.2f}"


def format_pct(value: float, sign: bool = True) -> str:
    """Format a float as percentage string."""
    prefix = "+" if sign and value >= 0 else ""
    return f"{prefix}{value:.2f}%"


def get_profile_color(profil: str) -> str:
    colors = {
        "Prudent": "#31E6A8",
        "Modéré": "#2F7CFF",
        "Dynamique": "#F3C969",
    }
    return colors.get(profil, "#2F7CFF")


def get_risk_score(profil: str) -> int:
    scores = {
        "Prudent": 35,
        "Modéré": 65,
        "Dynamique": 82,
    }
    return scores.get(profil, 65)