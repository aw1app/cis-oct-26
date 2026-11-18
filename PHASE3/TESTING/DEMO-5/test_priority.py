import pytest

from priority_score import calculate_priority_score


@pytest.mark.parametrize(
    ("severity", "metric_value", "threshold", "expected_score"),
    [
        ("critical", 150.0, 100.0, 80),
        ("warning", 150.0, 100.0, 50),
        ("info", 150.0, 100.0, 30),
    ],
)
def test_calculate_priority_score_above_threshold_returns_int(
    severity: str,
    metric_value: float,
    threshold: float,
    expected_score: int,
) -> None:
    score = calculate_priority_score(severity, metric_value, threshold)

    assert isinstance(score, int)
    assert score == expected_score



# --- Edge cases added manually ---
def test_unknown_severity_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported severity"):
        calculate_priority_score("emergency", 100, 90)


def test_zero_threshold_raises_value_error():
    with pytest.raises(ValueError, match="threshold must not be zero"):
        calculate_priority_score("critical", 50, 0)


def test_metric_below_threshold_gets_no_bonus():
    assert calculate_priority_score("warning", -20, 10) == 30


def test_metric_equal_to_threshold_gets_no_bonus():
    assert calculate_priority_score("critical", 100, 100) == 60


def test_bonus_is_capped_at_forty_points():
    assert calculate_priority_score("critical", 1000, 100) == 100
