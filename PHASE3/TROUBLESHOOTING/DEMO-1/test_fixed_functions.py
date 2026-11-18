from buggy_functions import (
    average_response_time,
    format_alert_summary,
    get_alert_owner,
)


def test_format_alert_summary_with_integer_count():
    assert format_alert_summary(3, "critical") == "There are 3 critical alerts active."


def test_get_alert_owner_with_missing_team():
    alert = {"owner": "network-team"}
    team_directory = {"support-team": "Support Operations"}

    assert get_alert_owner(alert, team_directory) == "Unassigned"


def test_get_alert_owner_with_existing_team():
    alert = {"owner": "network-team"}
    team_directory = {"network-team": "Network Operations"}

    assert get_alert_owner(alert, team_directory) == "Network Operations"


def test_average_response_time_with_empty_list():
    result = average_response_time([])

    assert isinstance(result, float)
    assert result == 0.0


def test_average_response_time_with_nonempty_list():
    assert average_response_time([1, 2]) == 1.5