from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import HARD_FAIL_LIMITS, LINK_PROFILES, REQUIRED_COLUMNS, SCENARIOS, WEIGHTS
from src.ui_helpers import show_navigation

st.set_page_config(
    page_title="About and Help | SDV Multi-Link Reliability Lab",
    page_icon="ℹ️",
    layout="wide",
)

show_navigation()

st.title("About and Help")

st.markdown(
    """
## What this project demonstrates

This project is a research-oriented synthetic reliability demo for software-defined vehicle connectivity. It compares multiple candidate links and selects the most reliable active link using transparent KPIs.

The purpose is to show an explainable decision workflow relevant to multi-link communications research:

- compare ITS-G5 / Wi-Fi-like V2X, 5G, and an optional 6G candidate link;
- simulate changing network conditions;
- detect degraded links;
- select a primary link;
- show rejected links and warning conditions;
- export a small decision report.

## What this project does not claim

This is not a real SDV simulator. It does not model real radio propagation, real vehicle mobility, real ETSI ITS-G5 behaviour, real 5G NR scheduling, real 6G air-interface design, ns-3, OMNeT++, SUMO, or vendor-grade measurements.

It is a compact portfolio project designed to demonstrate research thinking, KPI analysis, explainability, and clean Python implementation.
"""
)

st.markdown("## Synthetic link profiles")
st.dataframe(pd.DataFrame(LINK_PROFILES).T.reset_index().rename(columns={"index": "link"}))

st.markdown("## Supported degradation scenarios")
st.write(", ".join(SCENARIOS))

st.markdown("## Reliability score weights")
st.dataframe(pd.DataFrame([WEIGHTS]).T.reset_index().rename(columns={"index": "factor", 0: "weight"}))

st.markdown("## Hard-fail limits")
st.dataframe(pd.DataFrame([HARD_FAIL_LIMITS]).T.reset_index().rename(columns={"index": "rule", 0: "limit"}))

st.markdown("## CSV upload schema")
st.write("Uploaded CSV files must include these columns:")
st.code("\n".join(REQUIRED_COLUMNS), language="text")

st.markdown(
    """
## How to read the score

The reliability score is a synthetic decision index from 0 to 100. It combines latency, jitter, packet loss, throughput, signal quality, and availability. A higher score means the link is more suitable for the current synthetic scenario.

The score should be read as a relative link-selection signal. It is not a real safety guarantee and should not be interpreted as certified vehicle connectivity performance.
"""
)
