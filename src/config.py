from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LinkProfile:
    name: str
    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    throughput_mbps: float
    signal_quality: float
    availability: float


LINK_PROFILES: dict[str, LinkProfile] = {
    "ITS-G5": LinkProfile(
        name="ITS-G5",
        latency_ms=16.0,
        jitter_ms=4.0,
        packet_loss_pct=1.8,
        throughput_mbps=28.0,
        signal_quality=74.0,
        availability=0.965,
    ),
    "5G": LinkProfile(
        name="5G",
        latency_ms=24.0,
        jitter_ms=6.0,
        packet_loss_pct=0.9,
        throughput_mbps=85.0,
        signal_quality=79.0,
        availability=0.982,
    ),
    "6G Candidate": LinkProfile(
        name="6G Candidate",
        latency_ms=9.0,
        jitter_ms=2.5,
        packet_loss_pct=0.35,
        throughput_mbps=155.0,
        signal_quality=91.0,
        availability=0.995,
    ),
}

SCENARIO_LABELS = {
    "normal": "Nominal Operation",
    "congestion": "Congestion",
    "poor_signal": "Poor Signal",
    "high_mobility": "High Mobility",
    "packet_loss_spike": "Packet Loss Spike",
    "link_outage": "Link Outage",
}

SCENARIO_OPTIONS = list(SCENARIO_LABELS.keys())

AFFECTED_LINK_OPTIONS = ["All links", "ITS-G5", "5G", "6G Candidate"]

REQUIRED_COLUMNS = {
    "time_step",
    "link",
    "latency_ms",
    "jitter_ms",
    "packet_loss_pct",
    "throughput_mbps",
    "signal_quality",
    "availability",
}

HARD_FAIL_RULES = {
    "latency_ms": 120.0,
    "packet_loss_pct": 25.0,
    "availability": 0.70,
    "signal_quality": 20.0,
    "throughput_mbps": 1.0,
}

WARNING_RULES = {
    "packet_loss_pct": 10.0,
    "signal_quality": 45.0,
    "availability": 0.90,
}
