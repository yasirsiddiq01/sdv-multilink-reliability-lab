from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from .config import AFFECTED_LINK_OPTIONS, SCENARIO_LABELS
from .generator import generate_scenario, validate_uploaded_scenario
from .reliability import apply_scoring, select_best_link


def inject_css() -> None:
    st.markdown(
        """
<style>
:root {
  --navy: #07234a;
  --blue: #0b5ed7;
  --muted: #5d6b82;
  --border: #dbe5f4;
  --card: #ffffff;
  --soft-blue: #eef6ff;
  --green: #118753;
  --orange: #d86b00;
}

/* Hide Streamlit's automatic page navigation/header noise. */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { background: rgba(255,255,255,0.88); }
a[href^="#"] { display: none !important; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 70%);
  border-right: 1px solid #dfe7f2;
}

.block-container {
  padding-top: 3.2rem;
  padding-bottom: 3rem;
  padding-left: 2.4rem;
  padding-right: 2.4rem;
  max-width: 1160px;
}

h1 {
  color: var(--navy);
  font-size: 2.65rem !important;
  line-height: 1.12;
  letter-spacing: -0.025em;
  margin-bottom: 0.35rem !important;
}
h2, h3 { color: #102442; }
p, li, div { color: #182640; }
.small-muted { color: #6c788e; font-size: 0.96rem; margin-bottom: 1rem; }

.hero-note {
  border: 1px solid #b9d5ff;
  background: #eef6ff;
  border-radius: 10px;
  padding: 0.95rem 1.05rem;
  color: #064da8;
  margin: 1.1rem 0 1.35rem 0;
}

.sidebar-brand {
  background: linear-gradient(135deg, #061d3d 0%, #082b5a 100%);
  margin: -0.65rem -0.75rem 1.15rem -0.75rem;
  padding: 1.35rem 1.05rem;
  color: white;
  border-radius: 0 0 14px 0;
  overflow: visible;
}
.sidebar-brand-row {
  display: flex;
  gap: 0.7rem;
  align-items: center;
  min-width: 0;
}
.sidebar-logo {
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  line-height: 1;
}
.sidebar-brand-title {
  color: white !important;
  font-weight: 800;
  font-size: 1.13rem;
  line-height: 1.13;
  letter-spacing: -0.01em;
  white-space: normal;
  overflow-wrap: anywhere;
}

.sidebar-section {
  margin: 0.85rem 0 0.45rem 0;
  color: #566276;
  font-weight: 800;
  font-size: 0.76rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* Clean navigation radio style. */
[data-testid="stSidebar"] [role="radiogroup"] label {
  border: 1px solid #d5dfed;
  border-radius: 10px;
  padding: 0.62rem 0.75rem;
  margin-bottom: 0.38rem;
  background: #ffffff;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  border-color: #9fc3ff;
  background: #f4f8ff;
}

/* Scenario panel */
div[data-testid="stForm"] {
  border: 1px solid #dbe5f4;
  border-radius: 14px;
  padding: 1rem;
  box-shadow: 0 4px 18px rgba(8, 35, 75, 0.06);
  background: white;
}

/* Explicit boundaries for sidebar fields. Streamlit's default borders can look too faint. */
div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stFileUploader"] section {
  border: 1px solid #b9c8dc !important;
  border-radius: 9px !important;
  background: #ffffff !important;
  box-shadow: 0 1px 2px rgba(8,35,75,0.04) !important;
}
div[data-testid="stNumberInput"] button {
  border: 1px solid #cbd6e6 !important;
  background: #f9fbff !important;
}
div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] p {
  font-size: 0.9rem !important;
}

.metric-card {
  background: white;
  border: 1px solid #e1e8f2;
  border-radius: 14px;
  padding: 1.05rem 1.1rem;
  box-shadow: 0 4px 18px rgba(8, 35, 75, 0.07);
  min-height: 112px;
}
.metric-label {
  color: #60708a;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.metric-value {
  color: #0b5ed7;
  font-size: 1.55rem;
  font-weight: 800;
  margin-top: 0.35rem;
}
.metric-sub {
  color: #66758d;
  font-size: 0.82rem;
  margin-top: 0.35rem;
}
.decision-box {
  border: 1px solid #b7e4ca;
  border-left: 5px solid #118753;
  background: linear-gradient(90deg, #f0fbf5 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 1.15rem 1.25rem;
  margin: 1.2rem 0 1.1rem 0;
}
.decision-title { font-weight: 800; color: #0f5132; margin-bottom: 0.2rem; }
.decision-headline { font-size: 1.23rem; font-weight: 800; color: #118753; }
.warning-box {
  border: 1px solid #ffd18c;
  border-left: 5px solid #f0a230;
  background: #fffaf1;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  margin-top: 1rem;
}
.warning-title { color: #a34f00; font-weight: 800; margin-bottom: 0.55rem; }
.info-card {
  background: white;
  border: 1px solid #dbe5f4;
  border-radius: 14px;
  padding: 1.15rem 1.2rem;
  box-shadow: 0 4px 18px rgba(8, 35, 75, 0.06);
  min-height: 250px;
  margin-bottom: 1rem;
}
.info-card h3 {
  font-size: 1.05rem;
  margin-top: 0;
  margin-bottom: 0.65rem;
}
.chart-card {
  background: white;
  border: 1px solid #e1e8f2;
  border-radius: 14px;
  padding: 0.9rem;
  box-shadow: 0 4px 18px rgba(8, 35, 75, 0.06);
}
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
  border-radius: 10px;
  min-height: 2.6rem;
  font-weight: 750;
}
[data-testid="stFormSubmitButton"] button {
  width: 100%;
  background: #0b5ed7;
  color: white;
  border: 1px solid #0b5ed7;
}
hr { border: none; border-top: 1px solid #e1e8f2; margin: 1.1rem 0; }

/* Avoid cramped horizontal overflow on common laptop screens. */
@media (max-width: 1200px) {
  .block-container { padding-left: 1.6rem; padding-right: 1.6rem; }
  h1 { font-size: 2.25rem !important; }
  .metric-value { font-size: 1.32rem; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    st.sidebar.markdown(
        """
<div class="sidebar-brand">
  <div class="sidebar-brand-row">
    <div class="sidebar-logo">🚙</div>
    <div class="sidebar-brand-title">SDV Multi-Link<br/>Reliability Lab</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_navigation() -> str:
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Decision Dashboard"

    st.sidebar.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    nav_items = ["Decision Dashboard", "Graphs and Results", "About and Help"]
    current = st.session_state["active_page"]
    index = nav_items.index(current) if current in nav_items else 0

    selected = st.sidebar.radio(
        "Navigation",
        nav_items,
        index=index,
        label_visibility="collapsed",
        key="navigation_radio",
    )
    if selected != st.session_state["active_page"]:
        st.session_state["active_page"] = selected
        st.rerun()

    st.sidebar.markdown("<hr/>", unsafe_allow_html=True)
    return st.session_state["active_page"]


def scenario_form() -> tuple[bool, dict]:
    st.sidebar.markdown('<div class="sidebar-section">Scenario setup</div>', unsafe_allow_html=True)
    with st.sidebar.form("scenario_form"):
        scenario_label_options = list(SCENARIO_LABELS.values())
        label_to_key = {v: k for k, v in SCENARIO_LABELS.items()}

        selected_label = st.selectbox("Scenario type", scenario_label_options, index=0)
        affected_link = st.selectbox("Affected link", AFFECTED_LINK_OPTIONS, index=0)
        time_steps = st.number_input("Time steps", min_value=10, max_value=500, value=100, step=5)
        seed = st.number_input("Random seed", min_value=0, max_value=99999, value=42, step=1)
        uploaded = st.file_uploader("Optional CSV upload", type=["csv"])

        submitted = st.form_submit_button("▶ Run reliability analysis")

    return submitted, {
        "scenario": label_to_key[selected_label],
        "scenario_label": selected_label,
        "affected_link": affected_link,
        "time_steps": int(time_steps),
        "seed": int(seed),
        "uploaded": uploaded,
    }


def run_analysis(config: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    uploaded = config.get("uploaded")
    if uploaded is not None:
        raw_df = pd.read_csv(uploaded)
        valid, issues = validate_uploaded_scenario(raw_df)
        if not valid:
            raise ValueError("; ".join(issues))
    else:
        raw_df = generate_scenario(
            scenario=config["scenario"],
            affected_link=config["affected_link"],
            time_steps=config["time_steps"],
            seed=config["seed"],
        )

    scored = apply_scoring(raw_df)
    decision = select_best_link(scored)
    return raw_df, scored, decision


def ensure_initial_result() -> None:
    if "analysis" not in st.session_state:
        config = {
            "scenario": "normal",
            "scenario_label": "Nominal Operation",
            "affected_link": "All links",
            "time_steps": 100,
            "seed": 42,
            "uploaded": None,
        }
        raw_df, scored, decision = run_analysis(config)
        st.session_state["analysis"] = {
            "config": config,
            "raw_df": raw_df,
            "scored_df": scored,
            "decision": decision,
        }


def latest_metric_cards(decision: dict) -> None:
    cols = st.columns(4)
    values = [
        ("Selected link", decision["selected_link"], "Active connection", "#0b5ed7"),
        ("Latest score", f"{decision['selected_score']:.1f} /100", "Current reliability", "#118753"),
        ("Failover events", str(decision["failover_events"]), "Events observed", "#6f42c1"),
        ("Rejected links", str(len(decision["rejected_links"])), ", ".join(decision["rejected_links"]), "#d86b00"),
    ]

    for col, (label, value, sub, color) in zip(cols, values):
        with col:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-label">{html.escape(label)}</div>
  <div class="metric-value" style="color:{color};">{html.escape(value)}</div>
  <div class="metric-sub">{html.escape(sub)}</div>
</div>
                """,
                unsafe_allow_html=True,
            )


def status_badge(status: str) -> str:
    colors = {
        "Excellent": ("#e7f2ff", "#0b5ed7"),
        "Good": ("#e8f7ef", "#118753"),
        "Monitor": ("#fff7e6", "#a34f00"),
        "Degraded": ("#fff1e8", "#d86b00"),
        "Hard fail": ("#fde8e8", "#b42318"),
    }
    bg, fg = colors.get(status, ("#eef2f7", "#475467"))
    return f'<span style="background:{bg};color:{fg};border-radius:999px;padding:0.25rem 0.55rem;font-weight:700;font-size:0.8rem;">{html.escape(status)}</span>'


def format_latest_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "link",
        "latency_ms",
        "jitter_ms",
        "packet_loss_pct",
        "throughput_mbps",
        "signal_quality",
        "availability",
        "reliability_score",
        "status",
    ]
    out = df[cols].copy()
    out = out.rename(
        columns={
            "link": "Link",
            "latency_ms": "Latency (ms)",
            "jitter_ms": "Jitter (ms)",
            "packet_loss_pct": "Packet Loss (%)",
            "throughput_mbps": "Throughput (Mbps)",
            "signal_quality": "Signal Quality (/100)",
            "availability": "Availability",
            "reliability_score": "Reliability Score (/100)",
            "status": "Status",
        }
    )
    return out


def page_header(title: str, subtitle: str) -> None:
    # Avoid the previous top-right status text because it was clipped on laptop-width screens.
    st.title(title)
    st.markdown(f'<p class="small-muted">{html.escape(subtitle)}</p>', unsafe_allow_html=True)


def chart_line_data(scored_df: pd.DataFrame, metric: str) -> pd.DataFrame:
    pivot = scored_df.pivot(index="time_step", columns="link", values=metric)
    return pivot
