from uuid import uuid4
from datetime import datetime, timezone
from calendar import timegm
from django.conf import settings


def generate_id() -> str:
    return f"{uuid4().time}"


def make_utc(dt: datetime) -> datetime:
    if settings.USE_TZ and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def aware_utcnow() -> datetime:
    dt = datetime.now(tz=timezone.utc)
    if not settings.USE_TZ:
        dt = dt.replace(tzinfo=None)

    return dt


def datetime_to_epoch(dt: datetime) -> int:
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts: float) -> datetime:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if not settings.USE_TZ:
        dt = dt.replace(tzinfo=None)

    return dt
