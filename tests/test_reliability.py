from src.generator import generate_scenario
from src.reliability import (
    apply_scoring,
    decision_paragraph,
    is_hard_fail,
    reliability_score,
    select_best_link,
)


def test_reliability_score_range():
    df = generate_scenario(time_steps=10)
    score = reliability_score(df.iloc[0])
    assert 0 <= score <= 100


def test_apply_scoring_adds_columns():
    df = generate_scenario(time_steps=10)
    scored = apply_scoring(df)
    assert "reliability_score" in scored.columns
    assert "hard_fail" in scored.columns
    assert "status" in scored.columns


def test_best_link_selection_contains_fields():
    df = generate_scenario(time_steps=20, seed=10)
    scored = apply_scoring(df)
    decision = select_best_link(scored)
    assert decision["selected_link"] in {"ITS-G5", "5G", "6G Candidate"}
    assert isinstance(decision["rejected_links"], list)
    assert "best_average_link" in decision


def test_link_outage_can_create_hard_fail():
    df = generate_scenario("link_outage", affected_link="ITS-G5", time_steps=100, seed=2)
    scored = apply_scoring(df)
    its_latest = scored[(scored["time_step"] == scored["time_step"].max()) & (scored["link"] == "ITS-G5")].iloc[0]
    assert is_hard_fail(its_latest) is True


def test_decision_paragraph_uses_requested_style():
    df = generate_scenario(time_steps=20, seed=42)
    decision = select_best_link(apply_scoring(df))
    text = decision_paragraph(decision)
    assert "was selected because it offers the highest current reliability score" in text
    assert "while still staying within hard-fail limits" in text
    assert "At the most recent time step" in text
    assert "Over the entire trace" in text
