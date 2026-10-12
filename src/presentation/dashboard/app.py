"""Streamlit dashboard home page."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so 'src' package is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from src.presentation.dashboard.data import (  # noqa: E402
    load_branches_with_efficiency,
)

st.set_page_config(
    page_title="Bank Efficiency Platform",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Bank Efficiency Platform")
st.markdown("**DEA-ML hybrid platform for measuring and predicting bank branch efficiency.**")

st.divider()

with st.spinner("Loading data..."):
    df = load_branches_with_efficiency()

if df.empty:
    st.warning("No data available. Run `python scripts/seed_database.py` to populate the database.")
else:
    total_branches = len(df)
    scored = df["efficiency_score"].notna().sum()
    efficient = (df["efficiency_score"] == 1.0).sum() if scored > 0 else 0
    avg_eff = df["efficiency_score"].mean() if scored > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Branches", f"{total_branches}")
    col2.metric("Scored Branches", f"{scored}")
    col3.metric("Efficient (1.0)", f"{efficient}")
    col4.metric("Average Efficiency", f"{avg_eff:.2%}" if scored > 0 else "—")

    st.divider()

    st.subheader("Quick Guide")
    st.markdown(
        """
        **Available Pages** (use the sidebar):

        - **📊 Branch Overview** — Table of all branches with latest efficiency scores
        - **🔮 Predict Efficiency** — Interactive "what-if" prediction form

        **Data Source:** PostgreSQL (`branches`, `branch_observations`, `dea_results`)
        """
    )
