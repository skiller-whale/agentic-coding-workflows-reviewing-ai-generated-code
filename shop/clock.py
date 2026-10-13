from datetime import UTC, datetime
from zoneinfo import ZoneInfo

SHOP_TIMEZONE = ZoneInfo("Europe/London")


def now() -> datetime:
    """The current time, in UTC. Tests freeze this."""
    return datetime.now(UTC)
