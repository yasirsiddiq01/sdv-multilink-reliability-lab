from __future__ import annotations

import pandas as pd

from .config import HARD_FAIL_RULES, WARNING_RULES


def reliability_score(row: pd.Series) -> float:
    """Calculate a transparent synthetic reliability index from 0 to 100."""
    latency_score = max(0.0, 100.0 - (float(row["latency_ms"]) / 120.0) * 100.0)
    jitter_score = max(0.0, 100.0 - (float(row["jitter_ms"]) / 50.0) * 100.0)
    loss_score = max(0.0, 100.0 - (float(row["packet_loss_pct"]) / 25.0) * 100.0)
    throughput_score = min(100.0, (float(row["throughput_mbps"]) / 160.0) * 100.0)
    signal_score = max(0.0, min(100.0, float(row["signal_quality"])))
    availability_score = max(0.0, min(100.0, float(row["availability"]) * 100.0))

    score = (
        0.23 * loss_score
        + 0.20 * availability_score
        + 0.18 * latency_score
        + 0.14 * jitter_score
        + 0.15 * signal_score
        + 0.10 * throughput_score
    )
    return round(max(0.0, min(100.0, score)), 1)


def apply_scoring(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["reliability_score"] = out.apply(reliability_score, axis=1)
    out["hard_fail"] = out.apply(is_hard_fail, axis=1)
    out["status"] = out.apply(classify_status, axis=1)
    return out


def is_hard_fail(row: pd.Series) -> bool:
    return bool(
        row["latency_ms"] > HARD_FAIL_RULES["latency_ms"]
        or row["packet_loss_pct"] > HARD_FAIL_RULES["packet_loss_pct"]
        or row["availability"] < HARD_FAIL_RULES["availability"]
        or row["signal_quality"] < HARD_FAIL_RULES["signal_quality"]
        or row["throughput_mbps"] < HARD_FAIL_RULES["throughput_mbps"]
    )


def classify_status(row: pd.Series) -> str:
    if is_hard_fail(row):
        return "Hard fail"
    score = reliability_score(row)
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Monitor"
    return "Degraded"


def select_best_link(scored_df: pd.DataFrame) -> dict:
    latest_time = scored_df["time_step"].max()
    latest = scored_df[scored_df["time_step"] == latest_time].copy()

    eligible = latest[~latest["hard_fail"]].sort_values("reliability_score", ascending=False)
    if not eligible.empty:
        selected = eligible.iloc[0]
    else:
        selected = latest.sort_values("reliability_score", ascending=False).iloc[0]

    rejected = [link for link in latest["link"].tolist() if link != selected["link"]]
    mean_scores = (
        scored_df.groupby("link", as_index=False)["reliability_score"]
        .mean()
        .sort_values("reliability_score", ascending=False)
    )
    best_average = mean_scores.iloc[0]

    selected_over_time = (
        scored_df.sort_values(["time_step", "reliability_score"], ascending=[True, False])
        .query("hard_fail == False")
        .groupby("time_step")
        .first()
        .reset_index()
    )
    if selected_over_time.empty:
        failover_events = 0
    else:
        failover_events = int((selected_over_time["link"] != selected_over_time["link"].shift()).sum() - 1)
        failover_events = max(0, failover_events)

    warnings = warning_messages(scored_df)

    return {
        "latest_time": int(latest_time),
        "selected_link": str(selected["link"]),
        "selected_score": float(selected["reliability_score"]),
        "selected_latency_ms": float(selected["latency_ms"]),
        "selected_packet_loss_pct": float(selected["packet_loss_pct"]),
        "selected_availability": float(selected["availability"]),
        "selected_status": str(selected["status"]),
        "rejected_links": rejected,
        "best_average_link": str(best_average["link"]),
        "best_average_score": round(float(best_average["reliability_score"]), 1),
        "failover_events": int(failover_events),
        "warnings": warnings,
        "latest_table": latest.sort_values("reliability_score", ascending=False),
    }


def warning_messages(scored_df: pd.DataFrame) -> list[str]:
    messages: list[str] = []
    if (scored_df["packet_loss_pct"] > WARNING_RULES["packet_loss_pct"]).any():
        messages.append("at least one link or time step experienced packet loss exceeding 10%")
    if (scored_df["signal_quality"] < WARNING_RULES["signal_quality"]).any():
        messages.append("signal quality dropped below 45/100 in at least one link or time step")
    if (scored_df["availability"] < WARNING_RULES["availability"]).any():
        messages.append("availability dropped below 0.900 in at least one link or time step")
    return messages


def decision_headline(decision: dict) -> str:
    score = decision["selected_score"]
    if decision["selected_status"] == "Hard fail":
        return "No link is fully reliable under the current hard-fail rules."
    if score >= 90:
        return "The selected link is currently reliable."
    if score >= 75:
        return "The selected link is usable, but it should be monitored."
    if score >= 60:
        return "The selected link is marginal and should be treated with caution."
    return "The selected link is degraded; fallback or mitigation should be investigated."


def decision_paragraph(decision: dict) -> str:
    rejected_text = ", ".join(decision["rejected_links"]) if decision["rejected_links"] else "none"

    if decision["failover_events"] == 0:
        failover_sentence = "No failover events were observed."
    elif decision["failover_events"] == 1:
        failover_sentence = "One failover event was observed."
    else:
        failover_sentence = f"{decision['failover_events']} failover events were observed."

    warning_count = len(decision["warnings"])
    if warning_count == 0:
        warning_sentence = "No warning conditions were detected in the trace."
    elif warning_count == 1:
        warning_sentence = f"However, there is one warning: {decision['warnings'][0]}."
    else:
        joined = ", and ".join(decision["warnings"])
        warning_sentence = f"However, there are {warning_count} warnings: {joined}."

    return (
        f"The {decision['selected_link']} was selected because it offers the highest current reliability "
        f"score ({decision['selected_score']:.1f}/100) while still staying within hard-fail limits. "
        f"Its current latency is {decision['selected_latency_ms']:.1f} ms, packet loss is "
        f"{decision['selected_packet_loss_pct']:.1f}%, and availability is "
        f"{decision['selected_availability']:.3f}. At the most recent time step, {rejected_text} "
        f"were rejected. Over the entire trace, the {decision['best_average_link']} also has the best "
        f"average reliability at {decision['best_average_score']:.1f}/100. {failover_sentence} "
        f"{warning_sentence}"
    )


def warning_bullets(decision: dict) -> list[str]:
    if not decision["warnings"]:
        return ["No warning or hard-fail condition was detected in this synthetic trace."]
    return [message[0].upper() + message[1:] + "." for message in decision["warnings"]]
