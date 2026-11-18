from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import Alert
from priority_score import calculate_priority_score


@pytest.fixture
def test_context() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app), session_factory
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def test_alert_priority_matches_calculated_score(
    test_context: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_context
    with session_factory() as db:
        alert = Alert(severity="warning", metric_value=150.0, threshold=100.0)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        alert_id = alert.id
        expected_score = calculate_priority_score(
            alert.severity,
            alert.metric_value,
            alert.threshold,
        )

    response = client.get(f"/alerts/{alert_id}/priority")

    assert response.status_code == 200
    assert response.json() == {
        "alert_id": alert_id,
        "priority_score": expected_score,
    }


def test_nonexistent_alert_returns_404(
    test_context: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = test_context

    response = client.get("/alerts/999/priority")

    assert response.status_code == 404


# --- Edge case added manually ---
def test_zero_threshold_alert_returns_422(test_context):
    client, session_factory = test_context
    with session_factory() as db:
        alert = Alert(severity="warning", metric_value=50, threshold=0)
        db.add(alert)
        db.commit()
        alert_id = alert.id
    response = client.get(f"/alerts/{alert_id}/priority")
    assert response.status_code == 422
    assert "threshold must not be zero" in response.json()["detail"]