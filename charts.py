"""
charts.py — All 10 chart functions for the IMDB Movies Analytics Dashboard
Uses Matplotlib and Seaborn with a cinema / IMDB colour theme.

Cinema colour palette
---------------------
  IMDB_RED    = #E50914   (Netflix-style red  — accents, highlights)
  IMDB_YELLOW = #F5C518   (IMDB gold          — primary bars / lines)
  BG_DARK     = #1a1a2e   (dark navy          — figure background)
  BG_CARD     = #16213e   (slightly lighter   — axes background)
  TEXT_LIGHT  = #e0e0e0   (off-white          — labels / ticks)
  TEXT_DIM    = #a0a0b0   (muted              — grid / minor text)
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ── Global theme constants ─────────────────────────────────────────────────

IMDB_RED    = "#E50914"
IMDB_YELLOW = "#F5C518"
BG_DARK     = "#1a1a2e"
BG_CARD     = "#16213e"
TEXT_LIGHT  = "#e0e0e0"
TEXT_DIM    = "#a0a0b0"
GRID_COLOR  = "#2e2e4e"

# A palette of 8 cinema-inspired accent colours used in multi-series charts
CINEMA_PALETTE = [
    IMDB_YELLOW, IMDB_RED, "#00d4ff", "#ff6b35",
    "#7bc67e", "#c77dff", "#ff9f1c", "#2ec4b6",
]

# Apply a global dark style once at import time
plt.rcParams.update({
    "figure.facecolor":  BG_DARK,
    "axes.facecolor":    BG_CARD,
    "axes.edgecolor":    GRID_COLOR,
    "axes.labelcolor":   TEXT_LIGHT,
    "axes.titlecolor":   TEXT_LIGHT,
    "xtick.color":       TEXT_DIM,
    "ytick.color":       TEXT_DIM,
    "grid.color":        GRID_COLOR,
    "grid.linewidth":    0.6,
    "text.color":        TEXT_LIGHT,
    "legend.facecolor":  BG_CARD,
    "legend.edgecolor":  GRID_COLOR,
    "legend.labelcolor": TEXT_LIGHT,
    "font.size":         10,
    "axes.titlesize":    13,
    "axes.labelsize":    10,
})


# ── Helper ─────────────────────────────────────────────────────────────────

def _new_fig(w=8, h=4.5):
    """Create a new figure with the cinema background."""
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_CARD)
    return fig, ax


def _style_ax(ax, title, xlabel="", ylabel="", grid_axis="y"):
    """Apply consistent styling to an axes object."""
    ax.set_title(title, fontsize=13, fontweight="bold",
                 color=TEXT_LIGHT, pad=12)
    ax.set_xlabel(xlabel, color=TEXT_LIGHT, labelpad=6)
    ax.set_ylabel(ylabel, color=TEXT_LIGHT, labelpad=6)
    ax.tick_params(colors=TEXT_DIM)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID_COLOR, linewidth=0.6, alpha=0.7)
    plt.tight_layout(pad=1.5)


# ══════════════════════════════════════════════════════════════════════════════
# Chart 1 — Genre Distribution Pie Chart
# ══════════════════════════════════════════════════════════════════════════════

def chart_genre_pie(df: pd.DataFrame):
    """
    Pie chart showing the proportion of movies across the top 8 genres.
    Returns a Matplotlib Figure.
    """
    top8 = df["genre"].value_counts().nlargest(8)
    if top8.empty:
        return _empty_chart("No genre data available.")

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)

    wedges, texts, autotexts = ax.pie(
        top8.values,
        labels=top8.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=CINEMA_PALETTE,
        wedgeprops={"edgecolor": BG_DARK, "linewidth": 1.5},
        pctdistance=0.82,
    )
    for t in texts:
        t.set_color(TEXT_LIGHT)
        t.set_fontsize(9)
    for at in autotexts:
        at.set_color(BG_DARK)
        at.set_fontsize(8)
        at.set_fontweight("bold")

    ax.set_title("🎭  Genre Distribution (Top 8)", fontsize=13,
                 fontweight="bold", color=TEXT_LIGHT, pad=14)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 2 — Rating Distribution Histogram
# ══════════════════════════════════════════════════════════════════════════════

def chart_rating_histogram(df: pd.DataFrame):
    """
    Histogram of IMDB ratings with a KDE overlay.
    Returns a Matplotlib Figure.
    """
    ratings = df["rating"].dropna()
    if ratings.empty:
        return _empty_chart("No rating data available.")

    fig, ax = _new_fig(8, 4.5)
    ax.hist(ratings, bins=30, color=IMDB_YELLOW, edgecolor=BG_DARK,
            alpha=0.85, density=True, label="Frequency")

    # KDE overlay
    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(ratings)
        xs = np.linspace(ratings.min(), ratings.max(), 300)
        ax.plot(xs, kde(xs), color=IMDB_RED, linewidth=2.2, label="KDE")
    except Exception:
        pass  # scipy optional

    ax.axvline(ratings.mean(), color="#ffffff", linewidth=1.2,
               linestyle="--", label=f"Mean = {ratings.mean():.2f}")
    ax.legend()
    _style_ax(ax, "⭐  Distribution of Movie Ratings",
              "Rating (0–10)", "Density")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 3 — Average Rating Trend by Year (Line Chart)
# ══════════════════════════════════════════════════════════════════════════════

def chart_rating_trend(df: pd.DataFrame):
    """
    Line chart showing the average IMDB rating for each release year.
    Returns a Matplotlib Figure.
    """
    yearly = (
        df.dropna(subset=["rating", "year"])
          .groupby("year")["rating"]
          .agg(["mean", "count"])
          .reset_index()
    )
    yearly = yearly[yearly["count"] >= 3]   # filter noisy years
    if yearly.empty:
        return _empty_chart("Not enough year data to plot trend.")

    fig, ax = _new_fig(9, 4.5)
    ax.plot(yearly["year"], yearly["mean"],
            color=IMDB_YELLOW, linewidth=2.2, marker="o",
            markersize=4, markerfacecolor=IMDB_RED)
    ax.fill_between(yearly["year"], yearly["mean"],
                    alpha=0.15, color=IMDB_YELLOW)
    _style_ax(ax, "📈  Average Rating Trend by Year",
              "Year", "Average Rating")
    ax.set_ylim(bottom=0)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 4 — Top 10 Directors by Average Rating (Bar Chart)
# ══════════════════════════════════════════════════════════════════════════════

def chart_top_directors(df: pd.DataFrame):
    """
    Horizontal bar chart of the top 10 directors by mean IMDB rating
    (requiring at least 3 films).
    Returns a Matplotlib Figure.
    """
    dir_stats = (
        df[df["director"] != "Unknown"]
          .dropna(subset=["rating"])
          .groupby("director")["rating"]
          .agg(["mean", "count"])
          .query("count >= 3")
          .nlargest(10, "mean")
          .sort_values("mean")
    )
    if dir_stats.empty:
        return _empty_chart("Not enough director data (need ≥ 3 films each).")

    fig, ax = _new_fig(8, 5)
    colors = [IMDB_YELLOW if i < len(dir_stats) - 1 else IMDB_RED
              for i in range(len(dir_stats))]
    bars = ax.barh(dir_stats.index, dir_stats["mean"],
                   color=colors, edgecolor=BG_DARK, height=0.6)
    # Value labels
    for bar in bars:
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.2f}",
                va="center", ha="left", color=TEXT_LIGHT, fontsize=8)
    _style_ax(ax, "🎬  Top 10 Directors by Average Rating",
              "Average Rating", "Director", grid_axis="x")
    ax.set_xlim(right=ax.get_xlim()[1] * 1.08)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 5 — Rating vs Revenue Scatter Plot
# ══════════════════════════════════════════════════════════════════════════════

def chart_rating_vs_revenue(df: pd.DataFrame):
    """
    Scatter plot comparing IMDB rating (x) with box-office revenue (y).
    Points are coloured by genre.
    Returns a Matplotlib Figure.
    """
    sub = df.dropna(subset=["rating", "revenue"])
    sub = sub[sub["revenue"] > 0]
    if sub.empty:
        return _empty_chart("No rating-revenue data available.")

    top_genres = sub["genre"].value_counts().nlargest(8).index.tolist()
    sub = sub[sub["genre"].isin(top_genres)].copy()
    genre_color = {g: CINEMA_PALETTE[i % len(CINEMA_PALETTE)]
                   for i, g in enumerate(top_genres)}

    fig, ax = _new_fig(9, 5)
    for genre in top_genres:
        g_df = sub[sub["genre"] == genre]
        ax.scatter(g_df["rating"], g_df["revenue"] / 1e6,
                   color=genre_color[genre], alpha=0.65, s=22,
                   label=genre, edgecolors="none")

    ax.set_yscale("log")
    ax.legend(fontsize=7, ncol=2, framealpha=0.5)
    _style_ax(ax, "💰  Rating vs Revenue",
              "IMDB Rating", "Revenue ($ M, log scale)", grid_axis="both")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 6 — Rating Distribution by Genre (Box Plot)
# ══════════════════════════════════════════════════════════════════════════════

def chart_genre_boxplot(df: pd.DataFrame):
    """
    Box plot of rating distributions for the top 6 genres.
    Returns a Matplotlib Figure.
    """
    top6 = df["genre"].value_counts().nlargest(6).index.tolist()
    sub = df[df["genre"].isin(top6)].dropna(subset=["rating"])
    if sub.empty:
        return _empty_chart("No genre / rating data available.")

    fig, ax = _new_fig(9, 5)
    bp = ax.boxplot(
        [sub.loc[sub["genre"] == g, "rating"].values for g in top6],
        labels=top6,
        patch_artist=True,
        medianprops={"color": IMDB_RED, "linewidth": 2},
        whiskerprops={"color": TEXT_DIM},
        capprops={"color": TEXT_DIM},
        flierprops={"marker": "o", "color": IMDB_YELLOW,
                    "markersize": 3, "alpha": 0.4},
    )
    for patch, color in zip(bp["boxes"], CINEMA_PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    _style_ax(ax, "📦  Rating Distribution by Genre (Top 6)",
              "Genre", "IMDB Rating")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 7 — Correlation Heatmap
# ══════════════════════════════════════════════════════════════════════════════

def chart_correlation_heatmap(df: pd.DataFrame):
    """
    Heatmap of the Pearson correlation matrix for the five numeric features:
    rating, votes, revenue, budget, runtime.
    Returns a Matplotlib Figure.
    """
    cols = [c for c in ["rating", "votes", "revenue", "budget", "runtime"]
            if c in df.columns]
    corr = df[cols].dropna(how="all").corr()
    if corr.empty:
        return _empty_chart("Not enough numeric data for a correlation matrix.")

    fig, ax = _new_fig(6.5, 5)
    cmap = sns.diverging_palette(10, 45, s=85, l=45, as_cmap=True)
    sns.heatmap(
        corr, ax=ax, annot=True, fmt=".2f",
        cmap=cmap, linewidths=0.5, linecolor=BG_DARK,
        annot_kws={"size": 9, "color": TEXT_LIGHT},
        cbar_kws={"shrink": 0.8},
        vmin=-1, vmax=1,
    )
    ax.set_title("🔥  Correlation Matrix of Numeric Features",
                 fontsize=13, fontweight="bold", color=TEXT_LIGHT, pad=12)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", color=TEXT_DIM)
    plt.setp(ax.get_yticklabels(), rotation=0, color=TEXT_DIM)
    plt.tight_layout(pad=1.5)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 8 — Cumulative Movies Released per Year (Area Chart)
# ══════════════════════════════════════════════════════════════════════════════

def chart_cumulative_movies(df: pd.DataFrame):
    """
    Area chart showing the cumulative total number of movies released each year.
    Returns a Matplotlib Figure.
    """
    yearly = df.groupby("year").size().sort_index().cumsum()
    if yearly.empty:
        return _empty_chart("No year data available.")

    fig, ax = _new_fig(9, 4.5)
    ax.fill_between(yearly.index, yearly.values,
                    color=IMDB_YELLOW, alpha=0.25)
    ax.plot(yearly.index, yearly.values,
            color=IMDB_YELLOW, linewidth=2.2)
    _style_ax(ax, "📅  Cumulative Movies Released per Year",
              "Year", "Cumulative Count")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 9 — Top 10 Most Common Genres (Count Plot)
# ══════════════════════════════════════════════════════════════════════════════

def chart_genre_count(df: pd.DataFrame):
    """
    Horizontal bar chart (count plot) of the top 10 most frequent genres.
    Returns a Matplotlib Figure.
    """
    counts = df["genre"].value_counts().nlargest(10).sort_values()
    if counts.empty:
        return _empty_chart("No genre data available.")

    fig, ax = _new_fig(8, 5)
    bars = ax.barh(counts.index, counts.values,
                   color=IMDB_YELLOW, edgecolor=BG_DARK, height=0.65)
    bars[-1].set_color(IMDB_RED)   # highlight the top genre

    for bar in bars:
        ax.text(bar.get_width() + counts.max() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width()):,}",
                va="center", ha="left", color=TEXT_LIGHT, fontsize=8)

    _style_ax(ax, "🎞  Top 10 Most Common Genres",
              "Number of Movies", "Genre", grid_axis="x")
    ax.set_xlim(right=counts.max() * 1.12)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Chart 10 — Rating Distribution by Language (Violin Plot)
# ══════════════════════════════════════════════════════════════════════════════

def chart_language_violin(df: pd.DataFrame):
    """
    Violin plot showing the full rating distribution for the top 5 languages.
    Returns a Matplotlib Figure.
    """
    top5 = df["language"].value_counts().nlargest(5).index.tolist()
    sub = df[df["language"].isin(top5)].dropna(subset=["rating"])
    if sub.empty:
        return _empty_chart("No language / rating data available.")

    fig, ax = _new_fig(9, 5)
    parts = ax.violinplot(
        [sub.loc[sub["language"] == lang, "rating"].values for lang in top5],
        positions=range(len(top5)),
        showmedians=True,
        showextrema=True,
    )
    for i, (pc, color) in enumerate(zip(parts["bodies"],
                                        CINEMA_PALETTE)):
        pc.set_facecolor(color)
        pc.set_alpha(0.75)
        pc.set_edgecolor(BG_DARK)
    parts["cmedians"].set_color(IMDB_RED)
    parts["cmedians"].set_linewidth(2)

    ax.set_xticks(range(len(top5)))
    ax.set_xticklabels(top5, color=TEXT_DIM)
    _style_ax(ax, "🌍  Rating Distribution by Language (Top 5)",
              "Language", "IMDB Rating")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Helper — Empty chart placeholder
# ══════════════════════════════════════════════════════════════════════════════

def _empty_chart(message: str = "No data available for the current filters."):
    """Returns a figure with a friendly 'no data' message."""
    fig, ax = _new_fig(7, 3)
    ax.text(0.5, 0.5, f"⚠️  {message}",
            ha="center", va="center",
            fontsize=12, color=IMDB_YELLOW,
            transform=ax.transAxes, wrap=True)
    ax.set_axis_off()
    _style_ax(ax, "", grid_axis=None)
    return fig
