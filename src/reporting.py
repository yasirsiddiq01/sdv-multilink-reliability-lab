from __future__ import annotations

import pandas as pd

from .reliability import decision_headline, decision_paragraph, warning_bullets


def build_markdown_report(
    decision: dict,
    scored_df: pd.DataFrame,
    scenario_label: str,
    affected_link: str,
    time_steps: int,
    seed: int,
) -> str:
    latest = decision["latest_table"][
        [
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
    ].copy()

    table_md = latest.to_markdown(index=False)
    warnings = "\n".join(f"- {item}" for item in warning_bullets(decision))

    return f"""# SDV Multi-Link Reliability Lab Report

## Project scope

This is a research-oriented synthetic reliability demo for software-defined vehicle multi-link connectivity. It is not a real SDV, ITS-G5, 5G, 6G, ns-3, OMNeT++, SUMO, or vendor-grade simulator.

## Scenario configuration

- Scenario: {scenario_label}
- Affected link: {affected_link}
- Time steps: {time_steps}
- Random seed: {seed}

## Reliability decision

**{decision_headline(decision)}**

{decision_paragraph(decision)}

## Warning and fail conditions

{warnings}

## Latest KPI table

{table_md}

## Interpretation note

The reliability score is a transparent synthetic index used for relative link selection inside this demo. It should not be interpreted as a safety guarantee or as real deployment performance.
"""
