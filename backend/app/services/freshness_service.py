from datetime import datetime, timezone


class FreshnessService:
    """
    Determines how fresh a document version is based on
    when it was retrieved.
    """

    def __init__(
        self,
        fresh_days: int = 30,
        stale_days: int = 90,
    ):
        if fresh_days < 0:
            raise ValueError("fresh_days must be non-negative")

        if stale_days < fresh_days:
            raise ValueError(
                "stale_days must be greater than or equal to fresh_days"
            )

        self.fresh_days = fresh_days
        self.stale_days = stale_days

    def get_status(
        self,
        retrieved_at: datetime | None,
    ) -> str:
        """
        Return freshness status based on retrieval time.

        Possible values:
        - fresh
        - aging
        - stale
        - unknown
        """

        if retrieved_at is None:
            return "unknown"

        if retrieved_at.tzinfo is None:
            retrieved_at = retrieved_at.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        age_days = (
            now - retrieved_at
        ).total_seconds() / 86400

        if age_days < 0:
            return "fresh"

        if age_days <= self.fresh_days:
            return "fresh"

        if age_days <= self.stale_days:
            return "aging"

        return "stale"

    def get_age_days(
        self,
        retrieved_at: datetime | None,
    ) -> float | None:
        """
        Return the age of the source in days.
        """

        if retrieved_at is None:
            return None

        if retrieved_at.tzinfo is None:
            retrieved_at = retrieved_at.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        age_days = (
            now - retrieved_at
        ).total_seconds() / 86400

        return max(age_days, 0.0)