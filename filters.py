"""
filters.py — Data loading, cleaning, and filtering functions
IMDB Movies Analytics Dashboard
"""

import pandas as pd
import numpy as np


# ──────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ──────────────────────────────────────────────

def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """
    Loads the IMDB CSV file and performs all necessary cleaning steps.
    Returns a clean DataFrame ready for analysis and visualisation.
    """

    # ── Load ──────────────────────────────────
    df = pd.read_csv(filepath, encoding="utf-8", low_memory=False)

    # ── Normalise column names ─────────────────
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # ── Rename to expected schema if needed ───
    rename_map = {
        "title":        "movie_title",
        "name":         "movie_title",
        "genres":       "genre",
        "imdb_rating":  "rating",
        "imdb_score":   "rating",
        "num_voted_users": "votes",
        "gross":        "revenue",
        "director_name":"director",
        "actor_1_name": "cast",
        "duration":     "runtime",
        "title_year":   "year",
        "color":        "language",   # fallback only
        "country":      "country",
        "budget":       "budget",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns},
              inplace=True)

    # ── Ensure all expected columns exist ─────
    expected = ["movie_title", "year", "genre", "rating", "votes",
                "revenue", "director", "cast", "runtime", "language",
                "country", "budget"]
    for col in expected:
        if col not in df.columns:
            df[col] = np.nan

    # ── Year ──────────────────────────────────
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    # If year still largely missing, try to parse from a date column
    if df["year"].isna().mean() > 0.5:
        for candidate in ["release_date", "date_published", "release_year"]:
            if candidate in df.columns:
                df["year"] = pd.to_datetime(
                    df[candidate], errors="coerce"
                ).dt.year
                break
    df["year"] = df["year"].fillna(2000).astype(int)

    # ── Rating ────────────────────────────────
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["rating"] = df["rating"].clip(0, 10)

    # ── Votes ─────────────────────────────────
    df["votes"] = (
        df["votes"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # ── Revenue & Budget (strip $, commas, K/M) ──
    for col in ["revenue", "budget"]:
        df[col] = _clean_currency_column(df[col])

    # ── Runtime ───────────────────────────────
    df["runtime"] = (
        df["runtime"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .pipe(pd.to_numeric, errors="coerce")
    )

    # ── Genre — keep first genre if pipe/comma-separated ──
    df["genre"] = (
        df["genre"]
        .astype(str)
        .str.strip()
        .str.split(r"[|,/]")
        .str[0]
        .str.strip()
        .replace({"nan": "Unknown", "": "Unknown"})
    )

    # ── Text columns — strip whitespace ───────
    for col in ["movie_title", "director", "cast", "language", "country"]:
        df[col] = df[col].astype(str).str.strip().replace("nan", "Unknown")

    # ── Drop rows with no usable data ─────────
    df.dropna(subset=["movie_title"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _clean_currency_column(series: pd.Series) -> pd.Series:
    """Strip currency symbols and convert multipliers (K, M, B) to floats."""
    s = (
        series
        .astype(str)
        .str.replace(r"[\$,\s]", "", regex=True)
        .str.upper()
    )
    # Handle multipliers
    billions  = s.str.endswith("B")
    millions  = s.str.endswith("M")
    thousands = s.str.endswith("K")

    s = s.str.rstrip("BMK")
    s = pd.to_numeric(s, errors="coerce")
    s = s.where(~billions,  s * 1_000_000_000)
    s = s.where(~millions,  s * 1_000_000)
    s = s.where(~thousands, s * 1_000)
    return s


# ──────────────────────────────────────────────
# 2. APPLY FILTERS
# ──────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    year_range: tuple,
    genres: list,
    rating_range: tuple,
    countries: list,
    search_text: str,
) -> pd.DataFrame:
    """
    Applies all sidebar filters to the DataFrame and returns the filtered result.

    Parameters
    ----------
    df           : cleaned DataFrame from load_and_clean_data()
    year_range   : (min_year, max_year) tuple from the year slider
    genres       : list of selected genre strings; empty list = all genres
    rating_range : (min_rating, max_rating) tuple
    countries    : list of selected country strings; empty list = all countries
    search_text  : keyword to search within movie_title (case-insensitive)
    """

    filtered = df.copy()

    # ── Year range ────────────────────────────
    filtered = filtered[
        (filtered["year"] >= year_range[0]) &
        (filtered["year"] <= year_range[1])
    ]

    # ── Genre multi-select ────────────────────
    if genres:
        filtered = filtered[filtered["genre"].isin(genres)]

    # ── Rating range ─────────────────────────
    filtered = filtered[
        (filtered["rating"] >= rating_range[0]) &
        (filtered["rating"] <= rating_range[1])
    ]

    # ── Country multi-select ──────────────────
    if countries:
        filtered = filtered[filtered["country"].isin(countries)]

    # ── Keyword / title search ────────────────
    if search_text.strip():
        mask = filtered["movie_title"].str.contains(
            search_text.strip(), case=False, na=False, regex=False
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)
