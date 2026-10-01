from datetime import datetime, timedelta, timezone

import pytest

from app.services.freshness_service import FreshnessService


def test_recent_document_is_fresh():
    service = FreshnessService()

    retrieved_at = datetime.now(timezone.utc) - timedelta(days=10)

    assert service.get_status(retrieved_at) == "fresh"


def test_document_between_30_and_90_days_is_aging():
    service = FreshnessService()

    retrieved_at = datetime.now(timezone.utc) - timedelta(days=60)

    assert service.get_status(retrieved_at) == "aging"


def test_old_document_is_stale():
    service = FreshnessService()

    retrieved_at = datetime.now(timezone.utc) - timedelta(days=120)

    assert service.get_status(retrieved_at) == "stale"


def test_missing_retrieval_date_is_unknown():
    service = FreshnessService()

    assert service.get_status(None) == "unknown"


def test_naive_datetime_is_supported():
    service = FreshnessService()

    retrieved_at = datetime.utcnow() - timedelta(days=10)

    assert service.get_status(retrieved_at) == "fresh"


def test_age_days_returns_document_age():
    service = FreshnessService()

    retrieved_at = datetime.now(timezone.utc) - timedelta(days=10)

    age = service.get_age_days(retrieved_at)

    assert age is not None
    assert 9.9 <= age <= 10.1


def test_age_days_returns_none_for_missing_date():
    service = FreshnessService()

    assert service.get_age_days(None) is None


def test_invalid_thresholds_are_rejected():
    with pytest.raises(ValueError):
        FreshnessService(
            fresh_days=90,
            stale_days=30,
        )