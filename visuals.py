import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def graphique_scores(df_scores: pd.DataFrame):
    df_plot = df_scores.copy().sort_values("score", ascending=False)

    fig = px.bar(
        df_plot,
        x=df_plot.index,
        y="score",
        color="secteur" if "secteur" in df_plot.columns else None,
        title="Distribution des scores par action",
    )

    fig.update_layout(
        height=430,
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.02,
        xaxis_title="Ticker",
        yaxis_title="Score",
        font=dict(size=12, color="#0F172A"),
        legend_title_text="Secteur",
        margin=dict(l=30, r=30, t=60, b=40),
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E2E8F0")

    return fig


def graphique_top5(df_scores: pd.DataFrame, top_n: int = 5):
    df_top = df_scores.sort_values("score", ascending=False).head(top_n).copy()
    df_top = df_top.sort_values("score", ascending=True)

    fig = px.bar(
        df_top,
        x="score",
        y=df_top.index,
        orientation="h",
        color="secteur" if "secteur" in df_top.columns else None,
        title="Top des actions recommandées",
    )

    fig.update_layout(
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.02,
        xaxis_title="Score",
        yaxis_title="Ticker",
        font=dict(size=12, color="#0F172A"),
        legend_title_text="Secteur",
        margin=dict(l=30, r=30, t=60, b=40),
    )

    fig.update_xaxes(gridcolor="#E2E8F0")
    fig.update_yaxes(showgrid=False)

    return fig


def graphique_prix_historique(df_prix: pd.DataFrame, ticker: str, nom: str = None):
    if ticker not in df_prix.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Historique indisponible",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        return fig

    titre = f"Historique du prix — {ticker}"
    if nom:
        titre += f" ({nom})"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_prix.index,
        y=df_prix[ticker],
        mode="lines",
        name=ticker,
        line=dict(width=2.5, color="#1E40AF")
    ))

    fig.update_layout(
        title=titre,
        title_x=0.02,
        height=460,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Date",
        yaxis_title="Prix ajusté",
        font=dict(size=12, color="#0F172A"),
        margin=dict(l=30, r=30, t=60, b=40),
        showlegend=False,
    )

    fig.update_xaxes(gridcolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#E2E8F0")

    return fig


def graphique_radar_top(df_scores: pd.DataFrame, selected_tickers=None):
    if selected_tickers is None:
        selected_tickers = df_scores.index.tolist()[:3]

    radar_df = df_scores.loc[selected_tickers, [
        "rendement_annuel",
        "volatilite_annuelle",
        "beta",
        "sharpe"
    ]].copy()

    base = df_scores[[
        "rendement_annuel",
        "volatilite_annuelle",
        "beta",
        "sharpe"
    ]].copy()

    normalized = pd.DataFrame(index=radar_df.index)

    r_min, r_max = base["rendement_annuel"].min(), base["rendement_annuel"].max()
    if r_max != r_min:
        normalized["Rendement"] = (radar_df["rendement_annuel"] - r_min) / (r_max - r_min)
    else:
        normalized["Rendement"] = 0.5

    v_min, v_max = base["volatilite_annuelle"].min(), base["volatilite_annuelle"].max()
    if v_max != v_min:
        vol_norm = (radar_df["volatilite_annuelle"] - v_min) / (v_max - v_min)
    else:
        vol_norm = 0.5
    normalized["Volatilité"] = 1 - vol_norm

    b_min, b_max = base["beta"].min(), base["beta"].max()
    if b_max != b_min:
        beta_norm = (radar_df["beta"] - b_min) / (b_max - b_min)
    else:
        beta_norm = 0.5
    normalized["Bêta"] = 1 - beta_norm

    s_min, s_max = base["sharpe"].min(), base["sharpe"].max()
    if s_max != s_min:
        normalized["Sharpe"] = (radar_df["sharpe"] - s_min) / (s_max - s_min)
    else:
        normalized["Sharpe"] = 0.5

    categories = ["Rendement", "Volatilité", "Bêta", "Sharpe"]
    colors = ["#1E40AF", "#0F766E", "#B45309", "#BE123C", "#7C3AED"]

    fig = go.Figure()

    for i, ticker in enumerate(normalized.index):
        values = normalized.loc[ticker, categories].tolist()
        values += [values[0]]
        cats = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill="toself",
            name=ticker,
            line=dict(width=3, color=colors[i % len(colors)]),
            opacity=0.22,
            marker=dict(size=7, color=colors[i % len(colors)]),
            hovertemplate=(
                f"<b>{ticker}</b><br>"
                "Indicateur: %{theta}<br>"
                "Score normalisé: %{r:.2f}<extra></extra>"
            )
        ))

    fig.update_layout(
        title="Comparaison radar des actions sélectionnées",
        title_x=0.02,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=11),
                gridcolor="#DCE3EE",
                linecolor="#DCE3EE"
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color="#0F172A"),
                gridcolor="#E5EAF2",
                linecolor="#E5EAF2"
            ),
            bgcolor="white"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="left",
            x=0
        ),
        margin=dict(l=40, r=40, t=90, b=40),
        height=560,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=12, color="#0F172A")
    )

    return fig