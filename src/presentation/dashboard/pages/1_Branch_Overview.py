"""Branch overview page."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import streamlit as st  # noqa: E402

from src.presentation.dashboard.data import (  # noqa: E402
    load_branches_with_efficiency,
)

st.set_page_config(page_title="Branch Overview", page_icon="📊", layout="wide")

st.title("📊 Branch Overview")
st.markdown("Explore efficiency across all bank branches.")

df = load_branches_with_efficiency()

if df.empty:
    st.warning("No data. Run the seed script first.")
    st.stop()

# Filters
col1, col2 = st.columns(2)
with col1:
    regions = ["All"] + sorted(df["region"].dropna().unique().tolist())
    selected_region = st.selectbox("Filter by region", regions)
with col2:
    only_scored = st.checkbox("Only show scored branches", value=False)

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]
if only_scored:
    filtered = filtered[filtered["efficiency_score"].notna()]

st.divider()

# Histogram
if filtered["efficiency_score"].notna().any():
    st.subheader("Efficiency Distribution")

    fig = px.histogram(
        filtered.dropna(subset=["efficiency_score"]),
        x="efficiency_score",
        nbins=20,
        title="Distribution of Efficiency Scores",
        labels={
            "efficiency_score": "Efficiency Score",
            "count": "Number of Branches",
        },
    )
    fig.add_vline(
        x=1.0,
        line_dash="dash",
        line_color="green",
        annotation_text="Frontier",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Table
st.subheader(f"Branch Table ({len(filtered)} branches)")

display_cols = [
    "branch_id",
    "branch_name",
    "region",
    "square_meters",
    "efficiency_score",
    "observation_date",
]
display_df = filtered[display_cols].copy()
display_df["efficiency_score"] = display_df["efficiency_score"].apply(
    lambda x: f"{x:.4f}" if pd.notna(x) else "—"
)

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Top and bottom performers
if filtered["efficiency_score"].notna().any():
    st.divider()
    scored_df = filtered.dropna(subset=["efficiency_score"])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top 5 Performers")
        top = scored_df.nlargest(5, "efficiency_score")[
            ["branch_name", "region", "efficiency_score"]
        ]
        st.dataframe(top, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("⚠️ Bottom 5 Performers")
        bottom = scored_df.nsmallest(5, "efficiency_score")[
            ["branch_name", "region", "efficiency_score"]
        ]
        st.dataframe(bottom, use_container_width=True, hide_index=True)
