from __future__ import annotations

import streamlit as st

from src.reporting import build_markdown_report
from src.reliability import decision_headline, decision_paragraph, warning_bullets
from src.ui import (
    chart_line_data,
    ensure_initial_result,
    format_latest_table,
    inject_css,
    latest_metric_cards,
    page_header,
    run_analysis,
    scenario_form,
    sidebar_brand,
    sidebar_navigation,
)


st.set_page_config(
    page_title="SDV Multi-Link Reliability Lab",
    page_icon="🚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
sidebar_brand()
active_page = sidebar_navigation()
submitted, scenario_config = scenario_form()

if submitted:
    try:
        raw_df, scored_df, decision = run_analysis(scenario_config)
        st.session_state["analysis"] = {
            "config": scenario_config,
            "raw_df": raw_df,
            "scored_df": scored_df,
            "decision": decision,
        }
        st.session_state["analysis_message"] = "Analysis completed."
    except Exception as exc:
        st.session_state["analysis_error"] = str(exc)

ensure_initial_result()

if "analysis_error" in st.session_state:
    st.error(st.session_state.pop("analysis_error"))

analysis = st.session_state["analysis"]
config = analysis["config"]
scored_df = analysis["scored_df"]
decision = analysis["decision"]


def render_decision_dashboard() -> None:
    page_header(
        "SDV Multi-Link Reliability Lab",
        "Synthetic multi-link selection and failover demo for software-defined vehicle research.",
    )

    st.markdown(
        """
<div class="hero-note">
  ℹ️ This is a research-oriented synthetic reliability demo. It is not a real SDV/ITS-G5/5G/6G simulator.
</div>
        """,
        unsafe_allow_html=True,
    )

    latest_metric_cards(decision)

    st.markdown(
        f"""
<div class="decision-box">
  <div class="decision-title">Reliability decision</div>
  <div class="decision-headline">{decision_headline(decision)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(decision_paragraph(decision))

    bullets = "".join(f"<li>{item}</li>" for item in warning_bullets(decision))
    st.markdown(
        f"""
<div class="warning-box">
  <div class="warning-title">⚠ Warning and fail conditions</div>
  <ul>{bullets}</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

    report = build_markdown_report(
        decision=decision,
        scored_df=scored_df,
        scenario_label=config["scenario_label"],
        affected_link=config["affected_link"],
        time_steps=config["time_steps"],
        seed=config["seed"],
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Download decision report",
            data=report,
            file_name="sdv_multilink_reliability_report.md",
            mime="text/markdown",
        )
    with col2:
        st.download_button(
            "Download scored CSV",
            data=scored_df.to_csv(index=False),
            file_name="sdv_multilink_scored_results.csv",
            mime="text/csv",
        )


def render_graphs_and_results() -> None:
    page_header(
        "Graphs and Results",
        "Detailed KPI plots and trace-level results are separated from the main decision dashboard for clarity.",
    )

    st.markdown(
        '<div class="hero-note">ℹ️ Results reflect the most recent reliability analysis run.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        link_filter = st.selectbox("Selected link", ["All Links"] + sorted(scored_df["link"].unique().tolist()))
    with c2:
        metric_label = st.selectbox(
            "KPI metric",
            [
                "Reliability Score",
                "Latency",
                "Packet Loss",
                "Throughput",
                "Signal Quality",
                "Availability",
            ],
        )
    with c3:
        time_window = st.selectbox("Time window", ["Full trace", "Last 100 steps", "Last 50 steps"])

    filtered = scored_df.copy()
    if link_filter != "All Links":
        filtered = filtered[filtered["link"] == link_filter]

    if time_window == "Last 100 steps":
        start = max(0, int(scored_df["time_step"].max()) - 99)
        filtered = filtered[filtered["time_step"] >= start]
    elif time_window == "Last 50 steps":
        start = max(0, int(scored_df["time_step"].max()) - 49)
        filtered = filtered[filtered["time_step"] >= start]

    st.markdown("### KPI plots")

    chart1, chart2 = st.columns(2)
    with chart1:
        st.markdown('<div class="chart-card"><b>Reliability score over time</b>', unsafe_allow_html=True)
        st.line_chart(chart_line_data(filtered, "reliability_score"))
        st.markdown("</div>", unsafe_allow_html=True)

    with chart2:
        st.markdown('<div class="chart-card"><b>Latency over time</b>', unsafe_allow_html=True)
        st.line_chart(chart_line_data(filtered, "latency_ms"))
        st.markdown("</div>", unsafe_allow_html=True)

    chart3, chart4 = st.columns(2)
    with chart3:
        st.markdown('<div class="chart-card"><b>Packet loss over time</b>', unsafe_allow_html=True)
        st.line_chart(chart_line_data(filtered, "packet_loss_pct"))
        st.markdown("</div>", unsafe_allow_html=True)

    with chart4:
        st.markdown('<div class="chart-card"><b>Availability over time</b>', unsafe_allow_html=True)
        st.line_chart(chart_line_data(filtered, "availability"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Recent KPI summary")
    latest = format_latest_table(decision["latest_table"])
    st.dataframe(latest, hide_index=True)

    st.markdown(
        f"""
<div class="decision-box">
  <div class="decision-title">Trace summary</div>
  <div class="decision-headline">{decision['best_average_link']} has the strongest average reliability in this run.</div>
  <p>It achieved an average synthetic reliability score of {decision['best_average_score']:.1f}/100 across the trace.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "Export results CSV",
        data=filtered.to_csv(index=False),
        file_name="sdv_multilink_filtered_results.csv",
        mime="text/csv",
    )


def render_about_and_help() -> None:
    page_header(
        "About and Help",
        "Purpose, workflow, interpretation, limitations, and usage guidance for this project.",
    )

    st.markdown(
        """
<div class="hero-note">
  <b>SDV Multi-Link Reliability Lab</b> is a research-oriented synthetic reliability demo for software-defined vehicle multi-link connectivity.
  It is not a real ITS-G5/5G/6G simulator and does not use live network data.
</div>
        """,
        unsafe_allow_html=True,
    )

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown(
            """
<div class="info-card">
<h3>What this project does</h3>
<p>This tool generates synthetic link performance data for ITS-G5, 5G, and 6G candidate links. It evaluates reliability under configurable network conditions.</p>
<hr/>
<ul>
<li>Simulates link behaviour over time</li>
<li>Applies packet-loss and signal-quality models</li>
<li>Calculates a transparent reliability score</li>
<li>Recommends the strongest available link</li>
</ul>
</div>
            """,
            unsafe_allow_html=True,
        )

    with row1_col2:
        st.markdown(
            """
<div class="info-card">
<h3>How to use the dashboard</h3>
<ol>
<li><b>Configure scenario:</b> choose scenario type, affected link, time steps, and random seed.</li>
<li><b>Run reliability analysis:</b> press the blue button in the sidebar. Values do not update until this button is pressed.</li>
<li><b>Review selected link:</b> check the selected primary link, latest score, rejected links, and warning conditions.</li>
<li><b>Inspect graphs:</b> open Graphs and Results for KPI trends and tables.</li>
<li><b>Download outputs:</b> export the Markdown report or scored CSV.</li>
</ol>
</div>
            """,
            unsafe_allow_html=True,
        )

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown(
            """
<div class="info-card">
<h3>How to read the reliability score</h3>
<p>The reliability score ranges from 0 to 100 and indicates the link's relative suitability for selection in this synthetic scenario.</p>
<hr/>
<ul>
<li>Higher scores mean better expected reliability inside this demo.</li>
<li>The score uses latency, jitter, packet loss, throughput, signal quality, and availability.</li>
<li>Hard-fail conditions can reject a link regardless of score.</li>
<li>Use the score for comparison, not as a real-world safety guarantee.</li>
</ul>
</div>
            """,
            unsafe_allow_html=True,
        )

    with row2_col2:
        st.markdown(
            """
<div class="info-card">
<h3>Important limitations</h3>
<p>This is a synthetic research demo with known assumptions and boundaries.</p>
<hr/>
<ul>
<li>All data is synthetic, not live measurement data.</li>
<li>Models use transparent rules and visible parameters.</li>
<li>Results depend on scenario choices and random seed.</li>
<li>Outputs must not be interpreted as vehicle safety guarantees.</li>
</ul>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### CSV upload guide")
    st.markdown(
        """
A CSV file can be uploaded from the sidebar when you want to test your own synthetic scenario instead of using the built-in generator.

Required columns:

`time_step`, `link`, `latency_ms`, `jitter_ms`, `packet_loss_pct`, `throughput_mbps`, `signal_quality`, `availability`

After uploading the file, press **Run reliability analysis**. The app validates the required columns before scoring the uploaded data.
        """
    )

    st.markdown("### FAQ")
    faq1, faq2, faq3 = st.columns(3)
    with faq1:
        st.info("Why do results change? The synthetic generator uses randomized noise controlled by the random seed.")
    with faq2:
        st.info("Can this guide real deployment decisions? No. It is a portfolio and research-demonstration tool only.")
    with faq3:
        st.info("What should I explain in an interview? Explain the KPI model, hard-fail rules, failover logic, and limitations.")


if active_page == "Decision Dashboard":
    render_decision_dashboard()
elif active_page == "Graphs and Results":
    render_graphs_and_results()
else:
    render_about_and_help()
