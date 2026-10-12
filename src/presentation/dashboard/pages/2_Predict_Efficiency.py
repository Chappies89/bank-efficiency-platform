"""Interactive prediction page."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(page_title="Predict Efficiency", page_icon="🔮", layout="wide")

st.title("🔮 Predict Branch Efficiency")
st.markdown("Enter branch KPIs to predict the efficiency score using the ML model.")

st.divider()

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        fte_count = st.number_input(
            "FTE Count",
            min_value=1,
            max_value=500,
            value=20,
            step=1,
        )
        operational_expense = st.number_input(
            "Operational Expense (ZAR)",
            min_value=1.0,
            max_value=100_000_000.0,
            value=1_000_000.0,
            step=50_000.0,
        )

    with col2:
        digital_ratio = st.slider(
            "Digital Transaction Ratio",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.01,
        )

    submitted = st.form_submit_button("Predict Efficiency", type="primary")

if submitted:
    try:
        response = httpx.post(
            "http://localhost:8000/api/predict",
            json={
                "fte_count": int(fte_count),
                "operational_expense": float(operational_expense),
                "digital_transaction_ratio": float(digital_ratio),
            },
            timeout=10.0,
        )
        response.raise_for_status()
        result = response.json()

        st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:
            score = result["predicted_efficiency"]
            st.metric("Predicted Efficiency", f"{score:.2%}")

            if score >= 0.95:
                st.success("🌟 **On the frontier** — best in class")
            elif score >= 0.80:
                st.info("✅ **Strong performance** — top quartile")
            elif score >= 0.60:
                st.warning("⚠️ **Moderate efficiency** — improvement potential")
            else:
                st.error("🔴 **Low efficiency** — significant gaps")

        with col2:
            st.markdown(f"**Model Run ID:** `{result['model_run_id']}`")
            st.markdown(
                f"""
                **Input KPIs:**
                - FTE Count: **{fte_count}**
                - Operational Expense: **R{operational_expense:,.0f}**
                - Digital Ratio: **{digital_ratio:.0%}**
                """
            )

    except httpx.HTTPError as e:
        st.error(f"API request failed: {e}")
        st.info("Make sure the API is running: " "`uvicorn src.presentation.api.main:app`")
