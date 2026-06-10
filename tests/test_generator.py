import pandas as pd

from src.generator import generate_scenario, validate_uploaded_scenario
from src.config import REQUIRED_COLUMNS


def test_generate_scenario_shape():
    df = generate_scenario(time_steps=20, seed=1)
    assert len(df) == 60
    assert REQUIRED_COLUMNS.issubset(df.columns)


def test_generate_scenario_links():
    df = generate_scenario(time_steps=10)
    assert set(df["link"]) == {"ITS-G5", "5G", "6G Candidate"}


def test_packet_loss_spike_increases_loss():
    normal = generate_scenario("normal", time_steps=80, seed=4)
    spike = generate_scenario("packet_loss_spike", affected_link="All links", time_steps=80, seed=4)
    assert spike["packet_loss_pct"].mean() > normal["packet_loss_pct"].mean()


def test_validate_uploaded_scenario_accepts_valid_data():
    df = generate_scenario(time_steps=10)
    valid, issues = validate_uploaded_scenario(df)
    assert valid is True
    assert issues == []


def test_validate_uploaded_scenario_rejects_missing_columns():
    df = pd.DataFrame({"time_step": [0], "link": ["5G"]})
    valid, issues = validate_uploaded_scenario(df)
    assert valid is False
    assert issues
