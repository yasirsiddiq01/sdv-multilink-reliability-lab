"""Shared Streamlit UI helpers."""

from __future__ import annotations

import streamlit as st


def show_navigation() -> None:
    st.sidebar.markdown("### Navigation")
    st.sidebar.page_link("app.py", label="Decision Dashboard")
    st.sidebar.page_link("pages/1_Graphs_and_Results.py", label="Graphs and Results")
    st.sidebar.page_link("pages/2_About_and_Help.py", label="About and Help")
    st.sidebar.divider()


def status_message(status: str) -> None:
    if status == "ACCEPT":
        st.success("ACCEPT: selected link is currently reliable for the synthetic SDV scenario.")
    elif status == "MONITOR":
        st.warning("MONITOR: selected link is usable, but degradation should be tracked.")
    elif status == "RISK":
        st.error("RISK: selected link is not in hard-fail state, but the reliability score is weak.")
    else:
        st.error("FAIL: all candidate links are degraded or at least one hard-fail rule is active.")
