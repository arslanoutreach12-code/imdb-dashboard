"""
app.py — Main Streamlit dashboard
🎬 IMDB Movies Analytics Dashboard
EDA Course Project

Run with:  streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd

# ── Local modules ──────────────────────────────────────────────────────────
from filters import load_and_clean_data, apply_filters
import charts

# ══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the very first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="IMDB Movies Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — cinema dark theme ────────────────────────────────────────
st.markdown("""
<style>
/* ── Global background ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d1a;
    color: #e0e0e0;
}
[data-testid="stSidebar"] {
    background-color: #12122b;
    border-right: 1px solid #2e2e4e;
}
/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(135deg, #16213e 0%, #1a1a3e 100%);
    border: 1px solid #2e2e4e;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #F5C518;
    margin: 0;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #a0a0b0;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.kpi-icon {
    font-size: 1.5rem;
    margin-bottom: 6px;
}
/* ── Section headers ── */
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F5C518;
    border-left: 4px solid #E50914;
    padding-left: 10px;
    margin: 24px 0 12px 0;
}
/* ── Divider ── */
hr { border-color: #2e2e4e; }
/* ── Reset button ── */
div.stButton > button {
    background-color: #E50914;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    width: 100%;
}
div.stButton > button:hover { background-color: #c0070f; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# DATA LOADING  (cached so it only runs once)
# ══════════════════════════════════════════════════════════════════════════

DATA_PATH = os.path.join("data", "imdb_movies.csv")

@st.cache_data(show_spinner="Loading & cleaning dataset …")
def get_data():
    return load_and_clean_data(DATA_PATH)

# Guard — show a nice error if the CSV is missing
if not os.path.exists(DATA_PATH):
    st.error(
        "**Dataset not found!**  \n"
        f"Please place your CSV file at `{DATA_PATH}`.  \n"
        "Expected columns: `movie_title, year, genre, rating, votes, "
        "revenue, director, cast, runtime, language, country, budget`"
    )
    st.stop()

df_raw = get_data()


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS
# ══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<h2 style='color:#F5C518;margin-bottom:4px;'>🎬 IMDB Dashboard</h2>"
        "<p style='color:#a0a0b0;font-size:0.8rem;margin-top:0;'>"
        "EDA Course Project</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🎛️  Filters")

    # ── Year range ──────────────────────────────────────────────────────
    year_min = int(df_raw["year"].min())
    year_max = int(df_raw["year"].max())
    year_range = st.slider(
        "📅 Year Range",
        min_value=year_min, max_value=year_max,
        value=(year_min, year_max), step=1,
    )

    # ── Genre ───────────────────────────────────────────────────────────
    all_genres = sorted(df_raw["genre"].dropna().unique().tolist())
    selected_genres = st.multiselect(
        "🎭 Genre",
        options=all_genres,
        default=[],
        placeholder="All genres",
    )

    # ── Rating range ────────────────────────────────────────────────────
    rating_range = st.slider(
        "⭐ Rating Range",
        min_value=0.0, max_value=10.0,
        value=(0.0, 10.0), step=0.1,
    )

    # ── Country ─────────────────────────────────────────────────────────
    all_countries = sorted(
        df_raw["country"].replace("Unknown", pd.NA).dropna().unique().tolist()
    )
    selected_countries = st.multiselect(
        "🌍 Country",
        options=all_countries,
        default=[],
        placeholder="All countries",
    )

    # ── Keyword search ──────────────────────────────────────────────────
    search_text = st.text_input("🔍 Search Movie Title", value="",
                                placeholder="e.g. Inception …")

    st.markdown("---")

    # ── Reset button ────────────────────────────────────────────────────
    if st.button("🔄  Reset All Filters"):
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════

df = apply_filters(
    df_raw,
    year_range=year_range,
    genres=selected_genres,
    rating_range=rating_range,
    countries=selected_countries,
    search_text=search_text,
)


# ══════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════

st.markdown(
    "<h1 style='color:#F5C518;font-size:2.2rem;margin-bottom:2px;'>"
    "🎬 IMDB Movies Analytics Dashboard</h1>"
    "<p style='color:#a0a0b0;font-size:0.95rem;margin-top:0;'>"
    "Exploratory Data Analysis — 10 000+ movies  ·  "
    "Genres · Ratings · Revenue · Directors"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════
# EMPTY FILTER GUARD
# ══════════════════════════════════════════════════════════════════════════

if df.empty:
    st.warning(
        "⚠️  No movies match the current filters.  "
        "Try widening the year range, relaxing the rating slider, "
        "or clearing genre / country selections."
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════

total_movies = len(df)
avg_rating   = df["rating"].mean()
avg_revenue  = df["revenue"].dropna()
avg_revenue  = avg_revenue[avg_revenue > 0].mean()
best_row     = df.loc[df["rating"].idxmax()] if not df["rating"].isna().all() else None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

def _kpi_card(col, icon, value, label):
    col.markdown(
        f"<div class='kpi-card'>"
        f"<div class='kpi-icon'>{icon}</div>"
        f"<p class='kpi-value'>{value}</p>"
        f"<p class='kpi-label'>{label}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

_kpi_card(kpi1, "🎥", f"{total_movies:,}", "Total Movies")
_kpi_card(kpi2, "⭐", f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A", "Average Rating")
_kpi_card(kpi3, "💵",
          f"${avg_revenue/1e6:.1f}M" if pd.notna(avg_revenue) else "N/A",
          "Avg Revenue")
_kpi_card(kpi4, "🏆",
          best_row["movie_title"][:20] + "…" if best_row is not None and len(best_row["movie_title"]) > 20 else (best_row["movie_title"] if best_row is not None else "N/A"),
          f"Highest Rated  ({best_row['rating']:.1f}⭐)" if best_row is not None else "N/A")

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — RATING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-header'>⭐ Rating Analysis</div>",
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.pyplot(charts.chart_rating_histogram(df))
with col_b:
    st.pyplot(charts.chart_rating_trend(df))

col_c, col_d = st.columns(2)
with col_c:
    st.pyplot(charts.chart_genre_boxplot(df))
with col_d:
    st.pyplot(charts.chart_language_violin(df))


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — REVENUE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-header'>💰 Revenue Analysis</div>",
            unsafe_allow_html=True)

col_e, col_f = st.columns(2)
with col_e:
    st.pyplot(charts.chart_rating_vs_revenue(df))
with col_f:
    st.pyplot(charts.chart_correlation_heatmap(df))


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — GENRE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-header'>🎭 Genre Analysis</div>",
            unsafe_allow_html=True)

col_g, col_h = st.columns(2)
with col_g:
    st.pyplot(charts.chart_genre_pie(df))
with col_h:
    st.pyplot(charts.chart_genre_count(df))


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — DIRECTORS & TIMELINE
# ══════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-header'>🎬 Directors & Timeline</div>",
            unsafe_allow_html=True)

col_i, col_j = st.columns(2)
with col_i:
    st.pyplot(charts.chart_top_directors(df))
with col_j:
    st.pyplot(charts.chart_cumulative_movies(df))


# ══════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#a0a0b0;font-size:0.8rem;'>"
    f"Showing <b style='color:#F5C518;'>{total_movies:,}</b> movies · "
    f"Data source: IMDB Movies Dataset · EDA Course Project</p>",
    unsafe_allow_html=True,
)
