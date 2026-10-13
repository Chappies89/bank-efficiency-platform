"""Interactive prediction page with SHAP explanation."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(page_title="Predict Efficiency", page_icon="🔮", layout="wide")

st.title("🔮 Predict Branch Efficiency")
st.markdown("Enter branch KPIs to predict efficiency and see which factors drive the result.")

st.divider()

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        fte_count = st.number_input("FTE Count", min_value=1, max_value=500, value=20, step=1)
        operational_expense = st.number_input(
            "Operational Expense (ZAR)",
            min_value=1.0,
            max_value=100_000_000.0,
            value=1_000_000.0,
            step=50_000.0,
        )

    with col2:
        digital_ratio = st.slider("Digital Transaction Ratio", 0.0, 1.0, 0.75, 0.01)

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
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

        st.divider()

        # Prediction result
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

        # SHAP waterfall
        st.divider()
        st.subheader("🔍 Why This Prediction?")

        drivers = result.get("top_drivers", [])
        if drivers:
            features = [d["feature"] for d in drivers]
            contributions = [d["contribution"] for d in drivers]
            colors = ["#2ca02c" if c >= 0 else "#d62728" for c in contributions]

            fig = go.Figure(
                go.Bar(
                    x=contributions,
                    y=features,
                    orientation="h",
                    marker_color=colors,
                    text=[f"{c:+.3f}" for c in contributions],
                    textposition="outside",
                )
            )
            fig.update_layout(
                title="SHAP Feature Contributions",
                xaxis_title="Contribution to Prediction",
                yaxis_title="Feature",
                height=300,
                margin={"l": 20, "r": 20, "t": 40, "b": 20},
            )
            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "Green bars pushed the score **up**; red bars pushed it **down**. "
                "Magnitudes show how strongly each feature influenced the result."
            )
        else:
            st.info("No SHAP explanation available for this prediction.")

    except httpx.HTTPError as e:
        st.error(f"API request failed: {e}")
        st.info("Make sure the API is running: " "`uvicorn src.presentation.api.main:app`")
