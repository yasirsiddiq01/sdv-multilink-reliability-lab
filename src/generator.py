from __future__ import annotations

import numpy as np
import pandas as pd

from .config import LINK_PROFILES


def _affected_multiplier(link: str, affected_link: str) -> float:
    if affected_link == "All links":
        return 1.0
    return 1.0 if link == affected_link else 0.20


def _apply_scenario(row: dict, scenario: str, intensity: float) -> dict:
    if scenario == "normal":
        return row

    if scenario == "congestion":
        row["latency_ms"] += 32 * intensity
        row["jitter_ms"] += 11 * intensity
        row["throughput_mbps"] *= max(0.2, 1 - 0.48 * intensity)
        row["packet_loss_pct"] += 3.5 * intensity

    elif scenario == "poor_signal":
        row["signal_quality"] -= 36 * intensity
        row["packet_loss_pct"] += 5.0 * intensity
        row["availability"] -= 0.075 * intensity
        row["throughput_mbps"] *= max(0.15, 1 - 0.35 * intensity)

    elif scenario == "high_mobility":
        row["latency_ms"] += 18 * intensity
        row["jitter_ms"] += 9 * intensity
        row["signal_quality"] -= 18 * intensity
        row["packet_loss_pct"] += 3.0 * intensity
        row["availability"] -= 0.04 * intensity

    elif scenario == "packet_loss_spike":
        row["packet_loss_pct"] += 15.0 * intensity
        row["jitter_ms"] += 5.5 * intensity
        row["availability"] -= 0.05 * intensity

    elif scenario == "link_outage":
        row["latency_ms"] += 95 * intensity
        row["jitter_ms"] += 35 * intensity
        row["packet_loss_pct"] += 42 * intensity
        row["throughput_mbps"] *= max(0.02, 1 - 0.92 * intensity)
        row["signal_quality"] -= 55 * intensity
        row["availability"] -= 0.42 * intensity

    row["latency_ms"] = float(max(0.1, row["latency_ms"]))
    row["jitter_ms"] = float(max(0.0, row["jitter_ms"]))
    row["packet_loss_pct"] = float(np.clip(row["packet_loss_pct"], 0, 100))
    row["throughput_mbps"] = float(max(0.0, row["throughput_mbps"]))
    row["signal_quality"] = float(np.clip(row["signal_quality"], 0, 100))
    row["availability"] = float(np.clip(row["availability"], 0, 1))
    return row


def generate_scenario(
    scenario: str = "normal",
    affected_link: str = "All links",
    time_steps: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic multi-link vehicle connectivity KPI traces.

    This is intentionally synthetic. It is designed for explainable reliability
    selection logic, not for replacing a real network simulator.
    """
    if time_steps < 5:
        raise ValueError("time_steps must be at least 5")

    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    for t in range(time_steps):
        progress = t / max(1, time_steps - 1)
        scenario_active = progress >= 0.50
        ramp = min(1.0, max(0.0, (progress - 0.50) / 0.25)) if scenario_active else 0.0

        for link, profile in LINK_PROFILES.items():
            # Small deterministic trend plus random jitter.
            mobility_wave = 1.0 + 0.08 * np.sin(2 * np.pi * progress + len(link))
            row = {
                "time_step": t,
                "link": link,
                "latency_ms": profile.latency_ms * mobility_wave + rng.normal(0, profile.latency_ms * 0.06),
                "jitter_ms": profile.jitter_ms + rng.normal(0, max(0.2, profile.jitter_ms * 0.12)),
                "packet_loss_pct": profile.packet_loss_pct + rng.normal(0, 0.22),
                "throughput_mbps": profile.throughput_mbps * (1 + rng.normal(0, 0.055)),
                "signal_quality": profile.signal_quality + rng.normal(0, 2.5),
                "availability": profile.availability + rng.normal(0, 0.004),
                "scenario": scenario,
                "affected_link": affected_link,
            }

            if scenario_active:
                link_multiplier = _affected_multiplier(link, affected_link)
                temporal_intensity = ramp * link_multiplier
                row = _apply_scenario(row, scenario, temporal_intensity)

            row["latency_ms"] = round(float(max(0.1, row["latency_ms"])), 2)
            row["jitter_ms"] = round(float(max(0.0, row["jitter_ms"])), 2)
            row["packet_loss_pct"] = round(float(np.clip(row["packet_loss_pct"], 0, 100)), 2)
            row["throughput_mbps"] = round(float(max(0.0, row["throughput_mbps"])), 2)
            row["signal_quality"] = round(float(np.clip(row["signal_quality"], 0, 100)), 2)
            row["availability"] = round(float(np.clip(row["availability"], 0, 1)), 4)
            rows.append(row)

    return pd.DataFrame(rows)


def validate_uploaded_scenario(df: pd.DataFrame) -> tuple[bool, list[str]]:
    from .config import REQUIRED_COLUMNS

    issues = []
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        issues.append(f"Missing required columns: {', '.join(sorted(missing))}")

    if "availability" in df.columns and not df["availability"].between(0, 1).all():
        issues.append("availability must be between 0 and 1.")

    if "packet_loss_pct" in df.columns and not df["packet_loss_pct"].between(0, 100).all():
        issues.append("packet_loss_pct must be between 0 and 100.")

    if "link" in df.columns and df["link"].nunique() < 2:
        issues.append("CSV should contain at least two links for multi-link comparison.")

    return len(issues) == 0, issues
