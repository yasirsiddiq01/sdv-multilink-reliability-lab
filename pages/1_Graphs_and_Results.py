from __future__ import annotations

import streamlit as st

from src.ui_helpers import show_navigation

st.set_page_config(
    page_title="Graphs and Results | SDV Multi-Link Reliability Lab",
    page_icon="📊",
    layout="wide",
)

show_navigation()

st.title("Graphs and Results")
st.caption("Detailed KPI plots and tables are separated from the main decision dashboard to keep the project readable.")

if not st.session_state.get("analysis_has_run"):
    st.warning("No analysis result is available yet. Go to the Decision Dashboard, configure a scenario, and press Run reliability analysis.")
    st.stop()

result = st.session_state["analysis_result"]
scored = result.scored_data.copy()

st.markdown("## Reliability score over time")
chart_data = scored.pivot(index="time_step", columns="link", values="reliability_score")
st.line_chart(chart_data)

st.markdown("## Packet loss over time")
loss_data = scored.pivot(index="time_step", columns="link", values="packet_loss_pct")
st.line_chart(loss_data)

st.markdown("## Latency over time")
latency_data = scored.pivot(index="time_step", columns="link", values="latency_ms")
st.line_chart(latency_data)

st.markdown("## Latest KPI decision table")
st.dataframe(result.latest_table)

st.markdown("## Average reliability ranking across full trace")
st.dataframe(result.average_table)

st.markdown("## Full scored trace")
st.dataframe(scored)

st.download_button(
    label="Download scored CSV",
    data=scored.to_csv(index=False),
    file_name="sdv_multilink_scored_trace.csv",
    mime="text/csv",
)
